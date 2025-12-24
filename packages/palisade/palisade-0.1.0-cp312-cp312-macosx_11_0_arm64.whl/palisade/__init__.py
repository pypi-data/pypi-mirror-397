"""Palisade - Comprehensive LLM Security Scanner.

A zero-trust security scanner for machine learning models and their artifacts.
Provides 7 critical security validators to protect against threats in the ML supply chain.
"""

__version__ = "0.1.0"
__author__ = "Sharath Rajasekar"
__email__ = "sharath@highflame.com"

# Optional imports - only import what's needed to avoid dependency issues
try:
    from .models.metadata import ModelMetadata, ModelType
except ImportError:
    # Graceful fallback if dependencies are missing
    ModelMetadata = None
    ModelType = None

# Don't import Scanner by default to avoid dependency chain

__all__ = ["ModelMetadata", "ModelType"]
