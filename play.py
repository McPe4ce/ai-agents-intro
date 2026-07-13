#!/usr/bin/python3
import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.adk.agents import SequentialAgent
from google.genai import types

from agents.explainer_agent import explainer_agent
from agents.practice_designer_agent import designer_agent
from agents.reviewer_agent import reviewer_agent

APP_NAME = "ai-agents-intro"
USER_ID = "student"

pipeline = SequentialAgent(
    name= "explain_then_design",
    sub_agents= [explainer_agent, designer_agent, reviewer_agent]
)


async def explain(runner, topic):
    """Send one topic to the agent and print its explanation."""
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text=f"Explain briefly {topic} to a beginner, then save it to output/{topic}.md using your tool.")],

    )

    print(f"\n{'=' * 60}\nTOPIC: {topic}\n{'=' * 60}")
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="")
    print()


async def main(topics):
    runner = InMemoryRunner(agent=pipeline, app_name=APP_NAME)
    for topic in topics:
        await explain(runner, topic)


if __name__ == "__main__":
    # Use topics from the command line, or fall back to two test topics.
    args = sys.argv[1:]
    topics = args if args else ["SQL"]
    asyncio.run(main(topics))
