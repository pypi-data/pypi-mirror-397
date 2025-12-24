"""
PII Detection and Masking for compliance.
"""

import re
from typing import Tuple, Dict, List
import logging

logger = logging.getLogger(__name__)

class PIIDetector:
    """Detect and mask Personally Identifiable Information."""
    
    PATTERNS = {
        "ssn": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
    }
    
    MASKS = {
        "ssn": "[SSN]",
        "email": "[EMAIL]",
        "phone": "[PHONE]",
    }
    
    def __init__(self, rules: str = "general"):
        self.rules = rules
    
    def mask(self, text: str) -> Tuple[str, Dict[str, int]]:
        """Mask PII in text."""
        if not text:
            return text, {}
        
        masked_text = text
        pii_counts = {}
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                count = len(matches)
                pii_counts[pii_type] = count
                masked_text = re.sub(pattern, self.MASKS[pii_type], masked_text)
        
        return masked_text, pii_counts
    
    def scan(self, text: str) -> Dict[str, List[str]]:
        """Scan for PII without masking."""
        findings = {}
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings[pii_type] = matches
        return findings
