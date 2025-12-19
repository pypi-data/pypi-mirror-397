"""Gradio components for PraisonAI multi-agent framework."""

from gradio_praisonai.client import PraisonAIClient
from gradio_praisonai.interface import create_chat_interface

__all__ = ["PraisonAIClient", "create_chat_interface"]
__version__ = "0.1.0"
