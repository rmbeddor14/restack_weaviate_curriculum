import asyncio
import os
from src.functions.weaviate_functions import semantic_search, hybrid_search
from src.functions.gemini_function_call import gemini_function_call
from src.client import client
from src.workflows.workflow import CurriculumWorkflow
from watchfiles import run_process
from restack_ai.restack import ServiceOptions
import webbrowser

async def main():
    
    await asyncio.gather(
        client.start_service(
            workflows=[CurriculumWorkflow],
            functions=[semantic_search, hybrid_search]
        ),
        client.start_service(
            functions=[gemini_function_call],
            workflows=[],
            options=ServiceOptions(
                rate_limit=0.16,
            ),
            task_queue="gemini"
        )
    )

def run_services():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Service interrupted by user. Exiting gracefully.")

def watch_services():
    watch_path = os.getcwd()
    print(f"Watching {watch_path} and its subdirectories for changes...")
    webbrowser.open("http://localhost:5233")
    run_process(watch_path, recursive=True, target=run_services)

if __name__ == "__main__":
       run_services()
