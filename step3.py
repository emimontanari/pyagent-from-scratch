import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {e}"


def write_file(path, content):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {path} written successfully."
    except Exception as e:
        return f"Error writing file {path}: {e}"


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
                "name": "read_file",
                "description": "Reads the content of a file and returns it as a string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read."
                        }
                    },
                    "required": ["path"]
                }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file, replacing its current content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                           "type": "string",
                           "description": "The path to the file to write."
                    },
                    "content": {
                        "type": "string",
                        "description": "The text to write into the file."
                    }
                },
                "required": ["path", "content"]
            }
        }
    }
]

user_input = input("You: ")

messages = [
    {"role": "system", "content": "You are a helpful assistant that can read and write files."},
    {"role": "user", "content": user_input},
]

TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
}

while True:
    reponse = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_SCHEMAS,
    )
    message = reponse.choices[0].message
    messages.append(message)

    if not message.tool_calls:
        print(message.content)
        break

    for tool_call in message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        print(f"Model wants to run : {tool_call.function.name} with args: {args}"
              )

        result = TOOLS[name](**args)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })
