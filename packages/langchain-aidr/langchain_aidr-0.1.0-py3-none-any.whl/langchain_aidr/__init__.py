from importlib import metadata

from langchain_aidr.document_transformers.aidr_text_guard import CrowdStrikeGuardTransformer
from langchain_aidr.tools.ai_guard import CrowdStrikeAIGuard

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = ""
del metadata

__all__ = (
    "CrowdStrikeGuardTransformer",
    "CrowdStrikeAIGuard",
    "__version__",
)
