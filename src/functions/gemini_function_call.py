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
    tools: bool = False
    structured_output: bool = False

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
                tools=[types.Tool(
                    function_declarations=weaviate_tools)] if input.tools else None,
                response_schema=curriculum_schema if input.structured_output else None,
                response_mime_type="application/json" if input.structured_output else None
            )
        )
        return response
    except Exception as e:
        log.error("gemini_function_call function failed", error=e)
        raise e


curriculum_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "difficulty_level": {"type": "string", "enum": ["Beginner", "Intermediate", "Advanced"]},
        "estimated_duration": {"type": "string"},
        "prerequisites": {
            "type": "array",
            "items": {"type": "string"}
        },
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "module_number": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "learning_objectives": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "required_reading": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "author": {"type": "string"},
                                "pages": {"type": "string"},
                                "notes": {"type": "string"}
                            }
                        }
                    },
                    "assignments": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["module_number", "title", "description", "learning_objectives", "required_reading"]
            }
        }
    },
    "required": ["title", "description", "difficulty_level", "estimated_duration", "modules"]
}