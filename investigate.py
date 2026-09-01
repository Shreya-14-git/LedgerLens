import pandas as pd

# ==========================================
# LOAD RECONCILIATION RESULTS
# ==========================================

results = pd.read_csv(
    "data/reconciliation_results.csv"
)


# ==========================================
# SHOW AVAILABLE EXCEPTIONS
# ==========================================

exceptions = results[
    results["reconciliation_status"] != "Matched"
]

print("\n================================")
print("      LEDGERLENS EXCEPTIONS")
print("================================")

print(
    exceptions[
        [
            "order_id",
            "amount_order",
            "reconciliation_status"
        ]
    ].to_string(index=False)
)


# ==========================================
# ASK USER FOR ORDER ID
# ==========================================

order_id = input(
    "\nEnter an Order ID to investigate: "
).strip()


# ==========================================
# FIND TRANSACTION
# ==========================================

transaction = results[
    results["order_id"] == order_id
]


if transaction.empty:

    print("\n❌ Order not found.")

else:

    row = transaction.iloc[0]

    print("\n================================")
    print("      TRANSACTION DETAILS")
    print("================================")

    print(f"Order ID          : {row['order_id']}")

    print(
        f"Order amount      : ₹{row['amount_order']:,.2f}"
    )

    if pd.isna(row["payment_id"]):

        print("Payment           : ❌ Missing")

    else:

        print(
            f"Payment ID        : {row['payment_id']}"
        )

        print(
            f"Payment amount    : ₹{row['amount_payment']:,.2f}"
        )

        print(
            f"Payment status    : {row['status']}"
        )

    if pd.isna(row["settlement_id"]):

        print("Settlement        : ❌ Missing")

    else:

        print(
            f"Settlement ID     : {row['settlement_id']}"
        )

        print(
            f"Settlement amount : ₹{row['amount']:,.2f}"
        )


    print(
        f"\nStatus            : {row['reconciliation_status']}"
    )


    # ==========================================
    # CALCULATE DIFFERENCE
    # ==========================================

    if (
        not pd.isna(row["amount_payment"])
        and not pd.isna(row["amount"])
    ):

        difference = (
            row["amount_payment"]
            - row["amount"]
        )

        print(
            f"Difference        : ₹{difference:,.2f}"
        )


    # ==========================================
    # RECOMMEND ACTION
    # ==========================================

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


    print(
        f"\nRecommended action:\n{recommendation}"
    )