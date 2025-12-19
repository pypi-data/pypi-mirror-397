# UPIF - Universal Prompt Injection Firewall
# Copyright (c) 2025 AntiGravity
# This file exposes the main public API.

__version__ = "0.1.4"

from typing import Optional

# Lazy import to avoid circular deps during setup
def _get_guard():
    from .core.coordinator import GovernanceCoordinator
    from .modules.input_protection import InputGuard
    from .modules.output_protection import OutputShield
    from .core.licensing import LicenseManager
    from .modules.neural_guard import NeuralGuard
    
    coord = GovernanceCoordinator()
    # Auto-wire the Baseline Protections with Polite Defaults
    coord.register_input_guard(InputGuard(refusal_message="I cannot process this request due to safety guidelines."))
    coord.register_output_shield(OutputShield())
    
    # Initialize Licensing
    coord.license_manager = LicenseManager()
    
    # NEURAL: Check tier and register if PRO
    # Note: In a real app, this check might happen per-request or refresh periodically.
    # For MVP, we check on startup (or default to registered but checked internally).
    # We will register it as a "Secondary" guard or chain it.
    # For simplicity: We replace the InputGuard OR Chain them.
    # Let's Chain: The Coordinator currently supports one input guard.
    # We will make NeuralGuard WRAP the InputGuard (PatternComposite) or specific Logic?
    # Simple approach: Coordinator holds a list. Only 1 for now.
    # Let's add it as a separate property for now to minimal change.
    coord.neural_guard = NeuralGuard() # It handles its own disable state
    
    return coord

# Singleton instance for easy import
# Usage: from upif import guard
guard = _get_guard()
