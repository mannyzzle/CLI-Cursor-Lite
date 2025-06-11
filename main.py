import os
import sys
from dotenv import load_dotenv
from google import genai

# Check for prompt argument
if len(sys.argv) < 2:
    print("Error: You must provide a prompt as a command line argument.")
    print("Usage: python main.py \"Your prompt here\"")
    sys.exit(1)

# Join all arguments after the script name into one prompt string
prompt = " ".join(sys.argv[1:])

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Set up Gemini client
client = genai.Client(api_key=api_key)

# Make the API call
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=prompt
)

# Output response and usage
print("\nGemini says:\n")
print(response.text)

usage = response.usage_metadata
print("\nPrompt tokens:", usage.prompt_token_count)
print("Response tokens:", usage.candidates_token_count)
