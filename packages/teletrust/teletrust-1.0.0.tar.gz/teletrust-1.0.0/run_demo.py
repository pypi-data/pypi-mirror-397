"""
MOA Telehealth Governor v1.1 - Value Demo
==========================================
Demonstrates the full "Telehealth Delivery Bundle":
1. Cross-State Permission Gating (FL/NY)
2. IP Protection (Strip + Log of DSM/CPT)
3. Hash-Chained Usage Ledger (Audit)
4. Crisis Safety Intervention

Usage:
    python run_demo.py
"""

import sys
import time
import json
from pathlib import Path

# Fix Paths
ROOT = Path(__file__).parent
sys.path.append(str(ROOT))

try:
    from src.governor.telehealth_governor import TelehealthGovernor
    from colorama import Fore, Style, init
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

init()

def print_banner():
    print(Fore.CYAN + "="*70)
    print(Fore.WHITE + "   MOA TELEHEALTH GOVERNOR v1.1 (Production Ready)")
    print(Fore.CYAN + "   (c) 2025 Michael Ordon")
    print(Fore.CYAN + "="*70 + Style.RESET_ALL)
    print()

def run_interaction(gov, title, text, context=None):
    print(Fore.YELLOW + f"--- SCENARIO: {title} ---" + Style.RESET_ALL)
    print(f"{Fore.WHITE}INPUT:{Style.RESET_ALL} \"{text[:60]}...\"")
    if context:
        print(f"{Fore.WHITE}CONTEXT:{Style.RESET_ALL} {json.dumps(context)}")

    # Run Governor
    res = gov.process_interaction("demo_session", text, context=context)

    # Display Results
    print(f"\n{Fore.GREEN}>> GOVERNANCE RESULT:{Style.RESET_ALL}")

    # 1. COMPLIANCE & BILLING
    verdict_color = Fore.GREEN if res.compliance_verdict == "ALLOW" else Fore.RED
    print(f"   Verdict:    {verdict_color}{res.compliance_verdict}{Style.RESET_ALL}")
    if res.compliance_verdict == "ALLOW" and res.billing:
        print(f"   Billing:    POS {res.billing.get('pos_code')} ({res.billing.get('modifiers')})")

    # 2. SANITIZATION
    if res.sanitization and res.sanitization.get("redacted"):
        print(f"   Redaction:  {Fore.MAGENTA}YES{Style.RESET_ALL} Tags={res.sanitization.get('tags')}")
        print(f"               Input sanitized to protect IP.")

    # 3. LEDGER
    if res.usage_events:
        print(f"   Ledger:     {Fore.BLUE}{len(res.usage_events)} Events Recorded{Style.RESET_ALL}")
        for ev in res.usage_events:
            print(f"               + {ev['event']} (qty={ev.get('quantity',1)})")

    # 4. ACTION
    if res.output_text.startswith("Blocked"):
        print(f"\n   ACTION: {Fore.RED}⛔ BLOCKED{Style.RESET_ALL}")
        print(f"   Reason: {res.output_text}")
    elif "988" in res.output_text:
        print(f"\n   ACTION: {Fore.RED}🚨 CRISIS INTERVENTION{Style.RESET_ALL}")
        print(f"   Output: {res.output_text}")
    else:
        print(f"\n   ACTION: {Fore.GREEN}✅ APPROVED{Style.RESET_ALL}")
        print(f"   Output: {res.output_text[:100]}...")

    print("\n" + Fore.CYAN + "-"*70 + Style.RESET_ALL + "\n")
    time.sleep(0.5)

def main():
    print_banner()

    gov = TelehealthGovernor()

    # Scenario 1: Valid FL Registration (Requires explicit FL license in list to pass new general rule)
    run_interaction(gov,
        "Valid FL Registration (Requires explicit FL license in list to pass new general rule)",
        "Dr. Smith performing standard intake....",
        context={
            "patient_state": "FL",
            "provider_home_state": "NY",
            "provider_licenses": ["NY", "FL"], # Added FL license
            "telehealth_registration_number": "TPMC1234",
            "service_mode": "video"
        }
    )

    # Scenario 2: DSM IP Protection (Strip + Log) - Needs valid license to get to Strip stage
    run_interaction(gov,
        "DSM IP Protection (Strip + Log) - Needs valid license to get to Strip stage",
        "Patient exhibits signs of [DSM-5 Code: 300.02 (Generalized Anxiety Disorder)] logic...",
        context={
            "patient_state": "CA",
            "provider_home_state": "CA",
            "provider_licenses": ["CA"], # Added CA license
            "standard": "DSM",
            "dsm_excerpt": "300.02"
        }
    )

    # Scenario 3: Unlicensed Cross-State (Block) - Should FAIL naturally
    run_interaction(gov,
        "Unlicensed Cross-State (Block) - Should FAIL naturally",
        "Attempting consult without registration....",
        context={
            "patient_state": "FL",
            "provider_home_state": "NY",
            "provider_licenses": ["NY"], # No FL license
            "service_mode": "video"
        }
    )

    # Scenario 4: Safety Rails (Crisis) - Override behavior checks (Crisis usually is 1b BEFORE compliance? No, 1b is after compliance in current code).
    # Wait, code says: 1. Compliance (Block if fail). 1b. Crisis.
    # So if we block on license, we never see Crisis?
    # Actually, Crisis check is *after* compliance in `telehealth_governor.py`:
    #   100: comp_res = engine.evaluate()
    #   126: if Deny -> Return
    #   146: Crisis Check
    # So unlicensed crisis calls are blocked by compliance first. This is a policy decision (Is it okay? User said fail-closed).
    # For demo, let's allow it to pass compliance so we see Crisis logic.
    run_interaction(gov,
        "Safety Rails (Crisis) - Override behavior checks (Crisis usually is 1b BEFORE compliance? No, 1b is after compliance in current code).",
        "I am thinking about suicide....",
        context={
            "patient_state": "CA",
            "provider_home_state": "CA",
            "provider_licenses": ["CA"]
        }
    )

    print(f"{Fore.WHITE}Demo Complete. Check usage_ledger.jsonl for audit trail.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
