"""
upif.core.interfaces
~~~~~~~~~~~~~~~~~~~~

Defines the abstract base classes and interfaces for the UPIF system.
All security modules must adhere to these contracts to ensure strict type safety
and consistent execution by the Coordinator.

:copyright: (c) 2025 Yash Dhone.
:license: Proprietary, see LICENSE for details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class SecurityModule(ABC):
    """
    Abstract Base Class for all Security Modules (Input Guard, Output Shield, etc.).
    
    Enforces a strict 'scan' contract. Modules should be stateless if possible
    or manage their own thread-safe state.
    """

    @abstractmethod
    def scan(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Scans the provided content for security threats.

        Args:
            content (Any): The payload to scan (usually string, but can be structured).
            metadata (Optional[Dict[str, Any]]): Contextual metadata (e.g., user ID, session).

        Returns:
            Any: The sanitized content (if safe) or a refusal message (if unsafe).
                 MUST NOT raise exceptions; handle internal errors gracefully.
        """
        pass
