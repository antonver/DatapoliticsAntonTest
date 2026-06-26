import os
import faiss
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import load_index_from_storage
from dotenv import load_dotenv
import os

load_dotenv()

EMBED_MODEL = HuggingFaceEmbedding(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
SPLITTER = SentenceSplitter(chunk_size=300, chunk_overlap=100)
STORAGE_DIR = os.getenv("STORAGE", "./storage")

def build_and_save_vector_store(pdf_path: str) :
    documents = PDFReader().load_data(file=pdf_path)
    nodes = SPLITTER.get_nodes_from_documents(documents)
    doc_name = os.path.basename(pdf_path)

    for idx, node in enumerate(nodes):
        node.metadata["chunk_index"] = idx
        node.metadata["document_name"] = doc_name

    if os.path.isfile(f"{STORAGE_DIR}/docstore.json"):
        storage_context = StorageContext.from_defaults(
            vector_store=FaissVectorStore.from_persist_dir(STORAGE_DIR), persist_dir=STORAGE_DIR
        )
        index = load_index_from_storage(storage_context, embed_model=EMBED_MODEL)
        index.insert_nodes(nodes)
    else:
        storage_context = StorageContext.from_defaults(vector_store=FaissVectorStore(faiss_index=faiss.IndexFlatIP(384)))
        index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=EMBED_MODEL)

    index.storage_context.persist(persist_dir=STORAGE_DIR)
    print(f"Index for {doc_name} was succsesfully created: {STORAGE_DIR}")


def load_retriever(top_k: int = 5):
    vector_store = FaissVectorStore.from_persist_dir(persist_dir=STORAGE_DIR)
    storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=STORAGE_DIR)
    index = load_index_from_storage(storage_context, embed_model=EMBED_MODEL)
    return index.as_retriever(similarity_top_k=top_k)


def query_vector_store(retriever, query_text: str) -> list[dict]:
    retrieved_nodes = retriever.retrieve(query_text)
    output_chunks = []
    for node_with_score in retrieved_nodes:
        raw_page = node_with_score.node.metadata.get("page_label")
        output_chunks.append({
            "text": node_with_score.node.text,
            "score": float(node_with_score.score),
            "document_name": node_with_score.node.metadata.get("document_name"),
            "page_number": int(raw_page) if raw_page and raw_page.isdigit() else None,
            "chunk_index": node_with_score.node.metadata.get("chunk_index"),
        })
    return output_chunks
