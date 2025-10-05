from fastapi import FastAPI, Query
from queue_module.connect import queue
from queue_module.worker import process_query

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "Your Fast API is running"}


@app.post("/chat")
def chat(
    query: str = Query(..., description="Chat message")
):
    # into the Queue
    job = queue.enqueue(process_query, query)
    # return Message
    return {"status": "queued my dear", "job_id": job.id}

