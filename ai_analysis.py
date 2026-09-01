def analyze_transaction(transaction):
    """
    Analyze a reconciled transaction and generate
    a finance-operations explanation.
    """

    status = transaction["status"]

    order_amount = transaction.get("order_amount")
    payment_amount = transaction.get("payment_amount")
    settlement_amount = transaction.get("settlement_amount")
    difference = transaction.get("difference")

    # Missing Payment
    if status == "Missing Payment":

        return {
            "summary": (
                "The order does not have a corresponding "
                "successful payment record."
            ),
            "likely_causes": [
                "Payment was not completed",
                "Payment record was not received",
                "Payment processing failure"
            ],
            "confidence": "HIGH",
            "recommended_action": (
                "Verify whether the customer payment was "
                "successfully received before taking further action."
            )
        }

    # Missing Settlement
    if status == "Missing Settlement":

        return {
            "summary": (
                "The payment exists, but no corresponding "
                "settlement record was found."
            ),
            "likely_causes": [
                "Settlement is still pending",
                "Settlement record is delayed",
                "Settlement processing issue"
            ],
            "confidence": "HIGH",
            "recommended_action": (
                "Check the expected settlement date and "
                "verify the settlement status."
            )
        }

    # Settlement mismatch
    if status == "Settlement Mismatch":

        difference_value = abs(difference or 0)

        return {
            "summary": (
                f"The payment of ₹{payment_amount:,.0f} was successful, "
                f"but only ₹{settlement_amount:,.0f} was settled. "
                f"This creates a ₹{difference_value:,.0f} variance."
            ),
            "likely_causes": [
                "Processing fees",
                "Settlement adjustment",
                "Refund or deduction"
            ],
            "confidence": "HIGH",
            "recommended_action": (
                "Review the settlement breakdown and verify "
                "fees, deductions, refunds or other adjustments."
            )
        }

    # Duplicate Payment
    if status == "Duplicate Payment":

        return {
            "summary": (
                "More than one payment record appears to be "
                "associated with the same order."
            ),
            "likely_causes": [
                "Customer retried the payment",
                "Duplicate payment callback",
                "Payment processing duplication"
            ],
            "confidence": "MEDIUM",
            "recommended_action": (
                "Verify whether the duplicate payment is legitimate "
                "and determine whether a refund is required."
            )
        }

    # Matched
    return {
        "summary": (
            "Order, payment and settlement records are "
            "consistent."
        ),
        "likely_causes": [],
        "confidence": "HIGH",
        "recommended_action": "No action required."
    }