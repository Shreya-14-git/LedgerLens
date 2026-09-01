from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os
from datetime import datetime
from ai_analysis import analyze_transaction
app = FastAPI(title="LedgerLens API")
app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewTransaction(BaseModel):
    order_id: str
    order_amount: float
    payment_amount: float | None = None
    payment_status: str | None = None
    settlement_amount: float | None = None
    settlement_status: str | None = None

# Load reconciliation results
results = pd.read_csv(
    "data/reconciliation_results.csv"
)
NEW_TRANSACTIONS_FILE = "data/new_transactions.json"

try:
    with open(NEW_TRANSACTIONS_FILE, "r") as file:
        new_transactions = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    new_transactions = []


def save_new_transactions():
    os.makedirs("data", exist_ok=True)

    with open(NEW_TRANSACTIONS_FILE, "w") as file:
        json.dump(new_transactions, file, indent=4)

audit_events = []

@app.get("/")
def home():
    return {
        "message": "LedgerLens API is running!"
    }

@app.post("/transaction")
def add_transaction(transaction: NewTransaction):
        # Prevent duplicate Order IDs
    existing_order = results[
        results["order_id"] == transaction.order_id
    ]

    if not existing_order.empty:
        raise HTTPException(
            status_code=400,
            detail="Order ID already exists"
        )

    for item in new_transactions:
        if item["order_id"] == transaction.order_id:
            raise HTTPException(
                status_code=400,
                detail="Order ID already exists"
            )
    # Calculate difference
    difference = None

    if (
        transaction.payment_amount is not None
        and transaction.settlement_amount is not None
    ):
        difference = (
            transaction.payment_amount
            - transaction.settlement_amount
        )

    # Determine reconciliation status
    if transaction.payment_amount is None:
        status = "Missing Payment"

    elif transaction.settlement_amount is None:
        status = "Missing Settlement"

    elif difference != 0:
        status = "Settlement Mismatch"

    else:
        status = "Matched"

    # Recommended action
    if status == "Missing Payment":
        recommendation = (
            "Verify whether the customer payment "
            "was successfully received."
        )

    elif status == "Missing Settlement":
        recommendation = (
            "Check settlement status and "
            "expected settlement date."
        )

    elif status == "Settlement Mismatch":
        recommendation = (
            "Review settlement adjustment, "
            "fees or deductions."
        )

    else:
        recommendation = "No action required."

    # Prepare transaction data
    transaction_data = {
        "order_id": transaction.order_id,
        "order_amount": transaction.order_amount,

        "payment_id": None,
        "payment_amount": transaction.payment_amount,
        "payment_status": transaction.payment_status,

        "settlement_id": None,
        "settlement_amount": transaction.settlement_amount,

        "difference": difference,

        "status": status,
        "recommendation": recommendation
    }
        # AI investigation
    ai_analysis = analyze_transaction(transaction_data)

    transaction_data["ai_analysis"] = ai_analysis

    new_transactions.append(transaction_data)

    save_new_transactions()

    # Add event to audit trail
    audit_events.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": "New transaction added",
        "details": (
            f"Transaction {transaction.order_id} "
            f"was added and analyzed by AI"
        )
    })

    return transaction_data

@app.get("/check-order/{order_id}")
def check_order(order_id: str):

    existing_order = results[
        results["order_id"] == order_id
    ]

    if not existing_order.empty:
        return {
            "exists": True
        }

    for item in new_transactions:
        if item["order_id"] == order_id:
            return {
                "exists": True
            }

    return {
        "exists": False
    }

@app.get("/summary")
def summary():

    total = len(results) + len(new_transactions)

    matched = int(
        (results["reconciliation_status"] == "Matched").sum()
    )

    matched += sum(
        1
        for item in new_transactions
        if item["status"] == "Matched"
    )

    exceptions = total - matched

    match_rate = (
        (matched / total) * 100
        if total > 0
        else 0
    )

    return {
        "total_transactions": total,
        "matched": matched,
        "exceptions": exceptions,
        "match_rate": round(match_rate, 2)
    }

@app.get("/exceptions")
def get_exceptions():

    exceptions = results[
        results["reconciliation_status"] != "Matched"
    ]

    exception_list = []

    for _, row in exceptions.iterrows():
        exception_list.append({
            "order_id": row["order_id"],
            "amount": float(row["amount_order"]),
            "status": row["reconciliation_status"]
        })

    # Add newly created exceptions
    for item in new_transactions:
        if item["status"] != "Matched":
            exception_list.append({
                "order_id": item["order_id"],
                "amount": item["order_amount"],
                "status": item["status"]
            })

    return {
        "total_exceptions": len(exception_list),
        "exceptions": exception_list
    }

@app.get("/transaction/{order_id}")
def get_transaction(order_id: str):

    # Check newly added transactions first
    for item in new_transactions:
        if item["order_id"] == order_id:
            return item

    # Check existing CSV transactions
    transaction = results[
        results["order_id"] == order_id
    ]

    if transaction.empty:
        return {
            "error": "Transaction not found"
        }

    row = transaction.iloc[0]

    # Payment information
    payment_amount = None
    payment_status = None
    payment_id = None

    if not pd.isna(row["payment_id"]):
        payment_id = row["payment_id"]
        payment_amount = float(row["amount_payment"])
        payment_status = row["status"]

    # Settlement information
    settlement_amount = None
    settlement_id = None

    if not pd.isna(row["settlement_id"]):
        settlement_id = row["settlement_id"]
        settlement_amount = float(row["amount"])

    # Calculate difference
    difference = None

    if payment_amount is not None and settlement_amount is not None:
        difference = payment_amount - settlement_amount

    # Recommended action
    status = row["reconciliation_status"]

    if status == "Missing Payment":
        recommendation = (
            "Verify whether the customer payment "
            "was successfully received."
        )

    elif status == "Missing Settlement":
        recommendation = (
            "Check settlement status and "
            "expected settlement date."
        )

    elif status == "Settlement Mismatch":
        recommendation = (
            "Review settlement adjustment, "
            "fees or deductions."
        )

    elif status == "Duplicate Payment":
        recommendation = (
            "Verify whether the duplicate payment "
            "is legitimate and requires refund."
        )

    else:
        recommendation = "No action required."

    # Prepare transaction data
    transaction_data = {
        "order_id": row["order_id"],
        "order_amount": float(row["amount_order"]),

        "payment_id": payment_id,
        "payment_amount": payment_amount,
        "payment_status": payment_status,

        "settlement_id": settlement_id,
        "settlement_amount": settlement_amount,

        "difference": difference,

        "status": status,
        "recommendation": recommendation
    }

    # AI analysis
    ai_analysis = analyze_transaction(transaction_data)

    transaction_data["ai_analysis"] = ai_analysis

    return transaction_data



@app.get("/metrics")
def get_metrics():

    total = int(len(results) + len(new_transactions))

    matched = int(
        (results["reconciliation_status"] == "Matched").sum()
    )

    matched += sum(
        1
        for item in new_transactions
        if item["status"] == "Matched"
    )

    exceptions = int(total - matched)

    match_rate = round(
        (matched / total) * 100,
        2
    ) if total > 0 else 0.0

    # Existing CSV exceptions
    exception_data = results[
        results["reconciliation_status"] != "Matched"
    ]

    exception_breakdown = {
        str(key): int(value)
        for key, value in (
            exception_data["reconciliation_status"]
            .value_counts()
            .to_dict()
            .items()
        )
    }

    # Add newly created exceptions
    for item in new_transactions:
        if item["status"] != "Matched":
            exception_breakdown[item["status"]] = (
                exception_breakdown.get(item["status"], 0) + 1
            )

    # Existing exception value
    exception_value = float(
        exception_data["amount_order"].sum()
    )

    # Add new exception values
    exception_value += sum(
        float(item["order_amount"])
        for item in new_transactions
        if item["status"] != "Matched"
    )

    return {
        "records_processed": total,
        "matched": matched,
        "exceptions": exceptions,
        "match_rate": float(match_rate),
        "exception_value": float(exception_value),
        "exception_breakdown": exception_breakdown
    }

@app.get("/audit")
def get_audit():

    default_events = [
        {
            "time": "10:32:01",
            "event": "Reconciliation started",
            "details": "Processing financial records"
        },
        {
            "time": "10:32:01",
            "event": "Records processed",
            "details": f"{len(results)} records loaded"
        },
        {
            "time": "10:32:02",
            "event": "Transactions matched",
            "details": (
                f"{int((results['reconciliation_status'] == 'Matched').sum())} "
                "transactions successfully matched"
            )
        },
        {
            "time": "10:32:02",
            "event": "Exceptions detected",
            "details": (
                f"{int((results['reconciliation_status'] != 'Matched').sum())} "
                "transactions require investigation"
            )
        }
    ]

    return {
        "events": default_events + audit_events
    }