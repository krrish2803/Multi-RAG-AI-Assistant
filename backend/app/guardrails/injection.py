"""Prompt injection detector."""

import re
from typing import Optional


# Known injection patterns
INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"ignore (all )?prior instructions",
    r"disregard (all )?previous",
    r"forget (all )?previous",
    r"you are now",
    r"act as (if|a)",
    r"pretend you are",
    r"new instructions?:",
    r"system prompt:",
    r"override (your|the) (instructions|rules)",
    r"reveal (your|the) (system|hidden) prompt",
    r"what (are|were) your (original|initial) instructions",
    r"repeat your (system|initial) prompt",
    r"show me your prompt",
    r"ignore everything above",
    r"ignore everything below",
    r"do not follow (previous|prior|any) (rules|instructions)",
    r"from now on,?",
    r"new role:",
    r"begin new conversation",
]


class InjectionDetector:
    """Detects prompt injection attempts in user input."""

    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    def check(self, text: str) -> dict:
        """Check text for injection patterns.
        
        Returns:
            dict with keys: blocked, matched_patterns, confidence
        """
        matched = []
        for pattern in self.patterns:
            if pattern.search(text):
                matched.append(pattern.pattern)

        confidence = min(len(matched) * 0.4, 1.0) if matched else 0.0
        blocked = len(matched) >= 1

        return {
            "blocked": blocked,
            "matched_patterns": matched,
            "confidence": confidence,
            "type": "injection",
        }
