"""
Paywall Decorators for API Endpoints

Provides decorators to enforce subscription requirements and meter usage.
"""
import os
import functools
from typing import Callable, Optional, List
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import billing functions
from src.billing.stripe_integration import (
    get_subscription_item_for_customer,
    meter_usage,
    STRIPE_SECRET_KEY,
)

security = HTTPBearer(auto_error=False)


class TierRequired:
    """Dependency that checks if user has required subscription tier."""

    TIER_LEVELS = {
        "free": 0,
        "auditor": 0,  # Alias for free
        "governor": 1,
        "enterprise": 2,
        "shield": 2,  # Alias for enterprise
    }

    def __init__(self, minimum_tier: str = "free"):
        self.minimum_tier = minimum_tier.lower()
        self.minimum_level = self.TIER_LEVELS.get(self.minimum_tier, 0)

    async def __call__(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    ):
        # Get user tier from request state (set by auth middleware)
        user_tier = getattr(request.state, "user_tier", "free")
        user_level = self.TIER_LEVELS.get(user_tier.lower(), 0)

        if user_level < self.minimum_level:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "payment_required",
                    "message": f"This feature requires {self.minimum_tier} tier or higher.",
                    "required_tier": self.minimum_tier,
                    "current_tier": user_tier,
                    "upgrade_url": os.environ.get("STRIPE_CHECKOUT_URL", "/api/billing/checkout"),
                }
            )

        return user_tier


def require_tier(tier: str):
    """Decorator to require minimum subscription tier."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            # Simplified tier check
            user_tier = getattr(request.state, "user_tier", "free") if request else "free"
            tier_levels = TierRequired.TIER_LEVELS

            if tier_levels.get(user_tier.lower(), 0) < tier_levels.get(tier.lower(), 0):
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "payment_required",
                        "message": f"This feature requires {tier} tier or higher.",
                        "required_tier": tier,
                        "current_tier": user_tier,
                    }
                )

            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator


def metered(capability: str, quantity: int = 1):
    """
    Decorator to meter API usage for billing.

    Records usage after successful endpoint execution.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            # Execute the function first
            result = await func(*args, request=request, **kwargs)

            # If successful, record usage
            if request and hasattr(request.state, "stripe_customer_id"):
                customer_id = request.state.stripe_customer_id
                sub_item_id = get_subscription_item_for_customer(customer_id)

                if sub_item_id:
                    # Create idempotency key from request
                    idempotency_key = f"{customer_id}:{capability}:{id(request)}"
                    meter_usage(sub_item_id, quantity, idempotency_key)

            return result
        return wrapper
    return decorator


# FastAPI Dependency versions
def tier_dependency(tier: str):
    """Create a FastAPI dependency for tier checking."""
    return Depends(TierRequired(minimum_tier=tier))


# Example usage in route:
# @app.post("/api/audit/generate", dependencies=[tier_dependency("governor")])
# async def generate_audit_packet(...):
#     ...
