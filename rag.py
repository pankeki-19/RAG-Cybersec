"""Lógica RAG: vector store en PostgreSQL (pgvector) + respuesta con LLM."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

COLLECTION = "marcos_ciberseguridad"

SYSTEM_PROMPT = (
    "Eres un asistente experto en marcos de ciberseguridad. Responde en español "
    "usando SOLO el contexto proporcionado. Cita las fuentes con su número entre "
    "corchetes, por ejemplo [1]. Si el contexto no contiene la respuesta, dilo "
    "claramente en lugar de inventarla."
)


def get_vector_store(reset: bool = False) -> PGVector:
    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION,
        connection=os.environ["DATABASE_URL"],
        use_jsonb=True,
        pre_delete_collection=reset,
    )


@lru_cache
def _store() -> PGVector:
    return get_vector_store()


@lru_cache
def _llm() -> ChatOpenAI:
    return ChatOpenAI(model=os.getenv("CHAT_MODEL", "gpt-4o-mini"), temperature=0)


def answer(question: str, k: int = 4) -> dict:
    docs = _store().similarity_search(question, k=k)

    fuentes = []
    bloques = []
    for i, d in enumerate(docs, start=1):
        doc_name = Path(d.metadata.get("source", "desconocido")).name
        page = int(d.metadata.get("page", 0)) + 1  # PyPDFLoader cuenta desde 0
        fuentes.append({"id": i, "documento": doc_name, "pagina": page})
        bloques.append(f"[{i}] ({doc_name}, p. {page})\n{d.page_content}")

    contexto = "\n\n".join(bloques)
    resp = _llm().invoke([
        ("system", SYSTEM_PROMPT),
        ("human", f"Contexto:\n{contexto}\n\nPregunta: {question}"),
    ])
    return {"respuesta": resp.content, "fuentes": fuentes}
