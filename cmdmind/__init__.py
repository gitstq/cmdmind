"""
CmdMind - AI-Powered Terminal Command Intelligence
Smart command history management with semantic search
"""

__version__ = "1.0.0"
__author__ = "CmdMind Team"
__license__ = "MIT"

from cmdmind.core.database import CommandDatabase
from cmdmind.core.classifier import CommandClassifier
from cmdmind.core.searcher import CommandSearcher

__all__ = [
    "CommandDatabase",
    "CommandClassifier", 
    "CommandSearcher",
    "__version__",
]
