"""Kryten LLM Service - AI-powered chat responses for CyTube."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("kryten-llm")
except PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "Kryten Robot Team"
__license__ = "MIT"
