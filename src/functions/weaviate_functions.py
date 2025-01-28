from restack_ai.function import function, log
from pydantic import BaseModel
import weaviate
from weaviate.classes.init import Auth
import os, json

class QueryInput(BaseModel):
    user_content: str
    
class BookResult(BaseModel):
    title: str
    description: str

class DatabaseOutput(BaseModel):
    books: list[BookResult]

def weaviate_client():
    # Don't hardcode credentials in your code like us. This is an example.
    # The WCD API KEY is a read only API Key.
    wcd_url = "https://4zfylktqsqkmqkougroa.c0.us-east1.gcp.weaviate.cloud" 
    wcd_api_key = "UGbNHq95PEfuac6caJPFLBnMNLyzoIReZSIG" # READ ONLY API KEY
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=wcd_url,                                    # Replace with your Weaviate Cloud URL
        auth_credentials=Auth.api_key(wcd_api_key),             # Replace with your Weaviate Cloud key
        # headers={"X-OpenAI-Api-Key": openai_api_key},           # Replace with your Cohere API key
    )
    
    # Best practice: store your credentials in environment variables
    # wcd_url = os.environ["WCD_URL"]
    # wcd_api_key = os.environ["WCD_API_KEY"]
    return client

@function.defn()
async def hybrid_search(input: QueryInput) -> DatabaseOutput:
    try:
        client = weaviate_client()
        log.info(f"Client connected to Weaviate Cloud: {client} and hybrid search started")   

        questions = client.collections.get("BookVectorizedByWeaviateEmbeddings")

        response = questions.query.hybrid(
            query=input.user_content,
            alpha=0.5,
            limit=2
        )
        log.info(f"Response from Weaviate Cloud: {response}")
        for obj in response.objects:
            log.info(json.dumps(obj.properties, indent=2))

        client.close()  # Free up resources
        
        books = [
            BookResult(
                title=obj.properties.get('title'),
                description=obj.properties.get('description')
            )
            for obj in response.objects
        ]
        
        log.info(f"Hybrid search completed: {books}")
        return DatabaseOutput(books=books)

    except Exception as e:
        log.error("welcome function failed", error=e)
        raise e

@function.defn()
async def semantic_search(input: QueryInput) -> DatabaseOutput:
    try:
        client = weaviate_client()
        log.info(f"Client connected to Weaviate Cloud: {client} and semantic search started")

        questions = client.collections.get("BookVectorizedByWeaviateEmbeddings")

        response = questions.query.near_text(
            query=input.user_content,
            limit=2
        )
        log.info(f"Response from Weaviate Cloud: {response}")
        for obj in response.objects:
            log.info(json.dumps(obj.properties, indent=2))

        client.close()  # Free up resources
        
        books = [
            BookResult(
                title=obj.properties.get('title'),
                description=obj.properties.get('description')
            )
            for obj in response.objects
        ]
        
        return DatabaseOutput(books=books)

    except Exception as e:
        log.error("welcome function failed", error=e)
        raise e

## Weaviate functions as tools for Gemini 
weaviate_tools = [
    {
        "name": "hybrid_search",
        "description": "Hybrid search for books using the Weaviate Cloud Database",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "user_content": {"type": "STRING"}
            },
            "required": ["user_content"]
        }
    },
    {
        "name": "semantic_search",
        "description": "Semantic search for books using the Weaviate Cloud Database",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "user_content": {"type": "STRING"}
            },
            "required": ["user_content"]
        }
    }
]