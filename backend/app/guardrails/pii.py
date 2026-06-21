"""PII (Personally Identifiable Information) detector."""

import re
from typing import Optional


# PII patterns for common types
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "date_of_birth": re.compile(r"\b(?:born on|DOB|birth date)[:\s]+\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b", re.IGNORECASE),
}

# Redaction patterns
REDACTION_MAP = {
    "email": "[EMAIL REDACTED]",
    "phone": "[PHONE REDACTED]",
    "ssn": "[SSN REDACTED]",
    "credit_card": "[CREDIT CARD REDACTED]",
    "ip_address": "[IP REDACTED]",
    "date_of_birth": "[DOB REDACTED]",
}


class PIIDetector:
    """Detects and optionally redacts PII in text."""

    def __init__(self):
        self.patterns = PII_PATTERNS

    def scan(self, text: str) -> dict:
        """Scan text for PII entities.
        
        Returns:
            dict with keys: contains_pii, entities, entity_types
        """
        entities = []
        entity_types = set()

        for entity_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                entities.extend([
                    {"type": entity_type, "value": m} for m in matches
                ])
                entity_types.add(entity_type)

        return {
            "contains_pii": len(entities) > 0,
            "entities": entities,
            "entity_types": list(entity_types),
            "count": len(entities),
            "type": "pii",
        }

    def redact(self, text: str) -> str:
        """Redact PII from text by replacing with placeholders."""
        redacted = text
        for entity_type, pattern in self.patterns.items():
            replacement = REDACTION_MAP.get(entity_type, "[REDACTED]")
            redacted = pattern.sub(replacement, redacted)
        return redacted
