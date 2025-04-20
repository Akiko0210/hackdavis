import os

import google.genai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

try:
    # Read the content from sample.txt
    with open("sample.txt", "r") as file:
        content = file.read()

    # Configure the API key
    genai.configure(api_key=API_KEY)

    # Create a model instance
    model = genai.GenerativeModel("gemini-pro")

    # Create the prompt with actual content
    prompt = f"""
Read the following text and extract the main points:

{content}

Return: list[str]
"""

    # Generate content
    response = model.generate_content(prompt)

    print("Key Points Analysis:")
    print("-------------------")
    print(response.text)
except Exception as e:
    print(f"An error occurred: {str(e)}")
