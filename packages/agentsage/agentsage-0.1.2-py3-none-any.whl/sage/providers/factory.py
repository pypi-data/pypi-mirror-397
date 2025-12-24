"""Model factory for creating LangChain chat models."""

from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel


class ModelFactory:
    """
    Factory for creating LangChain chat models from various providers.

    Supports automatic provider detection from model names.

    Example:
        >>> llm = ModelFactory.create("gpt-4o")
        >>> llm = ModelFactory.create("claude-3-opus-20240229")
        >>> llm = ModelFactory.create("llama2:latest", provider="ollama")
    """

    PROVIDERS = {
        "openai": ("langchain_openai", "ChatOpenAI"),
        "anthropic": ("langchain_anthropic", "ChatAnthropic"),
        "google": ("langchain_google_genai", "ChatGoogleGenerativeAI"),
        "ollama": ("langchain_ollama", "ChatOllama"),
        "azure": ("langchain_openai", "AzureChatOpenAI"),
        "bedrock": ("langchain_aws", "ChatBedrock"),
    }

    @classmethod
    def create(
        cls,
        model: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> BaseChatModel:
        """
        Create a chat model instance.

        Args:
            model: Model identifier (e.g., "gpt-4o", "claude-3-opus").
            provider: Provider name. Auto-detected if not specified.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens per completion.
            **kwargs: Additional provider-specific arguments.

        Returns:
            Configured LangChain chat model.

        Raises:
            ValueError: If provider is unknown or required package not installed.
        """
        provider = provider or cls._detect_provider(model)

        if provider not in cls.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available: {', '.join(cls.PROVIDERS.keys())}"
            )

        module_name, class_name = cls.PROVIDERS[provider]

        try:
            module = __import__(module_name, fromlist=[class_name])
            model_class = getattr(module, class_name)
        except ImportError as e:
            raise ValueError(
                f"Provider '{provider}' requires package '{module_name}'. "
                f"Install with: pip install {module_name}"
            ) from e

        model_kwargs = cls._build_kwargs(provider, model, temperature, max_tokens, **kwargs)
        return model_class(**model_kwargs)

    @classmethod
    def _detect_provider(cls, model: str) -> str:
        """Detect provider from model name."""
        model_lower = model.lower()

        if any(model_lower.startswith(p) for p in ("gpt-", "o1", "o3", "davinci")):
            return "openai"
        if model_lower.startswith("claude"):
            return "anthropic"
        if model_lower.startswith(("gemini", "palm")):
            return "google"
        if ":" in model_lower:
            return "ollama"
        if model_lower.startswith("azure/"):
            return "azure"

        return "openai"

    @classmethod
    def _build_kwargs(
        cls,
        provider: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build provider-specific kwargs."""
        base: Dict[str, Any] = {"temperature": temperature}

        if provider == "openai":
            base.update({"model": model, "max_tokens": max_tokens})
        elif provider == "anthropic":
            base.update({"model": model, "max_tokens": max_tokens})
        elif provider == "google":
            base.update({"model": model, "max_output_tokens": max_tokens})
        elif provider == "ollama":
            base.update({"model": model, "num_predict": max_tokens})
        elif provider == "azure":
            base.update({"deployment_name": model.replace("azure/", ""), "max_tokens": max_tokens})
        elif provider == "bedrock":
            base.update({"model_id": model, "model_kwargs": {"max_tokens": max_tokens}})
        else:
            base.update({"model": model, "max_tokens": max_tokens})

        base.update(kwargs)
        return base

    @classmethod
    def list_providers(cls) -> List[str]:
        """Return list of available provider names."""
        return list(cls.PROVIDERS.keys())


def create_model(
    model: str,
    provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Create a chat model (convenience function).

    Args:
        model: Model identifier.
        provider: Provider name (auto-detected if not specified).
        temperature: Sampling temperature.
        max_tokens: Maximum tokens.
        **kwargs: Additional arguments.

    Returns:
        Configured LangChain chat model.
    """
    return ModelFactory.create(
        model=model,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
