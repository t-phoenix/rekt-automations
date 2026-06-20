"""Utility functions for LLM interactions."""
from typing import Any, Literal, Optional

from .llm_registry import (
    LLMSelection,
    create_llm,
    list_available_presets,
    resolve_default_preset_id,
)

TaskType = Literal["content_generation", "analysis", "general"]


def get_llm(
    task_type: TaskType = "general",
    llm_config: Optional[dict[str, Any]] = None,
    *,
    require_vision: bool = False,
):
    """
    Get an LLM instance for a task.

    Args:
        task_type: Affects temperature (creative vs analytical).
        llm_config: Request-scoped selection from state.config["llm"].
        require_vision: When True, use a vision-capable model (with fallback).
    """
    selection = LLMSelection.from_request(
        preset_id=(llm_config or {}).get("preset_id"),
        model_override=(llm_config or {}).get("model"),
    )
    return create_llm(selection, task_type, require_vision=require_vision)


def get_llm_from_state(state: dict, task_type: TaskType = "general", *, require_vision: bool = False):
    """Resolve LLM from graph state config."""
    llm_config = state.get("config", {}).get("llm")
    return get_llm(task_type, llm_config, require_vision=require_vision)


def any_llm_configured() -> bool:
    return bool(list_available_presets())
