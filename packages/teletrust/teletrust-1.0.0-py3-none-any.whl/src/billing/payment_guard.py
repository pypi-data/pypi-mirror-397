import os

class PaymentGuard:
    """
    Fail-closed Payment Guard.

    Security Policy:
    - In PROD mode: If Stripe cannot be verified (api error, no key, invalid sub), RETURN FALSE.
    - In DEV mode: Return True (allow bypass).

    Why: Production systems must never "default open" when billing fails.
    """
    def __init__(self):
        self.mode = os.environ.get("MOA_MODE", "dev").lower()
        self.stripe_key = os.environ.get("STRIPE_SECRET_KEY")

    def verify_subscription(self, customer_token: str) -> bool:
        """
        Verify if a customer has an active subscription.
        """
        if self.mode == "dev":
            # LOG: Dev bypass active
            return True

        if not self.stripe_key:
            # FAIL CLOSED: No key in prod = no access
            return False

        try:
            # Real Stripe verification would go here.
            # For now, we stub the logic but enforce the Fail-Closed structure.
            # import stripe
            # sub = stripe.Subscription.retrieve(customer_token)
            # return sub.status == 'active'
            return False # Default to False in PROD until fully wired
        except Exception:
            # FAIL CLOSED: On any error
            return False
