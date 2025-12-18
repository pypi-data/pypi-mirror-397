"""
Evoke Wrappers - Auto-discovery and instrumentation of model SDKs

Automatically instruments supported model providers to capture events
for detection and analysis.
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


def auto_instrument() -> List[str]:
    """
    Auto-discover and instrument all available model SDKs and frameworks.

    This function attempts to import and instrument each supported provider.
    If a provider is not installed, it silently skips it.

    Returns:
        List of successfully instrumented provider names
    """
    instrumentors = []

    # Try OpenAI
    try:
        import openai
        from evoke.wrappers.openai import EvokeOpenAIInstrumentor
        instrumentor = EvokeOpenAIInstrumentor()
        instrumentor.instrument()
        instrumentors.append("openai")
        logger.debug("Instrumented OpenAI")
    except ImportError:
        logger.debug("OpenAI SDK not installed, skipping instrumentation")
    except Exception as e:
        logger.warning(f"Failed to instrument OpenAI: {e}")

    # Try Anthropic
    try:
        import anthropic
        from evoke.wrappers.anthropic import EvokeAnthropicInstrumentor
        instrumentor = EvokeAnthropicInstrumentor()
        instrumentor.instrument()
        instrumentors.append("anthropic")
        logger.debug("Instrumented Anthropic")
    except ImportError:
        logger.debug("Anthropic SDK not installed, skipping instrumentation")
    except Exception as e:
        logger.warning(f"Failed to instrument Anthropic: {e}")

    # Try LangChain (if available)
    try:
        import langchain
        from evoke.wrappers.langchain import EvokeLangChainInstrumentor
        instrumentor = EvokeLangChainInstrumentor()
        instrumentor.instrument()
        instrumentors.append("langchain")
        logger.debug("Instrumented LangChain")
    except ImportError:
        logger.debug("LangChain not installed, skipping instrumentation")
    except Exception as e:
        logger.warning(f"Failed to instrument LangChain: {e}")

    # Try LiteLLM (universal provider - covers 100+ LLM APIs)
    try:
        import litellm
        from evoke.wrappers.litellm import EvokeLiteLLMInstrumentor
        instrumentor = EvokeLiteLLMInstrumentor()
        instrumentor.instrument()
        instrumentors.append("litellm")
        logger.debug("Instrumented LiteLLM (100+ providers)")
    except ImportError:
        logger.debug("LiteLLM not installed, skipping instrumentation")
    except Exception as e:
        logger.warning(f"Failed to instrument LiteLLM: {e}")

    return instrumentors


# Export base class for custom instrumentors
from evoke.wrappers.base import BaseInstrumentor

__all__ = [
    "auto_instrument",
    "BaseInstrumentor",
]
