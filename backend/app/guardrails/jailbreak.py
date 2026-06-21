"""Jailbreak detector - detects attempts to bypass safety measures."""

import re
from typing import Optional


# Known jailbreak patterns and keywords
JAILBREAK_PATTERNS = [
    r"DAN \(Do Anything Now\)",
    r"do anything now",
    r"bypass (your|the|all) (restrictions|limitations|rules|safety)",
    r"remove (your|all) (restrictions|limitations|filters)",
    r"act (as if|like) you (have|had) no (rules|restrictions|limitations)",
    r"pretend (you are|to be) (an? )?unrestricted",
    r"without (any )?(content|safety|ethical) (filter|policy|guidelines)",
    r"jailbreak",
    r"you have been freed",
    r"you are (now )?free (to|from)",
    r"unfiltered mode",
    r"developer mode (enabled|activated|on)",
    r"STAN \(Strive To Avoid Norms\)",
    r"DUDE mode",
    r"AIM \(Always Intelligent Machiavellian\)",
    r"KEVIN mode",
    r"evil mode",
    r"dark mode enabled",
    r"no ethical constraints",
    r"no moral (guidelines|restrictions|limits)",
]


class JailbreakDetector:
    """Detects jailbreak attempts in user input."""

    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in JAILBREAK_PATTERNS]

    def check(self, text: str) -> dict:
        """Check text for jailbreak patterns.
        
        Returns:
            dict with keys: blocked, matched_patterns, confidence
        """
        matched = []
        for pattern in self.patterns:
            if pattern.search(text):
                matched.append(pattern.pattern)

        # Also check for suspicious length/format (common in jailbreak prompts)
        suspicious_format = False
        if len(text) > 500 and any(kw in text.lower() for kw in ["role", "character", "scenario", "story"]):
            suspicious_format = True

        confidence = min(len(matched) * 0.5, 1.0) if matched else (0.3 if suspicious_format else 0.0)
        blocked = len(matched) >= 1

        return {
            "blocked": blocked,
            "matched_patterns": matched,
            "suspicious_format": suspicious_format,
            "confidence": confidence,
            "type": "jailbreak",
        }
