from restack_ai.function import function, log
from pydantic import BaseModel
import weaviate
from weaviate.classes.init import Auth
import os, json

class QueryInput(BaseModel):
    name: str


@function.defn()
async def hybrid_search(input: QueryInput) -> str:
    log.info(f"welcome function started", input=input)
    return "Hello, World!"

@function.defn()
async def semantic_search(input: QueryInput) -> str:
    try:

        # Don't hardcode credentials in your code like us. This is an example.
        # The WCD API KEY is a read only API Key.
        wcd_url = "https://4zfylktqsqkmqkougroa.c0.us-east1.gcp.weaviate.cloud" 
        wcd_api_key = "UGbNHq95PEfuac6caJPFLBnMNLyzoIReZSIG" # READ ONLY API KEY

        # Best practice: store your credentials in environment variables
        # wcd_url = os.environ["WCD_URL"]
        # wcd_api_key = os.environ["WCD_API_KEY"]


        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=wcd_url,                                    # Replace with your Weaviate Cloud URL
            auth_credentials=Auth.api_key(wcd_api_key),             # Replace with your Weaviate Cloud key
            # headers={"X-OpenAI-Api-Key": openai_api_key},           # Replace with your Cohere API key
        )
        log.info(f"Client connected to Weaviate Cloud: {client}")   

        questions = client.collections.get("BookVectorizedByWeaviateEmbeddings")

        response = questions.query.near_text(
            query=input.name,
            limit=2
        )
        log.info(f"Response from Weaviate Cloud: {response}")
        for obj in response.objects:
            log.info(json.dumps(obj.properties, indent=2))

        client.close()  # Free up resources
        return json.dumps(response.objects[0].properties.get('title'), indent=2)


    except Exception as e:
        log.error("welcome function failed", error=e)
        raise e
