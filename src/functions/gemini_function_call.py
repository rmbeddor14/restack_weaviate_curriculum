import os
from restack_ai.function import function, log
from pydantic import BaseModel, Field
from typing import Optional, List
from google import genai
from google.genai import types
from src.functions.weaviate_functions import weaviate_tools

class ChatMessage(BaseModel):
    role: str
    content: str

class FunctionInputParams(BaseModel):
    user_content: str
    

@function.defn()
async def gemini_function_call(input: FunctionInputParams):
    try:
        log.info("gemini_function_call function started", input=input)
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        log.info(f"Client connected to Google GenAI: {client}")
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[input.user_content],
            config=types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=weaviate_tools)],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
        )
        return response
    except Exception as e:
        log.error("gemini_function_call function failed", error=e)
        raise e
