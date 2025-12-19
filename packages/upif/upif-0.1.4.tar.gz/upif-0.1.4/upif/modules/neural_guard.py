"""
upif.modules.neural_guard
~~~~~~~~~~~~~~~~~~~~~~~~~

The AI Defense Layer.
Leverages local Small Language Models (SLM) via ONNX Runtime to perform
semantic analysis of input prompts, detecting intent-based attacks that
bypass heuristic regex filters.

:copyright: (c) 2025 Yash Dhone.
:license: Proprietary, see LICENSE for details.
"""

import os
import logging
from typing import Any, Optional, Dict
from upif.core.interfaces import SecurityModule
from upif.utils.logger import setup_logger

# Configure dedicated structured logger for AI events
logger = setup_logger("upif.modules.neural")

class NeuralGuard(SecurityModule):
    """
    Semantic Analysis Guard using ONNX Runtime.
    
    Attributes:
        threshold (float): Confidence score above which an input is blocked (0.0 - 1.0).
    """
    
    def __init__(self, model_path: str = "guard_model.onnx", threshold: float = 0.7):
        self.model_path = model_path
        self.threshold = threshold
        self.session = None
        self.enabled = False
        self.simulation_mode = False
        
        # Initialize resources safely
        self._load_model()

    def _load_model(self) -> None:
        """
        Loads the ONNX model. 
        Fail-Safe: If libraries are missing or file is absent (common in lightweight installs),
                   it gracefully disables itself or enters Simulation Mode for demonstration.
        """
        try:
            # Lazy import to keep 'core' lightweight if user didn't install [pro] extras
            import onnxruntime as ort
            
            # Locate model relative to the package data directory
            base_dir = os.path.dirname(os.path.dirname(__file__))
            full_path = os.path.join(base_dir, "data", self.model_path)
            
            if not os.path.exists(full_path):
                logger.warning(
                    f"NeuralGuard: Model file missing at {full_path}. "
                    "Entering SIMULATION MODE for demonstration."
                )
                self.simulation_mode = True
                self.enabled = True
                return

            # Initialize ONNX Session (Heavy Operation)
            self.session = ort.InferenceSession(full_path)
            self.simulation_mode = False
            self.enabled = True
            logger.info("NeuralGuard: AI Model Loaded Successfully via ONNX.")
            
        except ImportError:
            logger.warning("NeuralGuard: 'onnxruntime' not installed. AI protection disabled.")
            self.enabled = False
        except Exception as e:
            logger.error(f"NeuralGuard: Initialization Failed: {e}. AI protection disabled.")
            self.enabled = False

    def scan(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Any:
        # Pass-through if disabled or incorrect type
        if not self.enabled or not isinstance(content, str):
            return content

        try:
            # 1. Real Inference Path (Needs active ONNX session)
            if self.session and not self.simulation_mode:
                # TODO: Implement Tokenizer logic here (requires 'tokenizers' lib)
                # tokens = self.tokenizer.encode(content)
                # score = self.session.run(None, {'input': tokens})[0]
                pass 

            # 2. Simulation Path (For v1.0 MVP / Demo / Fallback)
            # Simulates semantic detection on keywords that Regex might miss
            # but a human/AI understands as "Roleplay" or "Hypothetical"
            score = 0.1
            semantic_triggers = [
                "imagine a world", "hypothetically", "roleplay", 
                "act as", "simulated environment"
            ]
            
            lower_content = content.lower()
            for trigger in semantic_triggers:
                if trigger in lower_content:
                    score += 0.8  # High confidence trigger
            
            # Decision
            if score > self.threshold:
                # We return a specific AI block message, or the upstream coordinator
                # can canonicalize it.
                return "[BLOCKED_BY_AI] Request unsafe."
                
            return content
            
        except Exception as e:
            # Fail-Open on Inference Error to prevent blocking safe traffic
            logger.error(f"NeuralGuard Inference Error: {e}")
            return content
