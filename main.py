import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Working directory for all function calls
WORKING_DIR = "calculator"

# System prompt instructing multi‐step bug fixing
system_prompt = """
You are an AI coding agent with these tools:
- get_files_info(directory)
- get_file_content(file_path)
- write_file(file_path, content)
- run_python_file(file_path)

When asked to fix a bug in the code, you MUST:
1. List files (get_files_info) to locate the relevant source.
2. Read the source file (get_file_content).
3. Apply edits (write_file).
4. Test the changes (run_python_file).

Do NOT skip straight to running the file. Always inspect before you modify or execute.
All paths are relative to the working directory and will be injected automatically.
"""

# --- Tool schema declarations ---
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="List files in a directory with sizes.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"directory": types.Schema(type=types.Type.STRING)},
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"file_path": types.Schema(type=types.Type.STRING)},
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(type=types.Type.STRING),
            "content": types.Schema(type=types.Type.STRING),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a Python file and capture its output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"file_path": types.Schema(type=types.Type.STRING)},
    ),
)

tools = [types.Tool(function_declarations=[
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
])]

config = types.GenerateContentConfig(
    tools=tools,
    system_instruction=system_prompt
)

# --- Function dispatch helper ---
def call_function(call: types.FunctionCall, verbose=False):
    name = call.name
    kwargs = dict(call.args or {})

    # Inject working directory
    kwargs["working_directory"] = WORKING_DIR

    # Strip any unexpected args per function
    if name == "run_python_file":
        # run_python_file only accepts 'file_path'
        kwargs = {k: v for k, v in kwargs.items() if k in ("file_path", "working_directory")}

    elif name == "get_files_info":
        # only 'directory'
        kwargs = {k: v for k, v in kwargs.items() if k in ("directory", "working_directory")}

    elif name == "get_file_content":
        # only 'file_path'
        kwargs = {k: v for k, v in kwargs.items() if k in ("file_path", "working_directory")}

    elif name == "write_file":
        # only 'file_path' and 'content'
        kwargs = {k: v for k, v in kwargs.items() if k in ("file_path", "content", "working_directory")}

    # Print call
    if verbose:
        print(f"Calling function: {name}({kwargs})")
    else:
        print(f" - Calling function: {name}")

    # Map to actual implementations
    fn_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }
    fn = fn_map.get(name)
    if not fn:
        return types.Content(
            role="tool",
            parts=[types.Part.from_function_response(
                name=name,
                response={"error": f"Unknown function: {name}"}
            )]
        )

    result = fn(**kwargs)
    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(
            name=name,
            response={"result": result}
        )]
    )

# --- Parse CLI arguments ---
raw = sys.argv[1:]
if not raw:
    print("Usage: python main.py \"<task>\" [--verbose]")
    sys.exit(1)

verbose = "--verbose" in raw
user_input = " ".join(arg for arg in raw if arg != "--verbose")

# --- Initialize conversation ---
messages = [types.Content(role="user", parts=[types.Part(text=user_input)])]

# --- Agent loop (up to 20 steps) ---
for _ in range(20):
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=config
    )
    candidate = resp.candidates[0]
    called = False

    for part in candidate.content.parts:
        if hasattr(part, "function_call") and part.function_call:
            # Append the model’s function call
            messages.append(types.Content(role="assistant", parts=[part]))
            # Execute and append tool output
            tool_content = call_function(part.function_call, verbose=verbose)
            messages.append(tool_content)
            called = True
            break

    if not called:
        # No more function calls, this is the final answer
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                print("Final response:\n" + part.text)
        break
