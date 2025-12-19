"""
upif.modules.output_protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Data Loss Prevention (DLP) layer.
Scans outgoing model responses for Personally Identifiable Information (PII)
and Secrets (API Keys) to prevent leakage.

:copyright: (c) 2025 Yash Dhone.
:license: Proprietary, see LICENSE for details.
"""

import re
from typing import Any, Optional, Dict, List
from upif.core.interfaces import SecurityModule

class OutputShield(SecurityModule):
    """
    PII and Secret Redaction Shield.
    
    Targets:
    - Email Addresses
    - US Phone Numbers
    - SSN (Social Security Numbers)
    - Generic API Keys (sk-..., gh_-...)
    """
    
    def __init__(self):
        # Compiled Regex Patterns for Performance
        self.patterns: List[Dict[str, Any]] = [
            # Email (Standard RFC-ish)
            {
                "name": "EMAIL_REDACTED",
                "regex": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            },
            # Phone (US Format mostly, simplistic)
            {
                "name": "PHONE_REDACTED",
                "regex": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
            },
            # SSN (Simple)
            {
                "name": "SSN_REDACTED",
                "regex": re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
            },
            # API Keys (Common prefixes)
            {
                "name": "API_KEY_REDACTED",
                "regex": re.compile(r'\b(sk-[a-zA-Z0-9]{20,}|gh[pousr]-[a-zA-Z0-9]{20,})\b')
            }
        ]

    def scan(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Redacts Sensitive Info from the content string.

        Args:
            content (Any): Model response.
        
        Returns:
            str: Redacted string (e.g., "Email: [EMAIL_REDACTED]")
        """
        if not isinstance(content, str):
            return content
            
        sanitized = content
        for p in self.patterns:
            # Replace found patterns with [NAME]
            # Efficient implementation: re.sub scans whole string
            sanitized = p["regex"].sub(f"[{p['name']}]", sanitized)
            
        return sanitized
