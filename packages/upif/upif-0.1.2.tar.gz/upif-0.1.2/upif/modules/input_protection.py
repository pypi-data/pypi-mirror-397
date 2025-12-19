"""
upif.modules.input_protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The First Line of Defense.
Implements heuristic analysis using massive regex pattern matching
to detect SQL Injection, XSS, Jailbreaks, and Prompt Manipulations.

:copyright: (c) 2025 Yash Dhone.
:license: Proprietary, see LICENSE for details.
"""

import re
import json
import os
from typing import Any, List, Optional, Dict
from upif.core.interfaces import SecurityModule

class InputGuard(SecurityModule):
    """
    Heuristic Input Guard.
    
    Capabilities:
    - Regex matching against 250+ known attack vectors.
    - JSON-based pattern loading for easy updates.
    - Configurable refusal messages (Internationalization ready).
    """

    def __init__(self, refusal_message: str = "Input unsafe. Action blocked."):
        """
        Initialize the Input Guard.

        Args:
            refusal_message (str): The message returned to the host application
                                   when an attack is detected.
        """
        self.refusal_message = refusal_message
        self.patterns: List[str] = []
        self._load_patterns()
        
        # Pre-compile regexes for performance (compilation happens once at startup)
        # Using IGNORECASE for broad matching
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    def _load_patterns(self) -> None:
        """
        Internal: Loads attack signatures from the bundled JSON database.
        
        Fail-Safe: If JSON allows parsing errors or is missing, falls back to
                   a minimal hardcoded set to ensure BASIC protection remains.
        """
        # Relative path resolution for self-contained distribution
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(base_dir, "data", "patterns.json")
        
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract patterns from all categories
            raw_patterns = []
            for category, pattern_list in data.get("categories", {}).items():
                if isinstance(pattern_list, list):
                    raw_patterns.extend(pattern_list)
                    
            # Critical: Escape special regex characters in the strings
            # We treat the JSON entries as "Signatures" (Literals), not "Regexes"
            # This prevents a malformed user string in JSON from crashing the engine.
            self.patterns.extend([re.escape(p) for p in raw_patterns])
            
        except Exception as e:
            # Silent Fail-Safe (Logged via Coordinator if this instantiates, 
            # but ideally we print here since Logger might not be ready)
            # In production, we assume standard library logging or print to stderr
            print(f"UPIF WARNING: Pattern Logic Fallback due to: {e}")
            self.patterns = [re.escape("ignore previous instructions"), re.escape("system override")]

    def scan(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Scans input string for known attack patterns.

        Args:
            content (Any): Payload. If not string, it is ignored (Pass-through).
            metadata (dict): Unused in Heuristic scan.

        Returns:
            str: Original content or self.refusal_message.
        """
        if not isinstance(content, str):
            return content
            
        # Linear Scan (Optimization: Could use Aho-Corasick for O(n) in v2)
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                # Attack Detected
                return self.refusal_message
                
        return content
