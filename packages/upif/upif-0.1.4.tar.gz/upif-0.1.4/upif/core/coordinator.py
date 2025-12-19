"""
upif.core.coordinator
~~~~~~~~~~~~~~~~~~~~~

The Central Nervous System of UPIF.
Manages the orchestration of security modules, enforces timeouts,
and guarantees Fail-Safe execution (Zero-Crash Policy).

:copyright: (c) 2025 Yash Dhone.
:license: Proprietary, see LICENSE for details.
"""

import concurrent.futures
import logging
from typing import Any, Optional, Dict
from upif.core.interfaces import SecurityModule
from upif.utils.logger import setup_logger, log_audit

# Configure high-performance structured logger
logger = setup_logger("upif.coordinator")

class GovernanceCoordinator:
    """
    Coordinator orchestrates the security pipeline.
    
    Design Guarantees:
    1. Fail-Safe: Internal errors in modules NEVER propagate to the host app.
    2. Zero-Latency: Fallback to pass-through on timeout.
    3. Observable: All security decisions are logged to JSON audit logs.
    """

    def __init__(self, timeout_ms: int = 50, audit_mode: bool = False):
        """
        Initialize the Governance Coordinator.

        Args:
            timeout_ms (int): Hard execution limit per module in milliseconds.
                              Defaults to 50ms (aggressive real-time target).
            audit_mode (bool): If True, detected threats are logged but NOT blocked.
                               Useful for initial deployment and shadow testing.
        """
        self.timeout_seconds: float = timeout_ms / 1000.0
        self.audit_mode: bool = audit_mode
        
        # Security Pipeline Components
        self.input_guard: Optional[SecurityModule] = None
        self.output_shield: Optional[SecurityModule] = None
        self.neural_guard: Optional[SecurityModule] = None
        
        # Dedicated ThreadPool for isolation and timeout enforcement
        # max_workers is tuned small to prevent resource starvation on host
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="UPIF_Worker")

    def register_input_guard(self, guard: SecurityModule) -> None:
        """Registers the primary heuristic input guard (Regex/Pattern)."""
        self.input_guard = guard

    def register_output_shield(self, shield: SecurityModule) -> None:
        """Registers the output protection shield (PII/Secret Redaction)."""
        self.output_shield = shield
        
    def register_neural_guard(self, guard: SecurityModule) -> None:
        """Registers the semantic AI guard (ONNX/Deep Learning)."""
        self.neural_guard = guard

    def process_input(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Public Entry Point: Scans input prompt for injections and malicious intent.

        Pipeline:
            1. InputHeuristic (Regex/Fast)
            2. InputNeural (AI/Semantic) - *If enabled and heuristic passed*

        Args:
            content (str): The user input prompt.
            metadata (dict): Context (user_id, session_id) for audit logging.

        Returns:
            str: Original content (if safe), Sanitized content, or Refusal Message.
        """
        # 1. Fast Path: Heuristic Scan
        # We run this first as it catches 90% of known attacks with <1ms latency.
        result = self._run_fail_safe(self.input_guard, content, metadata, "InputHeuristic")
        
        # Optimization: If blocked by regex, return immediately. Don't waste CPU on AI.
        # We assume the guard has a 'refusal_message' attribute to compare against.
        refusal_msg = getattr(self.input_guard, 'refusal_message', None)
        if refusal_msg and result == refusal_msg:
             return result
             
        # 2. Deep Path: Neural Scan
        # Only runs if Heuristics passed. Checks for semantic meaning (e.g., "Imagine a world...").
        if self.neural_guard:
             result_ai = self._run_fail_safe(self.neural_guard, result, metadata, "InputNeural")
             return result_ai
             
        return result

    def process_output(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Public Entry Point: Scans model output for PII leakage or Toxic content.

        Args:
            content (str): The LLM response.
            metadata (dict): Context.

        Returns:
            str: Redacted or Safe content.
        """
        return self._run_fail_safe(self.output_shield, content, metadata, "Output")

    def _run_fail_safe(self, module: Optional[SecurityModule], content: str, metadata: Optional[Dict[str, Any]], context: str) -> str:
        """
        Executes a security module within a Fail-Safe, Timed, and Audited context.

        Critical Logic:
            - Catches ALL exceptions.
            - Enforces hard timeouts via ThreadPool.
            - Logs strict Audit Events to JSON.
            - Respects 'Audit Mode' (Pass-through if detection only).
        """
        try:
            # Short-circuit if module not configured or content is empty
            if not module or not content:
                return content

            # Submit to isolated worker thread
            future = self._executor.submit(self._safe_scan, module, content, metadata)
            
            try:
                # Wait for result with strict timeout
                result = future.result(timeout=self.timeout_seconds)
                
                # DETECTION LOGIC
                # If the module modified the content (redaction or refusal), a detection occurred.
                if result != content:
                    
                    # Log Threat (Structured JSON)
                    log_audit(logger, "THREAT_DETECTED", {
                        "module": context,
                        "outcome": "BLOCKED" if not self.audit_mode else "AUDIT_ONLY",
                        "size_bytes": len(content.encode('utf-8'))
                    })
                    
                    if self.audit_mode:
                        logger.info(f"Audit Mode: Passing input despite detection in {context}")
                        return content # Soft Block (Pass-through)
                    
                return result

            except concurrent.futures.TimeoutError:
                # Fail-Open Logic: Availability > Security in this config.
                log_audit(logger, "TIMEOUT", {
                    "module": context, 
                    "limit_sec": self.timeout_seconds,
                    "action": "FAIL_OPEN"
                })
                return content
                
            except Exception as e:
                # Catch internal module errors
                log_audit(logger, "INTERNAL_MODULE_ERROR", {
                    "module": context,
                    "error": str(e),
                    "action": "FAIL_OPEN"
                })
                return content

        except Exception as e:
            # The "Impossible" Catch: If the logic above (submit/logging) fails.
            # Ensures main thread never crashes.
            print(f"UPIF CRITICAL FAILURE: {e}") # Last resort print
            return content

    def _safe_scan(self, module: SecurityModule, content: Any, metadata: Optional[Dict[str, Any]]) -> Any:
        """
        Helper wrapper to run the scan inside the thread. 
        Catches exceptions within the thread to avoid crashing the executor.
        """
        try:
            return module.scan(content, metadata)
        except Exception as e:
            raise e # Propagate to future.result() to be handled by _run_fail_safe
