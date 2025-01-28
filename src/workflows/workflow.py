from datetime import timedelta
from pydantic import BaseModel, Field
from restack_ai.workflow import workflow, import_functions, log, RetryPolicy
with import_functions():
    from src.functions.weaviate_functions import semantic_search, hybrid_search, QueryInput
    from src.functions.gemini_function_call import gemini_function_call, FunctionInputParams

class CurriculumInput(BaseModel):
    user_content: str = Field(default='I want to learn about the history of the United States')

@workflow.defn()
class CurriculumWorkflow:
    @workflow.run
    async def run(self, input: CurriculumInput):
        chat_history = []
        log.info("CurriculumWorkflow started")
        
        response = await workflow.step(gemini_function_call, input=FunctionInputParams(user_content=input.user_content + ', try to use the tools to find books and create a curriculum'), start_to_close_timeout=timedelta(seconds=120), retry_policy=RetryPolicy(maximum_attempts=1), task_queue="gemini")
        # Get function calls from response
        for candidate in response["candidates"]:
            for part in candidate["content"]["parts"]:
                if "functionCall" in part:
                    if part["functionCall"]["name"] == "hybrid_search":
                        hybrid_result = await workflow.step(hybrid_search, input=QueryInput(user_content=part["functionCall"]["args"]["user_content"]))
                        chat_history.append(hybrid_result)  
                    elif part["functionCall"]["name"] == "semantic_search": 
                        semantic_result = await workflow.step(semantic_search, input=QueryInput(user_content=part["functionCall"]["args"]["user_content"]))
                        chat_history.append(semantic_result)
        
        final_response = await workflow.step(gemini_function_call, input=FunctionInputParams(user_content=f"Here is the chat history: {chat_history}"), start_to_close_timeout=timedelta(seconds=120), retry_policy=RetryPolicy(maximum_attempts=1), task_queue="gemini")
        return final_response