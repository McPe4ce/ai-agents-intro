from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

explainer_agent = Agent(
    name="explainer_agent",
    model=LiteLlm(model="ollama_chat/gemma4"),
    instruction="Explain programming topics clearly for beginner students."
    )