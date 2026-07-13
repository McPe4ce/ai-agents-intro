from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections

explainer_agent = Agent(
    name="explainer_agent",
    model=LiteLlm(model="ollama_chat/gemma4"),
    instruction="Explain programming topics clearly for beginner students."
                "When the user asks you to save the explanation, call the "
                "save_markdown_file tool, passing the full markdown text as "
                "'content' and a filename ending in '.md' as 'file_path'." \
                "When you are done with that, use the validate_required_sections tool" \
                ,

    tools =[
        save_markdown_file,
        validate_required_sections
    ]
    )