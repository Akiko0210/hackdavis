import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import pymongo
from pydantic import BaseModel
from google import genai
from openai import OpenAI
import time
import os
from dotenv import load_dotenv
from typing import List
import json

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

class Project(BaseModel):
    title: str
    summary: str
    features: List[str]

MONGODB_URI = os.getenv("MONGODB_URI")  # Replace with your Atlas connection string
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with your OpenAI API key
DB_NAME = "hackdavis"
COLLECTION_NAME = "projects"
VECTOR_INDEX_NAME = "vector_index_projects"

# Initialize clients
mongo_client = pymongo.MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]
openai_client = OpenAI(api_key=OPENAI_API_KEY)


app = Flask(__name__)
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; WebScraper/1.0)"
}

def create_vector_search_index():
    try:
        # Check if index already exists
        existing_indexes = collection.list_search_indexes()
        for index in existing_indexes:
            if index["name"] == VECTOR_INDEX_NAME:
                print("Vector search index already exists. Dropping it to recreate with correct dimensions...")
                collection.drop_search_index(VECTOR_INDEX_NAME)
                break

        # Define the vector search index
        index_definition = {
            "name": VECTOR_INDEX_NAME,
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 1536,  # OpenAI text-embedding-ada-002 uses 1536 dimensions
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "hackathon_title"  # Using hackathon_title as a filter field
                    }
                ]
            }
        }

        # Create the index
        collection.create_search_index(index_definition)
        print("Creating vector search index...")

        # Poll until the index is ready
        while True:
            indexes = collection.list_search_indexes()
            for idx in indexes:
                if idx["name"] == VECTOR_INDEX_NAME and idx.get("status") == "READY":
                    print("Vector search index is ready!")
                    return
            print("Waiting for index to be ready...")
            time.sleep(5)

    except Exception as e:
        print(f"Error creating vector search index: {e}")

# Function to generate embeddings using OpenAI
def generate_embedding(text):
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Function to combine summary and features for embedding
def combine_summary_and_features(doc):
    print(doc, type(doc))
    summary = doc['summary']
    features = doc['features']
    # Convert features array to a single string
    features_text = " ".join([str(feature) for feature in features]) if features else ""
    # Combine summary and features, ensuring no empty result
    combined_text = f"{summary} {features_text}".strip()
    return combined_text if combined_text else None

# Function to add embeddings to existing documents
def add_embedding_to_document():
    try:
        # Find documents without an embedding
        documents = collection.find({"embedding": {"$exists": False}})
        for doc in documents:
            combined_text = combine_summary_and_features(doc)
            if combined_text:
                embedding = generate_embedding(combined_text)
                if embedding:
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"embedding": embedding}}
                    )
                    print(f"Added embedding for project: {doc['title']}")
                else:
                    print(f"Failed to generate embedding for project: {doc['title']}")
            else:
                print(f"No valid summary or features for project: {doc['title']}")
    except Exception as e:
        print(f"Error adding embeddings: {e}")

# Function to perform vector search
def perform_vector_search(query_text, limit=5, hackathon_filter=None):
    query_embedding = generate_embedding(query_text)
    if not query_embedding:
        return

    vector_search_stage = {
        "$vectorSearch": {
            "index": VECTOR_INDEX_NAME,
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": limit
        }
    }

    # Add filter for hackathon_title if provided
    if hackathon_filter:
        vector_search_stage["$vectorSearch"]["filter"] = {
            "hackathon_title": hackathon_filter
        }

    pipeline = [
        vector_search_stage,
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "summary": 1,
                "features": 1,
                "hackathon_title": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    try:
        results = collection.aggregate(pipeline)
        print(f"\nSearch results for query: '{query_text}'")
        for result in results:
            print(f"Title: {result['title']}, Hackathon: {result['hackathon_title']}, Score: {result['score']}")
            print(f"Summary: {result['summary']}")
            print(f"Features: {result['features']}\n")
        return results
    except Exception as e:
        print(f"Error performing vector search: {e}")

def gemini_summary(doc):
    print(doc, type(doc))
    try:
        # Create the prompt with project details
        prompt = f"""
        Project Title: {doc['title']}
        Project Description: {doc['description']}
        Project Story: {doc['story']}
        
        Extract the main points in simple words (basically what the project does) and return the data in the following format:
        {{
            "title": str,
            "summary": str,
            "features": List[str]
        }}
        """

        print(prompt, "prompt")
        
        # Generate content using Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": Project,
            },
        )

        print(response.text, "ghello")
        # Parse the response
        if response.text:
            try:
                # Convert the response to a dictionary
                response_data = json.loads(response.text)
                
                # Convert to Project model
                project = Project(**response_data)
                
                print(project)
                
                # Convert back to dictionary for MongoDB
                return project.model_dump()
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return None
        return None
    except Exception as e:
        print(f"Error in gemini_summary: {e}")
        return None

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data['url']
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Remove the built-with section entirely
    built_with = soup.find(id="built-with")
    if built_with:
        built_with.decompose()

    # Title
    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    og_title = og_title_tag['content'] if og_title_tag else "No Title"

    og_desc_tag = soup.find("meta", attrs={"property": "og:description"})
    og_desc = og_desc_tag['content'] if og_desc_tag else "No Description"

    app_details = soup.find(id="app-details-left")
    story = ""
    github = ""

    if app_details:
        divs = app_details.find_all("div", recursive=False)
        
        if len(divs) >= 2:
            info_div = divs[1]

            for i in info_div:

                if i.name == "h2":
                    story = story + i.get_text(strip=True) + ": "

                if i.name == "p":
                    story += i.get_text(strip=True)

                if i.name == "ul":
                    story = story + i.get_text(strip=True) + ","

        for a in app_details.find_all("a", href=True):
            href = a['href']
            if "https://github.com/" in href:
                github = href

    if story == "":
        story = og_desc

    link_tag = soup.select_one(".software-list-content > p > a")

    doc = {
        "title": og_title,
        "description": og_desc,
        "story": story.strip(),
        "github": github,
        "url": url,
        "submitted_to": link_tag.text.strip(),
        "hackathon": link_tag.get("href")
    }

    summary_doc = gemini_summary(doc)
    print(summary_doc, type(summary_doc))

    # Get search results
    search_results = perform_vector_search(combine_summary_and_features(summary_doc), limit=5, hackathon_filter=None)
    
    # Convert MongoDB results to JSON-serializable format
    json_results = []
    for result in search_results:
        # Convert ObjectId to string if present
        if '_id' in result:
            result['_id'] = str(result['_id'])
        json_results.append(result)
    
    return jsonify(json_results)

if __name__ == '__main__':
    app.run(debug=True)
