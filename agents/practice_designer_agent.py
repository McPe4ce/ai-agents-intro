#!/usr/bin/python3

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


designer_agent = Agent(
    name="designer_agent",
    model=LiteLlm(model="ollama_chat/gemma4"),
    description="You are a practice designer agent.",
    instruction=(
        "Create a short beginner-friendly exercise based on the topic and "
        "explanation provided. Do not rewrite the full explanation. "
        "Return only the exercise, expected input/output when relevant, "
        "and one or two hints."
    ),
)
