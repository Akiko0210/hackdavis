import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


class Project(BaseModel):
    project_name: str
    main_points: list[str]
    type


client = genai.Client(api_key=API_KEY)

with open("sample.txt", "r") as file:
    content = file.read()

prompt = f"""
Read the following prject descriptions and extract the main points in simple words:

{content}
"""

# print(prompt)
# Cook city

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Project],
    },
)
print(response.text)
