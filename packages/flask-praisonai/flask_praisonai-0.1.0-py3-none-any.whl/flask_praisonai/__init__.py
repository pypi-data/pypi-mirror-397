"""Flask integration for PraisonAI multi-agent framework."""

from flask_praisonai.client import PraisonAIClient
from flask_praisonai.blueprint import create_blueprint

__all__ = ["PraisonAIClient", "create_blueprint"]
__version__ = "0.1.0"
