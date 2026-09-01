import pandas as pd
import random
from datetime import datetime, timedelta
import os

# -----------------------------
# SETTINGS
# -----------------------------

NUM_TRANSACTIONS = 250

random.seed(42)

# Create data folder
os.makedirs("data", exist_ok=True)

# -----------------------------
# GENERATE ORDERS
# -----------------------------

orders = []

start_date = datetime(2026, 8, 1)

for i in range(1, NUM_TRANSACTIONS + 1):

    order_id = f"ORD{i:04d}"
    customer_id = f"CUST{random.randint(1, 100):03d}"

    amount = random.choice([
        299, 499, 799, 999, 1499,
        1999, 2499, 2999, 3999, 4999
    ])

    order_date = start_date + timedelta(
        days=random.randint(0, 20)
    )

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "order_date": order_date.strftime("%Y-%m-%d")
    })


# -----------------------------
# GENERATE PAYMENTS
# -----------------------------

payments = []

for order in orders:

    # 95% of orders have a payment
    if random.random() < 0.95:

        payment_id = f"PAY{len(payments) + 1:04d}"

        payments.append({
            "payment_id": payment_id,
            "order_id": order["order_id"],
            "amount": order["amount"],
            "status": "success",
            "payment_date": order["order_date"]
        })


# -----------------------------
# GENERATE SETTLEMENTS
# -----------------------------

settlements = []

for payment in payments:

    # 90% of successful payments get settled
    if random.random() < 0.90:

        settlement_id = f"SET{len(settlements) + 1:04d}"

        settlements.append({
            "settlement_id": settlement_id,
            "payment_id": payment["payment_id"],
            "order_id": payment["order_id"],
            "amount": payment["amount"],
            "settlement_date": payment["payment_date"]
        })


# -----------------------------
# INTRODUCE INTENTIONAL ERRORS
# -----------------------------

# 1. Amount mismatches
for settlement in random.sample(
    settlements,
    min(10, len(settlements))
):
    settlement["amount"] -= random.choice([50, 100, 200, 500])


# 2. Duplicate payments
duplicate_source = random.sample(
    payments,
    min(5, len(payments))
)

for payment in duplicate_source:

    duplicate = payment.copy()

    duplicate["payment_id"] = (
        f"PAY{len(payments) + 1:04d}"
    )

    payments.append(duplicate)


# -----------------------------
# SAVE CSV FILES
# -----------------------------

orders_df = pd.DataFrame(orders)
payments_df = pd.DataFrame(payments)
settlements_df = pd.DataFrame(settlements)

orders_df.to_csv(
    "data/orders.csv",
    index=False
)

payments_df.to_csv(
    "data/payments.csv",
    index=False
)

settlements_df.to_csv(
    "data/settlements.csv",
    index=False
)


# -----------------------------
# DISPLAY SUMMARY
# -----------------------------

print("\n✅ LedgerLens dataset created successfully!\n")

print(f"Orders:       {len(orders_df)}")
print(f"Payments:     {len(payments_df)}")
print(f"Settlements:  {len(settlements_df)}")

print("\nFiles created:")

print("📄 data/orders.csv")
print("📄 data/payments.csv")
print("📄 data/settlements.csv")