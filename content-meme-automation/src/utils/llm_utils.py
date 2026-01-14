"""Utility functions for LLM interactions."""
import os
from typing import Literal


def get_llm(task_type: Literal["content_generation", "analysis", "general"] = "general"):
    """
    Get LLM instance based on task type.
    
    Args:
        task_type: Type of task - affects temperature and model selection
        
    Returns:
        LLM instance
        
    Raises:
        ValueError: If no API keys are configured
    """
    # Primary: OpenAI (most compatible with LangChain)
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        if task_type == "content_generation":
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
        elif task_type == "analysis":
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        else:
            return ChatOpenAI(model="gpt-4o-mini")
    
    # Fallback: Google Gemini (v2.5-flash via native SDK)
    elif os.getenv("GOOGLE_API_KEY"):
        raise NotImplementedError(
            "Gemini integration has SDK compatibility issues. "
            "Please set OPENAI_API_KEY for now."
        )
    
    else:
       raise ValueError(
            "No LLM API keys found. Please set OPENAI_API_KEY"
        )
