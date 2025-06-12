import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Check for prompt and optional --verbose flag
args = sys.argv[1:]

if not args:
    print("Error: You must provide a prompt as a command line argument.")
    print("Usage: python main.py \"Your prompt here\" [--verbose]")
    sys.exit(1)

# Determine if --verbose is enabled
verbose = False
if "--verbose" in args:
    verbose = True
    args.remove("--verbose")  # Remove it from args so it doesn’t pollute the prompt

# Join remaining args as the prompt
prompt = " ".join(args)

# System prompt override
system_prompt = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'

# Set up Gemini client and config
client = genai.Client(api_key=api_key)
config = types.GenerateContentConfig(system_instruction=system_prompt)

# Make the API call
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=prompt,
    config=config
)

# Print result
print("\nGemini says:\n")
print(response.text)

# Optional verbose output
if verbose:
    usage = response.usage_metadata
    print("\n[VERBOSE MODE]")
    print("User prompt:", prompt)
    print("Prompt tokens:", usage.prompt_token_count)
    print("Response tokens:", usage.candidates_token_count)
