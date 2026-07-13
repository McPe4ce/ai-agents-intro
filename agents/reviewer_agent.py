#!/usr/bin/python3

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

reviewer_agent = Agent(
    name="reviewer_agent",
    model=LiteLlm("ollama_chat/gemma4"),
    description="You are a reviewer agent.",
    instruction=(
        "Review the draft study guide for clarity, completeness, and usefulness. "
        "Identify missing or unclear parts. "
        "Provide short, actionable suggestions. "
        "Do not rewrite the entire guide."
    ),
)
