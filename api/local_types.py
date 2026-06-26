from typing import List

from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class OutputChunks(BaseModel):
    document_name: str
    page_number: int | None = None
    chunk_index: int
    score: float
    text: str


class SearchResponse(BaseModel):
    query: str
    results: List[OutputChunks]
