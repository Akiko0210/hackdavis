import pymongo
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

load_dotenv()
# Configuration
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

# Function to create vector search index
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
    summary = doc.get("summary", "")
    features = doc.get("features", [])
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
    except Exception as e:
        print(f"Error performing vector search: {e}")

# Main execution
if __name__ == "__main__":
    # Create vector search index
    create_vector_search_index()

    # Add embeddings to documents (including the sample data)
    add_embedding_to_document()

    sample_query = "AI-powered cooking assistant"  # New query
    perform_vector_search(sample_query, limit=5, hackathon_filter=None)