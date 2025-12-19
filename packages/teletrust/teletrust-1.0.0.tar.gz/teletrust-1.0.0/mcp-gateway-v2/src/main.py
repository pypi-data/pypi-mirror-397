"""
MCP Regulatory Gateway - Apify Actor

Pay-per-event metered billing for healthcare regulatory compliance lookups.
Wraps the FastMCP tools with Actor.charge() for marketplace monetization.
"""
import asyncio
import requests
from apify import Actor

# Static reference tables (same as src/reg_gateway/server.py)
NLM_CODES_STATIC = {
    "99213": "Office or other outpatient visit for the evaluation and management of an established patient.",
    "90837": "Psychotherapy, 60 minutes with patient and/or family member.",
    "99214": "Office visit, established patient, moderate complexity.",
    "99215": "Office visit, established patient, high complexity.",
}

CA_STATUTES_STATIC = {
    "AB-456": "California Assembly Bill 456: Telehealth parity.",
    "BPC-2290.5": "Business and Professions Code 2290.5: Telehealth consent requirements.",
    "HSC-1374.13": "Health and Safety Code 1374.13: Health plan coverage for telehealth.",
}


async def lookup_ecfr(query: str, title: str = None) -> str:
    """Look up federal regulations in the eCFR using the official API."""
    base_url = "https://www.ecfr.gov/api/search/v1/results"
    params = {"query": query, "per_page": 3}
    if title:
        params["title"] = title

    try:
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return "No results found in eCFR."

        summary = []
        for r in results:
            ref = f"{r.get('title')} CFR {r.get('section')}"
            header = r.get("hierarchy", {}).get("part", {}).get("description", "Regulation")
            summary.append(f"[{ref}] {header}: {r.get('summary', 'No summary available.')}")

        return "\n\n".join(summary)
    except Exception as e:
        return f"Error contacting eCFR API: {str(e)}"


async def lookup_nlm_codes(keyword: str) -> str:
    """Look up clinical codes (CPT, HCPCS) from NLM static reference."""
    if keyword in NLM_CODES_STATIC:
        return f"[REF] {keyword}: {NLM_CODES_STATIC[keyword]}"
    return f"Code '{keyword}' not found. Available: {', '.join(NLM_CODES_STATIC.keys())}"


async def get_ca_telehealth_statutes() -> str:
    """Retrieve California telehealth statutes from static reference."""
    return "\n".join([f"[REF] {k}: {v}" for k, v in CA_STATUTES_STATIC.items()])


async def main():
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        tool = actor_input.get("tool", "lookup_ecfr")
        query = actor_input.get("query", "telehealth")
        title = actor_input.get("title")

        Actor.log.info(f"Processing tool={tool} query={query}")

        result = None
        event_name = None

        # Route to appropriate tool and charge
        if tool == "lookup_ecfr":
            event_name = "regulation_lookup"
            result = await lookup_ecfr(query, title)

        elif tool == "lookup_nlm_codes":
            event_name = "billing_code_lookup"
            result = await lookup_nlm_codes(query)

        elif tool == "get_ca_telehealth_statutes":
            event_name = "compliance_check"
            result = await get_ca_telehealth_statutes()

        else:
            result = f"Unknown tool: {tool}. Available: lookup_ecfr, lookup_nlm_codes, get_ca_telehealth_statutes"

        # Charge for the event (Apify metered billing)
        if event_name:
            try:
                await Actor.charge(event_name=event_name, count=1)
                Actor.log.info(f"Charged for event: {event_name}")
            except Exception as e:
                Actor.log.warning(f"Billing charge failed (may be in dev mode): {e}")

        # Push result to dataset
        await Actor.push_data({
            "tool": tool,
            "query": query,
            "result": result,
            "event_charged": event_name
        })

        Actor.log.info("Actor completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
