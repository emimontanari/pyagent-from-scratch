# pyagent-from-scratch

A minimal AI coding agent in pure Python: an LLM tool-calling loop that can list, read, and write files and run shell commands.

## How it works

1. You type a request; it is sent to the model (`gpt-4o-mini`) along with the tool schemas.
2. If the model wants a tool, it replies with a tool call (name + JSON arguments).
3. Python runs the matching function and sends the result back as a `tool` message with the same `tool_call_id`.
4. The loop repeats until the model answers with plain text, which is printed.

## Tools

| Tool | What it does |
| --- | --- |
| `list_files` | Lists files and folders in a directory (folders end with `/`). |
| `read_file` | Returns the contents of a text file. |
| `write_file` | Writes content to a file. **Overwrites existing files without asking.** |
| `run_command` | Runs a shell command and returns its exit code and output. **Asks for `y/n` approval first.** |

## Project structure

The project is built up in steps:

- `step1.py` – a single chat completion call.
- `step2.py` – a chat loop that keeps conversation history.
- `step3.py` – tool calling with `read_file` and `write_file`.
- `agent.py` – the final agent: all four tools, an error-handling tool runner, and an interactive loop.

## Requirements

- Python 3.15 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- An OpenAI API key

## Quick start

```bash
uv sync
```

Create a `.env` file in the project root containing this single line (replace the value with your OpenAI API key):

```
OPENAI_API_KEY=your-api-key-here
```

Then run the agent:

```bash
uv run agent.py
```

Type `exit` (or `quit`) to leave.

## Example prompt

```
You: Create a simple Snake game in snake_game/index.html
```

The agent will write the file and may ask permission to run commands (for example, to open it).

## Safety

The agent runs real shell commands and writes files in the directory you launch it from. Review every command before approving it, and never commit your `.env` file.
