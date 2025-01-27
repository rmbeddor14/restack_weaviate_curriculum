from datetime import timedelta
from pydantic import BaseModel, Field
from restack_ai.workflow import workflow, import_functions, log, RetryPolicy
with import_functions():
    from src.functions.function import semantic_search, hybrid_search, QueryInput

class GreetingWorkflowInput(BaseModel):
    name: str = Field(default='Bob')

@workflow.defn()
class GreetingWorkflow:
    @workflow.run
    async def run(self, input: GreetingWorkflowInput):
        log.info("GreetingWorkflow started")
        result = await workflow.step(semantic_search, input=QueryInput(name=input.name), start_to_close_timeout=timedelta(seconds=120), retry_policy=RetryPolicy(maximum_attempts=1))

        result2 = await workflow.step(hybrid_search, input=QueryInput(name=input.name), start_to_close_timeout=timedelta(seconds=120), retry_policy=RetryPolicy(maximum_attempts=1))

        log.info("GreetingWorkflow completed", result=result)
        return result + " - " + result2