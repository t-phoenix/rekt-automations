"""LLM provider registry — user-selectable presets, not a single hardcoded model."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal, Optional

TaskType = Literal["content_generation", "analysis", "general"]

TEMPERATURE_BY_TASK: dict[TaskType, float] = {
    "content_generation": 0.8,
    "analysis": 0.3,
    "general": 0.5,
}


@dataclass(frozen=True)
class LLMPreset:
    id: str
    label: str
    provider: str
    model: str
    description: str
    supports_vision: bool
    tier: str  # budget | balanced | premium
    vision_model: Optional[str] = None

    @property
    def effective_vision_model(self) -> str:
        return self.vision_model or self.model


# Curated presets: cheap models with strong output for meme workflows.
LLM_PRESETS: dict[str, LLMPreset] = {
    "gemini-flash": LLMPreset(
        id="gemini-flash",
        label="Gemini 2.5 Flash",
        provider="google",
        model="gemini-2.5-flash",
        description="Best value: fast, cheap, vision + JSON. Recommended default.",
        supports_vision=True,
        tier="balanced",
    ),
    "gemini-flash-lite": LLMPreset(
        id="gemini-flash-lite",
        label="Gemini 2.0 Flash Lite",
        provider="google",
        model="gemini-2.0-flash-lite",
        description="Cheapest Google option; good for high-volume text.",
        supports_vision=True,
        tier="budget",
    ),
    "groq-llama-70b": LLMPreset(
        id="groq-llama-70b",
        label="Groq Llama 3.3 70B",
        provider="groq",
        model="llama-3.3-70b-versatile",
        description="Very fast, low cost text. Vision step uses fallback model.",
        supports_vision=False,
        tier="budget",
    ),
    "groq-llama-8b": LLMPreset(
        id="groq-llama-8b",
        label="Groq Llama 3.1 8B",
        provider="groq",
        model="llama-3.1-8b-instant",
        description="Fastest/cheapest text option.",
        supports_vision=False,
        tier="budget",
    ),
    "deepseek": LLMPreset(
        id="deepseek",
        label="DeepSeek Chat",
        provider="deepseek",
        model="deepseek-chat",
        description="Strong creative writing at low cost. Vision uses fallback.",
        supports_vision=False,
        tier="balanced",
    ),
    "gpt-4o-mini": LLMPreset(
        id="gpt-4o-mini",
        label="GPT-4o Mini",
        provider="openai",
        model="gpt-4o-mini",
        description="Reliable OpenAI mini model with vision support.",
        supports_vision=True,
        tier="balanced",
    ),
    "gpt-4o": LLMPreset(
        id="gpt-4o",
        label="GPT-4o",
        provider="openai",
        model="gpt-4o",
        description="Highest quality OpenAI; higher cost.",
        supports_vision=True,
        tier="premium",
    ),
}


def _provider_env_key(provider: str) -> str:
    return {
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }[provider]


def is_provider_configured(provider: str) -> bool:
    if provider == "openrouter":
        return bool(os.getenv("OPENROUTER_API_KEY"))
    return bool(os.getenv(_provider_env_key(provider)))


def is_preset_available(preset_id: str) -> bool:
    preset = LLM_PRESETS.get(preset_id)
    if not preset:
        return False
    return is_provider_configured(preset.provider)


def list_available_presets() -> list[dict[str, Any]]:
    """Presets the server can run right now (based on configured API keys)."""
    available = []
    for preset in LLM_PRESETS.values():
        if not is_preset_available(preset.id):
            continue
        available.append(
            {
                "id": preset.id,
                "label": preset.label,
                "provider": preset.provider,
                "model": preset.model,
                "supports_vision": preset.supports_vision,
                "tier": preset.tier,
                "description": preset.description,
            }
        )
    if is_provider_configured("openrouter"):
        available.append(
            {
                "id": "openrouter",
                "label": "OpenRouter (custom model)",
                "provider": "openrouter",
                "model": None,
                "supports_vision": True,
                "tier": "balanced",
                "description": (
                    "Pass llm_model (e.g. google/gemini-2.5-flash, "
                    "meta-llama/llama-3.3-70b-instruct). One key, many models."
                ),
            }
        )
    return available


def resolve_default_preset_id() -> str:
    explicit = os.getenv("DEFAULT_LLM")
    if explicit and is_preset_available(explicit):
        return explicit

    for candidate in ("gemini-flash", "gpt-4o-mini", "groq-llama-70b", "deepseek"):
        if is_preset_available(candidate):
            return candidate

    for preset_id in LLM_PRESETS:
        if is_preset_available(preset_id):
            return preset_id

    if is_provider_configured("openrouter"):
        return "openrouter"

    raise ValueError(
        "No LLM provider configured. Set GOOGLE_API_KEY, GROQ_API_KEY, "
        "DEEPSEEK_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY."
    )


def resolve_vision_fallback_preset_id() -> str:
    explicit = os.getenv("DEFAULT_VISION_LLM")
    if explicit:
        preset = LLM_PRESETS.get(explicit)
        if preset and preset.supports_vision and is_preset_available(explicit):
            return explicit

    for candidate in ("gemini-flash", "gemini-flash-lite", "gpt-4o-mini", "gpt-4o"):
        if is_preset_available(candidate):
            preset = LLM_PRESETS[candidate]
            if preset.supports_vision:
                return candidate

    raise ValueError(
        "No vision-capable LLM configured. Set GOOGLE_API_KEY or OPENAI_API_KEY, "
        "or choose a vision preset (gemini-flash, gpt-4o-mini)."
    )


@dataclass
class LLMSelection:
    preset_id: str
    model_override: Optional[str] = None

    @classmethod
    def from_request(cls, preset_id: Optional[str], model_override: Optional[str] = None) -> LLMSelection:
        if preset_id == "openrouter":
            if not model_override:
                raise ValueError(
                    "llm_model is required when llm=openrouter "
                    "(e.g. google/gemini-2.5-flash)"
                )
            if not is_provider_configured("openrouter"):
                raise ValueError("OpenRouter is not configured on this server")
            return cls(preset_id="openrouter", model_override=model_override)

        resolved_id = preset_id or resolve_default_preset_id()

        if resolved_id not in LLM_PRESETS:
            valid = ", ".join(sorted(LLM_PRESETS.keys()) + ["openrouter"])
            raise ValueError(f"Unknown llm preset '{resolved_id}'. Valid: {valid}")

        if not is_preset_available(resolved_id):
            raise ValueError(
                f"LLM preset '{resolved_id}' is not available — "
                f"configure {_provider_env_key(LLM_PRESETS[resolved_id].provider)}"
            )

        return cls(preset_id=resolved_id, model_override=model_override)


def _build_chat_model(
    provider: str,
    model: str,
    task_type: TaskType,
):
    temperature = TEMPERATURE_BY_TASK[task_type]

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )

    if provider == "deepseek":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

    if provider == "openrouter":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature)

    raise ValueError(f"Unsupported LLM provider: {provider}")


def create_llm(selection: LLMSelection, task_type: TaskType = "general", *, require_vision: bool = False):
    """Build a LangChain chat model for the requested preset and task."""
    if selection.preset_id == "openrouter":
        model = selection.model_override or "google/gemini-2.5-flash"
        return _build_chat_model("openrouter", model, task_type)

    preset = LLM_PRESETS[selection.preset_id]

    if require_vision and not preset.supports_vision:
        fallback_id = resolve_vision_fallback_preset_id()
        fallback = LLM_PRESETS[fallback_id]
        return _build_chat_model(fallback.provider, fallback.effective_vision_model, task_type)

    model = selection.model_override or preset.model
    return _build_chat_model(preset.provider, model, task_type)


def selection_to_metadata(selection: LLMSelection, *, vision_fallback: bool = False) -> dict[str, Any]:
    if selection.preset_id == "openrouter":
        return {
            "preset": "openrouter",
            "provider": "openrouter",
            "model": selection.model_override,
            "vision_fallback": vision_fallback,
        }

    preset = LLM_PRESETS[selection.preset_id]
    model = selection.model_override or preset.model
    if vision_fallback and not preset.supports_vision:
        fallback = LLM_PRESETS[resolve_vision_fallback_preset_id()]
        model = fallback.effective_vision_model

    return {
        "preset": preset.id,
        "provider": preset.provider,
        "model": model,
        "vision_fallback": vision_fallback and not preset.supports_vision,
    }
