import json
from typing import List
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

class Project(BaseModel):
    title: str
    summary: str
    features: List[str]

def process_hackathons():
    """Process all hackathons and their projects."""
    # Read hackathon data
    with open("hackathon_data.json", "r") as f:
        data = json.load(f)

    all_results = []
    devpost_mapping = {}
    hackathons = data["hackathons"]
    for hackathon in hackathons:
        print(f"Processing {hackathon['title']}...")
        prompt = ""
        for projectBatch in hackathon["projects"]:
            for project in projectBatch:
                devpost_mapping[project["title"]] = project["url"]
                prompt += f"""
                Project Title: {project["title"]}
                Project Description: {project["description"]}
                Project Story: {project["story"]}
                """
        
        prompt += """
        Extract the main points in simple words (basically what the project does) and return the data in the following format:
        {
            "title": str,
            "summary": str,
            "features": List[str]
        }
        """
    
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Project],
            },
        )

        try:
            # Parse the response text as JSON
            response_data = json.loads(response.text)
            print(type(response_data))
            # Convert each item in the list to a Project model
            projects = [Project(**item) for item in response_data]
            print(len(projects))
            # Convert to dictionary format
            json_data = [project.model_dump() for project in projects]
            for project in json_data:
                print(project)
                project["hackathon_title"] = hackathon["title"] or ""
                project["hackathon_location"] = hackathon["location"] or ""
                project["hackathon_submission_dates"] = hackathon["submission_dates"] or ""
                project["hackathon_organization"] = hackathon["organization"] or ""
                project["devpost_url"] = devpost_mapping[project["title"]] if project["title"] in devpost_mapping else ""

            all_results.extend(json_data)
            print(f"Successfully processed {len(projects)} projects")
        except Exception as e:
            print(f"Error processing response: {str(e)}")
            # print(f"Response text: {response.text}")
            continue

    # Save all results to file
    with open("hackathon_summaries.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("Results saved to hackathon_summaries.json")

if __name__ == "__main__":
    process_hackathons() 