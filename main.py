#!/usr/bin/python3
import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections

from agents.explainer_agent import explainer_agent
from agents.practice_designer_agent import designer_agent
from agents.reviewer_agent import reviewer_agent

APP_NAME = "ai-agents-intro"
USER_ID = "student"
topic = sys.argv[1] if len(sys.argv) > 1 else "SQL"


async def run_agent(agent, prompt:str) -> str:
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    collected = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    collected += part.text
    return collected


async def run_explainer_agent(topic) -> str:
    prompt = f"Explain {topic} to a beginner."
    return await run_agent(explainer_agent, prompt)

async def run_practice_designer_agent(topic, explanation) -> str:
    prompt = f"Topic: {topic}\n\nExplanation:\n{explanation}\n\nCreate a beginner practice exercise based on this."
    return await run_agent(designer_agent, prompt)

async def run_reviewer_agent(draft) -> str:
    prompt = f"Review this study guide draft:\n\n{draft}"
    return await run_agent(reviewer_agent, prompt)


def assemble_markdown(topic, explanation, practice) -> str:
    return f"""# Topic: {topic}

{explanation}

## Practice Exercise
{practice}
"""

def assemble_final_markdown(draft, review) -> str:
    return f"""{draft}

## Review Comments
{review}

## Final Summary
This study guide walked through a beginner-friendly explanation of the topic, a
hands-on practice exercise, and reviewer feedback. Revisit the practice exercise
and the reviewer's suggestions to reinforce what you learned.
"""

async def main():
    explanation = await run_explainer_agent(topic)
    practice    = await run_practice_designer_agent(topic, explanation)
    draft       = assemble_markdown(topic, explanation, practice)   # no await — pure Python
    review      = await run_reviewer_agent(draft)
    final_md    = assemble_final_markdown(draft, review)
    result      = validate_required_sections(final_md)              # no await
    save_markdown_file("output/study_guide.md", final_md)


if __name__ == "__main__":
    asyncio.run(main())
