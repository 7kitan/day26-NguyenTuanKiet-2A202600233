"""Shared LLM factory for all agents.

Uses OpenRouter as an OpenAI-compatible API.
"""

import os

from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI client pointed at OpenRouter."""
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
        temperature=0.3,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
