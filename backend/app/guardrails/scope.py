"""Out-of-scope topic classifier."""

import re
from typing import Optional


# Topics that are in scope
IN_SCOPE_TOPICS = [
    "company", "policy", "policies", "hr", "human resources", "benefits",
    "salary", "compensation", "leave", "vacation", "insurance", "health",
    "finance", "financial", "budget", "revenue", "expense", "report",
    "engineering", "software", "code", "development", "architecture",
    "marketing", "brand", "campaign", "customer", "sales",
    "meeting", "project", "team", "department", "office", "workplace",
    "onboarding", "training", "performance", "review", "promotion",
    "it ", "technology", "system", "access", "password", "security",
    "travel", "reimbursement", "procurement", "vendor",
    "compliance", "regulation", "audit", "standard", "procedure",
    "employee", "manager", "executive", "organization",
]

# Patterns that suggest out-of-scope
OUT_OF_SCOPE_PATTERNS = [
    r"what('s| is) the (weather|temperature|forecast)",
    r"(cook|recipe|bake|fry|boil)",
    r"(movie|film|tv show|netflix|series) (recommendation|suggestion)",
    r"(write|compose) (a )?(poem|song|story|novel) (about|for)",
    r"(translate|translation) (to|into)",
    r"(math|calculus|algebra|geometry) (problem|equation)",
    r"(personal|dating|relationship) (advice|help)",
    r"(investment|stock|crypto|bitcoin) (advice|recommendation)",
    r"(medical|health) (advice|diagnosis)",
    r"(legal) (advice|counsel)",
]


class ScopeDetector:
    """Detects whether a question is within the scope of the enterprise assistant."""

    def __init__(self):
        self.out_of_scope_patterns = [
            re.compile(p, re.IGNORECASE) for p in OUT_OF_SCOPE_PATTERNS
        ]
        self.in_scope_keywords = IN_SCOPE_TOPICS

    def check(self, text: str) -> dict:
        """Check if the question is in scope.
        
        Returns:
            dict with keys: blocked, in_scope, confidence, reason
        """
        text_lower = text.lower()

        # Check for explicit out-of-scope patterns
        for pattern in self.out_of_scope_patterns:
            if pattern.search(text):
                return {
                    "blocked": True,
                    "in_scope": False,
                    "confidence": 0.8,
                    "reason": "Question appears to be outside enterprise knowledge scope",
                    "type": "scope",
                }

        # Check for in-scope keywords
        keyword_matches = sum(1 for kw in self.in_scope_keywords if kw in text_lower)
        
        # If no keywords match and text is short, likely out of scope
        if keyword_matches == 0 and len(text.split()) < 5:
            return {
                "blocked": False,  # Don't block, just flag
                "in_scope": False,
                "confidence": 0.4,
                "reason": "No enterprise-related keywords detected",
                "type": "scope",
            }

        return {
            "blocked": False,
            "in_scope": True,
            "confidence": min(keyword_matches * 0.2, 1.0),
            "reason": "Question appears to be within enterprise knowledge scope",
            "type": "scope",
        }
