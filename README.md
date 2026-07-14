[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

# AI Agents in Python

## Description
A small multi-agent pipeline that turns a single programming **topic** into a
beginner-friendly Markdown **study guide**. Three specialised agents run in
sequence — one explains the topic, one designs a practice exercise, and one
reviews the draft — and the result is validated and saved to disk.

The agents are built with **Google ADK** (`google-adk`) and run against a
**local model served by Ollama**, reached through **LiteLLM**. No cloud API
keys are required.

**Pipeline:** `topic → explainer → practice designer → reviewer → validate → save`

## Requirements
- **Python 3.10+** (developed and tested on 3.12)
- **[Ollama](https://ollama.com/)** installed and running locally (default
  `http://localhost:11434`)
- The Ollama model referenced by the agents: **`gemma4`**
- Python dependencies (see `requirements.txt`):
  - `google-adk==2.4.0` — agent framework / runner
  - `litellm==1.92.0` — routes model calls to Ollama
  - `google-genai==2.11.0` — `Content`/`Part` message types
  - `orjson==3.11.9` — required by LiteLLM's tool path (agent crashes without it)

## Setup
1. **Clone and enter the project:**
   ```bash
   git clone https://github.com/yourusername/ai-agents-intro.git
   cd ai-agents-intro
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install and start Ollama, then pull the model:**
   ```bash
   ollama serve                    # if not already running
   ollama pull gemma4              # must match the model in agents/*.py
   ```

## Configuration
This project uses a **local** model, so there are no secret API keys to set.
Configuration lives in the agent definitions themselves:

- The model is set in each file under `agents/` as
  `LiteLlm(model="ollama_chat/gemma4")`. To use a different Ollama model,
  change that string in all three agent files and `ollama pull` the new model.
- To point at a non-default Ollama host, pass `api_base` to `LiteLlm`, e.g.
  `LiteLlm(model="ollama_chat/gemma4", api_base="http://localhost:11434")`.

> A `.env.example` file is present but the application does not currently load
> a `.env` — no environment variables are required to run it.

## How to Run
Pass the topic as a command-line argument:
```bash
python3 main.py "recursion"
```
The generated guide is written to **`output/study_guide.md`** (the `output/`
directory is created automatically).

On failure the program prints a single `Error: ...` line to **stderr** and
exits with status **1** — for example, if Ollama isn't running you'll see a
clear "Could not reach the model" message instead of a raw traceback.

## Example Input
A single topic string:
```bash
python3 main.py "recursion"
python3 main.py "python lists"
python3 main.py "big-O notation"
```

## Example Output
A Markdown file (`output/study_guide.md`) with a fixed structure:

```markdown
# Topic: recursion

## Simple Explanation
Recursion is when a function calls itself to solve a smaller version of...

## Key Concepts
- Base case
- Recursive case
...

## Example
def factorial(n):
    ...

## Common Mistakes
- Forgetting the base case (infinite recursion)
...

## Practice Exercise
Write a function that sums a list of numbers using recursion.
Input: [1, 2, 3]  ->  Output: 6
Hint: think about the base case for an empty list.

## Review Comments
The explanation is clear; consider adding a note on stack depth limits.

## Final Summary
This study guide walked through a beginner-friendly explanation of the topic...
```

## Project Structure
```
ai-agents-intro/
├── main.py                          # Orchestrates the pipeline and error handling
├── agents/
│   ├── explainer_agent.py           # Explains the topic for a beginner
│   ├── practice_designer_agent.py   # Designs a practice exercise
│   └── reviewer_agent.py            # Reviews the assembled draft
├── tools/
│   ├── file_writer.py               # save_markdown_file(): writes the guide to disk
│   └── validation.py                # validate_required_sections(): checks headings
├── data/
│   └── topic_examples.json          # Placeholder for example topics
├── output/                          # Generated study guides (created at runtime)
├── requirements.txt
├── .env.example
└── README.md
```

## Agents
| Agent | File | Role |
| --- | --- | --- |
| **Explainer** | `agents/explainer_agent.py` | Produces the beginner explanation using four fixed headings: *Simple Explanation, Key Concepts, Example, Common Mistakes*. |
| **Practice Designer** | `agents/practice_designer_agent.py` | Creates one short beginner exercise (with expected input/output and hints) from the topic and explanation — without rewriting the explanation. |
| **Reviewer** | `agents/reviewer_agent.py` | Reviews the assembled draft for clarity and completeness and returns short, actionable suggestions — without rewriting the guide. |

Each agent is a `google.adk.agents.Agent` with its own `instruction`, driven by
`InMemoryRunner` in `run_agent()` (`main.py`).

## Tools
These are plain Python helpers the orchestration in `main.py` calls directly
(they support the pipeline rather than being invoked by the agents):

| Tool | File | Role |
| --- | --- | --- |
| **`save_markdown_file(path, content)`** | `tools/file_writer.py` | Creates the parent directory if needed and writes the final Markdown to disk. |
| **`validate_required_sections(content)`** | `tools/validation.py` | Checks the assembled guide for all required section headings and returns `{"passed": bool, "missing": [...]}`. |

## Self-Validation Checklist
Use this to confirm a run is healthy:

- [ ] Ollama is running and `ollama list` shows the `gemma4` model
- [ ] `python3 main.py "recursion"` completes with no error output
- [ ] `output/study_guide.md` exists and is non-empty
- [ ] The guide contains every required section: `Topic`, `Simple Explanation`,
      `Key Concepts`, `Example`, `Practice Exercise`, `Common Mistakes`,
      `Review Comments`, `Final Summary`
- [ ] Running with no topic (`python3 main.py`) reports the empty-topic error
- [ ] With Ollama stopped, the program prints a clean "Could not reach the
      model" message and exits non-zero (no raw traceback)

## Reflection

**What is the difference between a direct LLM call and an AI agent?**
A direct LLM call is a single, stateless request/response: you send a prompt and
get one block of text back. An AI agent wraps the model in a runtime (here Google
ADK's `Runner`) that gives it a persistent role/instruction, a session, an event
loop, and the ability to use tools and take multiple steps. In this project each
agent has a specialised job and is invoked through the runner rather than as a
one-off completion, which is what lets us chain them into a pipeline.

**What role does each agent have in your system?**
The **explainer** produces the core beginner explanation in a fixed section
format; the **practice designer** turns that explanation into a hands-on
exercise; the **reviewer** critiques the assembled draft and suggests
improvements. Each stage consumes the previous stage's output.

**What role does each tool have in your system?**
`validate_required_sections` acts as a quality gate — it confirms the final guide
contains every required heading and reports what's missing, so a malformed guide
is caught instead of saved. `save_markdown_file` persists the finished guide to
`output/`, creating the directory as needed.

**What was the most difficult part of the project?**
Wiring the local model stack together reliably — getting ADK to talk to Ollama
through LiteLLM, and hitting non-obvious dependency requirements (LiteLLM's tool
path crashes without `orjson`). Beyond setup, handling errors around the async
event stream took care: mapping the exceptions LiteLLM raises (which surface as
`openai.*` classes) to clean, contextual messages, and deciding where to catch
them so a failed agent stops the pipeline instead of feeding an empty string into
the next stage.

**What limitation did you observe when using your selected model?**
The local `gemma4` model is slower than a hosted model and does not follow
formatting instructions perfectly — it occasionally omits or renames a required
section, which is exactly why the validation step exists. Output quality and
structure are less consistent than a larger cloud model would produce.

## Known Limitations
- **Local model dependency:** requires Ollama running with the `gemma4` model;
  there is no cloud fallback.
- **Inconsistent structure:** the model may skip or rename required sections,
  causing validation to fail on some runs.
- **Fixed model per agent:** the model name is hard-coded in each agent file and
  must be changed in three places.
- **Empty-topic check runs at import time:** calling `python3 main.py` with no
  argument raises before the entry-point handler, so it prints a traceback
  rather than a clean message.
- **Tools are not agent-invoked:** validation and file writing are called by the
  orchestration code, not exposed to the agents as callable tools.
- **No automated tests** and **`data/topic_examples.json` is currently empty.**

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
