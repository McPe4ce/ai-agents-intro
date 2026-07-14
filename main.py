#!/usr/bin/python3
import asyncio
import sys

import openai  # LiteLLM maps model errors onto openai.* exception classes

from google.adk.runners import InMemoryRunner
from google.genai import types
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections

from agents.explainer_agent import explainer_agent
from agents.practice_designer_agent import designer_agent
from agents.reviewer_agent import reviewer_agent


APP_NAME = "ai-agents-intro"
USER_ID = "student"

if len(sys.argv) > 1:
    topic = sys.argv[1]
else:
    raise ValueError("Topic cant be empty")


async def run_agent(agent, prompt:str) -> str:
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    if runner is None:
        raise ValueError("Cant run the agent")
    
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    if session is None:
        raise ValueError("Session failed to create")
    
    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    collected = ""

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        collected += part.text
    except openai.APIConnectionError as err:
        # Ollama unreachable: server down, wrong port, or a timeout.
        # This is the failure you'll hit most often in practice.
        raise RuntimeError(
            f"Could not reach the model for agent '{agent.name}'. "
            f"Is Ollama running? Details: {err}"
        ) from err
    except openai.APIError as err:
        # Everything else the model layer can raise (bad request, missing
        # model / 404, rate limit, 5xx). openai.APIError is the shared base
        # for all litellm/openai errors, so this one clause catches the rest.
        raise RuntimeError(
            f"The model call failed for agent '{agent.name}': {err}"
        ) from err

    # No exception, but the model produced no text. Fail here so an empty
    # string doesn't silently flow into the next agent's prompt.
    if not collected:
        raise RuntimeError(f"Agent '{agent.name}' returned no text.")

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

    # validate_required_sections returns {"passed": bool, "missing": [...]}.
    # Actually react to it instead of discarding the result.
    result = validate_required_sections(final_md)              # no await
    if not result["passed"]:
        raise RuntimeError(
            "Study guide is missing required sections: "
            + ", ".join(result["missing"])
        )

    # The tool creates output/ for us, but the write itself can still fail
    # (permissions, disk full). OSError covers those file-system errors.
    try:
        save_markdown_file("output/study_guide.md", final_md)
    except OSError as err:
        raise RuntimeError(f"Could not save the study guide: {err}") from err


if __name__ == "__main__":
    # Every failure above is raised as RuntimeError, so we catch it here,
    # print one clean line, and exit non-zero — no raw traceback for the user.
    try:
        asyncio.run(main())
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
