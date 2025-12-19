"""FastAPI integration for PraisonAI multi-agent framework."""

from fastapi_praisonai.client import PraisonAIClient
from fastapi_praisonai.router import create_router

__all__ = ["PraisonAIClient", "create_router"]
__version__ = "0.1.0"
