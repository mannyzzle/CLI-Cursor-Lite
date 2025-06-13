import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Hardcoded working directory
WORKING_DIR = "calculator"

# System prompt
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls — it will be injected automatically.
"""

# Function Declarations
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="List files in a directory and their sizes.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory to list, relative to working dir."
            )
        }
    )
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read contents of a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Relative path to the file to read."
            )
        }
    )
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a Python file with optional args.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Python file to run, relative to working dir."
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional arguments to pass",
                items=types.Schema(type=types.Type.STRING)
            )
        }
    )
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write content to a file, creating or overwriting it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to write file to, relative to working dir."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Text content to write."
            )
        }
    )
)

# Tool list
tools = [types.Tool(function_declarations=[
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file
])]

# Config
config = types.GenerateContentConfig(
    tools=tools,
    system_instruction=system_prompt
)

# Prompt input
args = sys.argv[1:]
if not args:
    print("Error: Provide a prompt.")
    sys.exit(1)

user_prompt = " ".join(args)

# Format message
messages = [
    types.Content(
        role="user",
        parts=[types.Part(text=user_prompt)]
    )
]

# Call Gemini
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=config
)

# Parse response
if response.candidates:
    candidate = response.candidates[0]
    for part in candidate.content.parts:
        if hasattr(part, "function_call") and part.function_call:
            fn = part.function_call
            print(f"\nCalling function: {fn.name}({fn.args})")

            if fn.name == "get_files_info":
                output = get_files_info(WORKING_DIR, **fn.args)
            elif fn.name == "get_file_content":
                output = get_file_content(WORKING_DIR, **fn.args)
            elif fn.name == "run_python_file":
                output = run_python_file(WORKING_DIR, **fn.args)
            elif fn.name == "write_file":
                output = write_file(WORKING_DIR, **fn.args)
            else:
                output = f"Unknown function: {fn.name}"

            print("\nFunction Output:\n" + output)

        elif hasattr(part, "text") and part.text:
            print("\nResponse:\n" + part.text)
else:
    print("No response.")
