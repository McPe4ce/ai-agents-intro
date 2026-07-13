#!/usr/bin/python3

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

explainer_agent = Agent(
    name="explainer_agent",
    model=LiteLlm(model="ollama_chat/gemma4"),
    instruction=(
        "Explain the given programming topic clearly for a beginner student. "
        "Structure your answer using exactly these markdown section headings, "
        "in this order:\n"
        "## Simple Explanation\n"
        "## Key Concepts\n"
        "## Example\n"
        "## Common Mistakes\n"
        "Write beginner-friendly content under each heading. "
        "Do not add any other top-level (#) headings."
    ),
)
