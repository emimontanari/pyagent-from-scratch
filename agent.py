import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


SYSTEM_PROMPT = """You are a coding agent running in the user's terminal.
You can list files, read files, and write files, and run shell comands.
Use your tools to complete the user's task, then briefly explain what you did.
The working directory is the folder the user lauched you from.
"""


def list_files(path="."):
    entries = []
    for entry in os.scandir(path):
        entries.append(entry.name + ("/" if entry.is_dir() else ""))
    return "\n".join(sorted(entries)) or "(empty directory)"


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved content to {path}. ({len(content)} characters)"


def run_command(command):
    answer = input(f" Run '{command}'? (y/n): ")
    if answer.strip().lower() != "y":
        return "The user declined to run this command."
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True, timeout=120)

    output = (result.stdout + result.stderr).strip() or "(no output)"

    return f"Command exited with code {result.returncode}.\nOutput:\n{output}"


TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files and folders in a directory. Folders end with '/'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory to list. Optional; defaults to '.' (the current directory).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file and return its full contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to read.",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if needed and overwrites (replaces) any existing content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The full text content to write to the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command in the working directory and return its exit code and output. The user must approve the command before it runs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run.",
                    },
                },
                "required": ["command"],
            },
        },
    },
]


def run_tools(tool_call):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    print(f"Model wants to run: {name} with args: {args}")
    try:
        return str(TOOLS[name](**args))
    except Exception as e:
        return f"Error running {name}: {e}"


def run_agent(messages):
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOL_SCHEMAS,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            result = run_tools(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Welcome to the coding agent. Type your request below.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Exiting the coding agent.")
            break
        messages.append({"role": "user", "content": user_input})
        response = run_agent(messages)
        print(f"Agent: {response}")


if __name__ == "__main__":
    main()
