import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Check if API key exists
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Test the AI
response = client.responses.create(
    model="gpt-5.6",
    input="Explain what financial reconciliation means in one simple sentence."
)

print("\nLedgerLens AI:")
print(response.output_text)