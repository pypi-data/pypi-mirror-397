
import os
import requests
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP
from src.billing.stripe_integration import meter_usage

# Initialize FastMCP server
mcp = FastMCP("Telehealth Citation Gateway")

# STATIC REFERENCES (Labeling as per instructions)
# Real NLM/UMLS requires API keys not present in env yet.
NLM_CODES_STATIC = {
    "99213": "Office or other outpatient visit for the evaluation and management of an established patient.",
    "90837": "Psychotherapy, 60 minutes with patient and/or family member."
}

CA_STATUTES_STATIC = {
    "AB-456": "California Assembly Bill 456: Telehealth parity.",
    "BPC-2290.5": "Business and Professions Code 2290.5: Telehealth consent requirements."
}

@mcp.tool()
def lookup_ecfr(query: str, title: str = None, section: str = None) -> str:
    """
    Look up federal regulations in the eCFR using the official API.
    """
    # Meter usage execution
    meter_usage(user_id=0, capability="ecfr_lookup", quantity=1)

    base_url = "https://www.ecfr.gov/api/search/v1/results"
    params = {
        "query": query,
        "per_page": 3
    }
    if title:
        params["title"] = title

    try:
        resp = requests.get(base_url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return "No results found in eCFR."

        summary = []
        for r in results:
            ref = f"{r.get('title')} CFR {r.get('section')}"
            header = r.get("hierarchy", {}).get("part", {}).get("description", "Regulation")
            # Clean up HTML snippet if present, simplistic approach for now
            summary.append(f"[{ref}] {header}: {r.get('summary', 'No summary available.')}")

        return "\n\n".join(summary)
    except Exception as e:
        return f"Error contacting eCFR API: {str(e)}"

@mcp.tool()
def lookup_nlm_codes(keyword: str) -> str:
    """
    Look up clinical codes (CPT, HCPCS) from NLM.
    (Currently using Static Reference Table due to missing UMLS API keys)
    """
    meter_usage(user_id=0, capability="nlm_lookup", quantity=1)

    if keyword in NLM_CODES_STATIC:
        return f"[STATIC_REF] {keyword}: {NLM_CODES_STATIC[keyword]}"
    return "Code not found in static reference."

@mcp.tool()
def get_ca_telehealth_statutes() -> str:
    """
    Retrieve California telehealth statutes.
    (Currently using Static Reference Table)
    """
    meter_usage(user_id=0, capability="ca_statutes", quantity=1)

    return "\n".join([f"[STATIC_REF] {k}: {v}" for k, v in CA_STATUTES_STATIC.items()])

if __name__ == "__main__":
    mcp.run()
