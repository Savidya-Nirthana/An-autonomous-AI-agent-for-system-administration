"""
Application configuration - loads from YAML param files.

CONFIGURATION POLICY:
=====================
Configuration is loaded from config/param.yaml and config/models.yaml.
Secrets (API keys) live only in .env and are loaded via os.getenv()

Support multiple LLM providers via Openrouter unified API or direct providers:
- Openrouter (unified multiple-provider accesss)
- OpenAI (direct access)
- Anthropic (direct access)
- Google (direct access)
- Groq (direct access)
- DeepSeek (direct access)

"""


from pathlib import Path
from typing import Dict, Any, Optional
import os 
import yaml

from paths import BUNDLE_DIR, CONFIG_DIR as _CONFIG_DIR, USER_DATA_DIR


# ================================================
# YAML Config loading 
# ================================================


def _load_yaml(filename: str)-> Dict[str, Any]:
    """ Load a YAML config file """
    filepath = _CONFIG_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, 'r') as f:
        return yaml.safe_load(f) or {}

def _get_nasted(d: Dict, *keys, default=None):
    """ Get nested dictionary value safely """
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default 
    return d if d is not None else default

# Load configs
_PARAMS = _load_yaml("param.yaml")
_MODELS = _load_yaml("models.yaml")

# ===============================================
# Provider configuration
# ===============================================

PROVIDER = _get_nasted(_PARAMS, "provider", "default", default="openrouter")
MODEL_TIER = _get_nasted(_PARAMS, "provider", "tier", default="general")
OPENROUTER_BASE_URL = _get_nasted(_PARAMS, "provider", "openrouter_base_url", default="https://openrouter.ai/api/v1")

# ===============================================
# Model Names (from models.yaml)
# ===============================================

def get_chat_model(provider: Optional[str]=None, tier: Optional[str] = None) -> str:
    """ Get chat model name for specified provider and tier """
    provier = provider or PROVIDER
    tier = tier or MODEL_TIER

    if provider == "google":
        provider = "google"
    elif provider == "gemini":
        provider = "google"
    
    return _get_nasted(_MODELS, provider, "chat", tier, default="google/gemini-2.5-flash")


EMBEDDING_TIER = _get_nasted(_PARAMS, "embedding", "tier", default="default")

def get_embedding_model(provider: Optional[str] = None, tier: Optional[str] = None) -> str:
    """ Get embedding model name for specified provider and tier. """
    provider = provider or PROVIDER
    tier = tier or EMBEDDING_TIER

    # Handle provider name mapping 
    if provider == "google" or provider == "gemini":
        provider = "google"
    
    return _get_nasted(_MODELS, provider, "embedding", tier, default="google/gemini-embedding-001")


ROUTER_MODEL = "llama-3.1-8b-instant"
ROUTER_PROVIDER = "groq"

EXTRACTOR_MODEL = ""
EXTRACTOR_PROVIDER = ""

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

CHAT_MODEL = "google/gemini-2.5-flash"
CHAT_PROVIDER = "openrouter"

EMBEDDING_MODEL = get_embedding_model()

OPENAI_CHAT_MODEL = CHAT_MODEL

EMBEDDING_DIM = 1536  # Default for text-embedding-3-small

# Auto-detect dimension from model name
if "large" in EMBEDDING_MODEL.lower():
    EMBEDDING_DIM = 3072
elif "small" in EMBEDDING_MODEL.lower() or "ada" in EMBEDDING_MODEL.lower():
    EMBEDDING_DIM = 1536

# =======================================
# LLM Parameters
# =======================================

LLM_TEMPERATURE = _get_nasted(_PARAMS, "llm", "temperature", default=0.0)
LLM_MAX_TOKENS = _get_nasted(_PARAMS, "llm", "max_tokens", default=2000)
LLM_STREAMING = _get_nasted(_PARAMS, "llm", "streaming", default=False)

# =======================================
# Retrieval Parameters
# =======================================

TOP_K_RESULTS = _get_nasted(_PARAMS, "retrieval", "top_k", default=5)
SIMILARITY_THRESHOLD = _get_nasted(_PARAMS, "retrieval", "similarity_threshold", default=0.7)

 
# ========================================
# Helper Functions
# ========================================

def get_api_key(provider: Optional[str] = None) -> Optional[str]:
    """Get API key for the specified provider."""
    provider = provider or PROVIDER
    key_map = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "gemini": "GOOGLE_API_KEY",  # Alias
        "groq": "GROQ_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "tavily": "TAVILY_API_KEY",
    }
    env_var = key_map.get(provider, f"{provider.upper()}_API_KEY")
    return os.getenv(env_var)

def validate() -> None:
    """
    Validate configuration and create required directories.

    Raises:
        ValueError: If required secrets are missing
    """
    # Check required secrets based on provider
    api_key = get_api_key()
    if not api_key:
        key_name = "OPENROUTER_API_KEY" if PROVIDER == "openrouter" else f"{PROVIDER.upper()}_API_KEY"
        raise ValueError(
            f"❌ Missing required secret: {key_name}\n"
            f"Please add it to your .env file."
        )


def get_all_models() -> Dict[str, Any]:
    """Return all available models from models.yaml."""
    return _MODELS


def get_config() -> Dict[str, Any]:
    """Return full config dictionary."""
    return _PARAMS

