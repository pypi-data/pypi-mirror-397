from typing import Dict, List, Any

class RegulatoryInterceptor:
    """
    Intercepts user input before it reaches the core physics engine to check
    against regulatory policies (e.g., HIPAA, specific disallowed content).

    MVP: Uses keyword matching.
    Future: Connects to an MCP Regulatory Server.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # Hard blocks - these are absolutely prohibited
        self.block_keywords = [
            "HIPAA violation",
            "billing fraud",
            "illegal prescription",
            "suicide pact" # Extreme safety guard
        ]

        # Crisis phrases - require immediate escalation (not blocked, but RED zone)
        self.crisis_keywords = [
            "ending it all",
            "kill myself",
            "suicidal",
            "want to die",
            "hurt myself",
            "self-harm",
            "don't want to live",
            "no reason to live",
        ]

        # In a real MCP setup, we would initialize the client here.
        self.mcp_client = None

    def check_compliance(self, text: str) -> Dict[str, Any]:
        """
        Check if the text complies with regulatory rules.
        Returns:
            {
                "allowed": bool,
                "reason": str (if blocked),
                "signals": List[str],
                "crisis_detected": bool
            }
        """
        signals = []
        lower_text = text.lower()
        crisis_detected = False

        # Check hard blocks first
        for keyword in self.block_keywords:
            if keyword.lower() in lower_text:
                signals.append(f"BLOCK_KEYWORD:{keyword.upper()}")
                return {
                    "allowed": False,
                    "reason": f"Regulatory Block: Detected '{keyword}'",
                    "signals": signals,
                    "crisis_detected": False
                }

        # Check crisis phrases - these are allowed through but flagged
        for keyword in self.crisis_keywords:
            if keyword.lower() in lower_text:
                signals.append(f"CRISIS_DETECTED:{keyword.upper()}")
                crisis_detected = True

        # If no hard blocks, we can still add warning signals
        if "warning" in lower_text:
            signals.append("WARN:General")

        return {
            "allowed": True,
            "reason": "Passed local compliance checks",
            "signals": signals,
            "crisis_detected": crisis_detected
        }
