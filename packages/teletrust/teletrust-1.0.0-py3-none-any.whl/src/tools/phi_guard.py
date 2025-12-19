import re
from typing import List, Tuple

class PhiGuard:
    """
    Protects against PHI leakage by detecting and regarding sensitive patterns
    before they leave the system boundaries.
    """

    # Simple regex patterns for common PHI identifiers
    PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "PHONE": r"\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "MRN": r"\bMRN-?\d{6,}\b", # Example pattern for Medical Record Number
        # Add more patterns as needed (Dates, IPs, etc based on HIPAA)
    }

    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.PATTERNS.items()
        }

    def scan(self, text: str) -> bool:
        """
        Returns True if any PHI pattern is detected in the text.
        """
        for pattern in self.compiled_patterns.values():
            if pattern.search(text):
                return True
        return False

    def redact(self, text: str) -> str:
        """
        Replaces detected PHI with [REDACTED:<TYPE>].
        """
        redacted_text = text
        for name, pattern in self.compiled_patterns.items():
            redacted_text = pattern.sub(f"[REDACTED:{name}]", redacted_text)
        return redacted_text

    def get_detected_types(self, text: str) -> List[str]:
        """
        Returns a list of the types of PHI detected.
        """
        detected = []
        for name, pattern in self.compiled_patterns.items():
            if pattern.search(text):
                detected.append(name)
        return detected
