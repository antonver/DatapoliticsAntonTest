from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from .local_types import SearchResponse, SearchRequest
from ingestion_app.data_vectorisation import load_retriever, query_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retriever = load_retriever()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/search")
def search(data: SearchRequest, request: Request) -> SearchResponse:
    chunks = query_vector_store(request.app.state.retriever, query_text=data.query)
    return {"query": data.query, "results": chunks}
