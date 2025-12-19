"""
Stripe integration for Mike's Way Academic Writing Editor.

Handles payment processing, subscription management, and webhooks.
"""
import os
from datetime import datetime
from typing import Any, Dict, Optional

import stripe

# from src.database import (
#     update_subscription,
#     log_stripe_event,
#     SessionLocal,
#     User
# )

# Metrics Stub
def log_stripe_event(*args, **kwargs):
    print(f"[METRIC] Stripe Event: {kwargs.get('event_type')}")
    return True

def update_subscription(*args, **kwargs):
    print(f"[DB] Update Subscription: {kwargs}")

def SessionLocal():
    return None

class User:
    stripe_customer_id = "cus_mock"

# Configure Stripe
# Configure Stripe
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    print("Warning: STRIPE_SECRET_KEY not found in environment")

# Pricing configuration
PRICING_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "daily_limit": 10,
        "features": [
            "10 paragraphs per day",
            "Basic analysis",
            "Style rewriting"
        ]
    },
    "compliance": {
        "name": "Compliance",
        "price": 49900,  # $499.00
        "daily_limit": 99999,
        "features": [
            "Unlimited paragraphs",
            "Fail-Closed Payment Guard",
            "HMAC Receipts",
            "Auditor Pack Generation",
            "SLA Support"
        ]
    }
}


def create_checkout_session(user_id: int, user_email: str, plan: str = "premium") -> Optional[str]:
    """
    Create Stripe checkout session for subscription.
    Returns checkout URL or None if Stripe not configured.
    """
    if not STRIPE_SECRET_KEY:
        return None

    try:
        # Create or retrieve customer
        customers = stripe.Customer.list(email=user_email, limit=1)
        if customers.data:
            customer = customers.data[0]
        else:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={"user_id": user_id}
            )

        # Get base URL (Fly.dev, Railway, or local)
        base_url = os.environ.get("BASE_URL", os.environ.get("FLY_APP_NAME", "localhost:5000"))
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Mike's Way Academic Writing Editor - {PRICING_PLANS[plan]['name']}",
                        "description": "Unlimited academic writing analysis and rewriting"
                    },
                    "unit_amount": PRICING_PLANS[plan]["price"],
                    "recurring": {"interval": "month"}
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{base_url}/?payment=success",
            cancel_url=f"{base_url}/?payment=cancelled",
            metadata={
                "user_id": user_id,
                "plan": plan
            }
        )

        return session.url
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return None


def handle_webhook(payload: bytes, sig_header: str) -> Dict[str, Any]:
    """
    Handle Stripe webhook events.
    Returns dict with status and message.
    """
    if not STRIPE_WEBHOOK_SECRET:
        return {"status": "error", "message": "Webhook secret not configured"}

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return {"status": "error", "message": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"status": "error", "message": "Invalid signature"}

    # Check if already processed (idempotency)
    if not log_stripe_event(
        stripe_event_id=event["id"],
        event_type=event["type"],
        payload=event,
        customer_id=event["data"]["object"].get("customer"),
        subscription_id=event["data"]["object"].get("id")
    ):
        return {"status": "duplicate", "message": "Event already processed"}

    # Handle different event types
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        handle_checkout_completed(data)
    elif event_type == "customer.subscription.created":
        handle_subscription_created(data)
    elif event_type == "customer.subscription.updated":
        handle_subscription_updated(data)
    elif event_type == "customer.subscription.deleted":
        handle_subscription_deleted(data)
    elif event_type == "invoice.payment_succeeded":
        handle_payment_succeeded(data)
    elif event_type == "invoice.payment_failed":
        handle_payment_failed(data)

    return {"status": "success", "message": f"Processed {event_type}"}


def handle_checkout_completed(session: Dict[str, Any]):
    """Handle successful checkout completion."""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    metadata = session.get("metadata", {})
    user_id = metadata.get("user_id")
    plan = metadata.get("plan", "premium")

    if user_id:
        update_subscription(
            user_id=int(user_id),
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            tier=plan,
            status="active",
            start_date=datetime.utcnow()
        )


def handle_subscription_created(subscription: Dict[str, Any]):
    """Handle new subscription creation."""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status = subscription.get("status")

    # Find user by customer ID
    # db = SessionLocal()
    # try:
    #     user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    #     if user:
    #         period_end = datetime.fromtimestamp(subscription["current_period_end"])
    #         update_subscription(
    #             user_id=user.id,
    #             stripe_subscription_id=subscription_id,
    #             status=status,
    #             end_date=period_end
    #         )
    # finally:
    #     db.close()
    print(f"[BILLING] Stub: Created Subscription {subscription_id} for {customer_id} (status={status})")

def handle_subscription_updated(subscription: Dict[str, Any]):
    print(f"[BILLING] Stub: Updated Subscription {subscription.get('id')}")

def handle_subscription_deleted(subscription: Dict[str, Any]):
    print(f"[BILLING] Stub: Deleted Subscription {subscription.get('id')}")

def handle_payment_succeeded(invoice: Dict[str, Any]):
    print(f"[BILLING] Stub: Payment Succeeded for {invoice.get('customer')}")

def handle_payment_failed(invoice: Dict[str, Any]):
    print(f"[BILLING] Stub: Payment Failed for {invoice.get('customer')}")


def get_customer_portal_url(customer_id: str) -> Optional[str]:
    """
    Create customer portal session for managing subscription.
    Returns portal URL or None if error.
    """
    if not STRIPE_SECRET_KEY:
        return None

    try:
        # Get base URL (Fly.dev, Railway, or local)
        base_url = os.environ.get("BASE_URL", os.environ.get("FLY_APP_NAME", "localhost:5000"))
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=base_url
        )

        return session.url
    except Exception as e:
        print(f"Error creating portal session: {e}")
        return None

def meter_usage(subscription_item_id: str, quantity: int = 1, idempotency_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Record usage for metered billing.

    Args:
        subscription_item_id: Stripe SubscriptionItem ID (si_...)
        quantity: Number of units to record
        idempotency_key: Optional unique key to prevent duplicate records

    Returns:
        Usage record dict or None if failed
    """
    if not STRIPE_SECRET_KEY:
        print("[BILLING] Stripe not configured, skipping usage record")
        return None

    import time

    try:
        usage_record = stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=int(time.time()),
            action='increment',
            idempotency_key=idempotency_key,
        )
        print(f"[BILLING] Recorded usage: {quantity} units for {subscription_item_id}")
        return {
            "id": usage_record.id,
            "quantity": usage_record.quantity,
            "timestamp": usage_record.timestamp,
        }
    except stripe.error.StripeError as e:
        print(f"[BILLING] Failed to record usage: {e}")
        return None


def get_subscription_item_for_customer(customer_id: str, price_lookup_key: str = "moa_audit_pack_per_unit") -> Optional[str]:
    """
    Get the subscription item ID for a customer's metered product.

    Args:
        customer_id: Stripe Customer ID
        price_lookup_key: The lookup key of the metered price

    Returns:
        Subscription Item ID or None
    """
    if not STRIPE_SECRET_KEY:
        return None

    try:
        subscriptions = stripe.Subscription.list(customer=customer_id, status="active", limit=10)
        for sub in subscriptions.auto_paging_iter():
            for item in sub["items"]["data"]:
                if item.price.lookup_key == price_lookup_key:
                    return item.id
        return None
    except stripe.error.StripeError as e:
        print(f"[BILLING] Failed to get subscription item: {e}")
        return None
