"""API REST del asistente RAG."""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag import answer

app = FastAPI(title="Asistente RAG de marcos de ciberseguridad")


class Pregunta(BaseModel):
    pregunta: str = Field(..., min_length=3, examples=["¿Cuáles son las funciones del NIST CSF 2.0?"])
    k: int = Field(4, ge=1, le=10, description="Número de fragmentos a recuperar")


@app.get("/salud")
def salud() -> dict:
    return {"estado": "ok"}


@app.post("/preguntar")
def preguntar(p: Pregunta) -> dict:
    return answer(p.pregunta, p.k)
