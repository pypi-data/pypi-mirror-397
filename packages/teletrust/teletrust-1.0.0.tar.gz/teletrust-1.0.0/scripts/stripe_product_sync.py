from __future__ import annotations

import argparse
import json
import os

import stripe


def must_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v

def norm_price_spec(p: dict) -> tuple:
    recurring = p.get("recurring") or {}
    return (
        int(p["unit_amount"]),
        recurring.get("interval") or "",
        recurring.get("usage_type") or "",
        recurring.get("aggregate_usage") or "",
        p.get("billing_scheme") or "",
        p.get("nickname") or "",
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    stripe.api_key = must_env("STRIPE_SECRET_KEY")

    cat = json.load(open(args.catalog, "r", encoding="utf-8"))
    currency = cat.get("currency", "usd")

    out = {"products": []}

    # Stripe product lookup by exact name (simple + predictable)
    all_products = list(stripe.Product.list(limit=100, active=True).auto_paging_iter())

    for spec in cat["products"]:
        name = spec["name"]
        meta = spec.get("metadata") or {}
        product = next((p for p in all_products if p.get("name") == name), None)

        if not product:
            print(f"MISSING product: {name}")
            if args.apply:
                product = stripe.Product.create(name=name, metadata=meta)
                print(f"CREATED product {name} -> {product['id']}")
            else:
                continue
        else:
            # keep metadata in sync
            if args.apply and meta:
                stripe.Product.modify(product["id"], metadata=meta)

        # fetch prices for this product
        existing_prices = list(stripe.Price.list(product=product["id"], limit=100).auto_paging_iter())
        existing_norm = { norm_price_spec({
            "unit_amount": p.get("unit_amount"),
            "recurring": (p.get("recurring") or {}),
            "billing_scheme": p.get("billing_scheme"),
            "nickname": p.get("nickname")
        }): p for p in existing_prices if p.get("unit_amount") is not None }

        created = []
        for ps in spec.get("prices", []):
            ps = dict(ps)
            ps["unit_amount"] = int(ps["unit_amount"])
            key = norm_price_spec(ps)
            if key in existing_norm:
                created.append(existing_norm[key]["id"])
                continue

            print(f"MISSING price for {name}: {ps}")
            if not args.apply:
                continue

            payload = {
                "product": product["id"],
                "currency": currency,
                "unit_amount": ps["unit_amount"],
                "nickname": ps.get("nickname"),
            }
            if ps.get("recurring"):
                payload["recurring"] = ps["recurring"]
            if ps.get("billing_scheme"):
                payload["billing_scheme"] = ps["billing_scheme"]

            pr = stripe.Price.create(**payload)
            print(f"CREATED price -> {pr['id']}")
            created.append(pr["id"])

        out["products"].append({
            "name": name,
            "product_id": product["id"],
            "price_ids": created
        })

    out_path = os.path.join(os.path.dirname(args.catalog), "stripe_ids.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"WROTE {out_path}")

if __name__ == "__main__":
    main()
