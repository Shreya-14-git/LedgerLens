import pandas as pd

# ==========================================
# 1. LOAD DATA
# ==========================================

orders = pd.read_csv("data/orders.csv")
payments = pd.read_csv("data/payments.csv")
settlements = pd.read_csv("data/settlements.csv")

print("Data loaded successfully!")
print(f"Orders: {len(orders)}")
print(f"Payments: {len(payments)}")
print(f"Settlements: {len(settlements)}")


# ==========================================
# 2. CHECK FOR DUPLICATE PAYMENTS
# ==========================================

payment_counts = payments.groupby("order_id").size()

duplicate_orders = set(
    payment_counts[payment_counts > 1].index
)


# ==========================================
# 3. KEEP ONE PAYMENT PER ORDER
# ==========================================

# For reconciliation we use the first payment.
# Duplicate payments are separately flagged.
payments_unique = payments.drop_duplicates(
    subset="order_id",
    keep="first"
)


# ==========================================
# 4. MATCH ORDERS WITH PAYMENTS
# ==========================================

result = orders.merge(
    payments_unique,
    on="order_id",
    how="left",
    suffixes=("_order", "_payment")
)


# ==========================================
# 5. MATCH PAYMENTS WITH SETTLEMENTS
# ==========================================

result = result.merge(
    settlements,
    on="order_id",
    how="left",
    suffixes=("", "_settlement")
)


# ==========================================
# 6. CHECK EACH TRANSACTION
# ==========================================

def check_transaction(row):

    order_id = row["order_id"]

    # Duplicate payment
    if order_id in duplicate_orders:
        return "Duplicate Payment"

    # Missing payment
    if pd.isna(row["payment_id"]):
        return "Missing Payment"

    # Payment failed
    if row["status"] != "success":
        return "Payment Failed"

    # Missing settlement
    if pd.isna(row["settlement_id"]):
        return "Missing Settlement"

    # Settlement mismatch
    if row["amount_payment"] != row["amount"]:
        return "Settlement Mismatch"

    # Everything matches
    return "Matched"


result["reconciliation_status"] = result.apply(
    check_transaction,
    axis=1
)


# ==========================================
# 7. CALCULATE METRICS
# ==========================================

total_orders = len(orders)

matched = (
    result["reconciliation_status"] == "Matched"
).sum()

exceptions = total_orders - matched

match_rate = (
    matched / total_orders
) * 100


# ==========================================
# 8. DISPLAY REPORT
# ==========================================

print("\n================================")
print("      LEDGERLENS REPORT")
print("================================")

print(f"Orders processed : {total_orders}")
print(f"Matched          : {matched}")
print(f"Exceptions       : {exceptions}")
print(f"Match rate       : {match_rate:.2f}%")

print("\nException breakdown:")

print(
    result["reconciliation_status"]
    .value_counts()
)


# ==========================================
# 9. SAVE RESULTS
# ==========================================

result.to_csv(
    "data/reconciliation_results.csv",
    index=False
)

print("\n✅ Reconciliation completed!")
print("📄 Results saved to:")
print("data/reconciliation_results.csv")