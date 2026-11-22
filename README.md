# Asistente RAG de marcos de ciberseguridad

Asistente que responde preguntas sobre documentos de NIST (u otros marcos) usando
**RAG (Retrieval-Augmented Generation)** y cita el documento y la página de cada respuesta.

**Stack:** Python · LangChain · OpenAI API (embeddings + LLM) · PostgreSQL con pgvector · FastAPI · Docker

## Cómo funciona

1. `ingest.py` lee los PDFs de `docs/`, los divide en fragmentos y genera un embedding por fragmento.
2. Los embeddings se guardan en PostgreSQL (extensión pgvector).
3. Al recibir una pregunta, se busca por similitud semántica los fragmentos más relevantes.
4. El LLM responde usando solo esos fragmentos y cita sus fuentes.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # y pon tu OPENAI_API_KEY
docker compose up -d             # levanta PostgreSQL + pgvector
```

## Documentos

Descarga y guarda en `docs/` (ejemplos, son de dominio público):

- NIST Cybersecurity Framework 2.0 — https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- NIST SP 800-30 Rev. 1 (evaluación de riesgos) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf

## Uso

```bash
python ingest.py
uvicorn app:app --reload
```

Abre http://localhost:8000/docs para probar la API, o:

```bash
curl -X POST http://localhost:8000/preguntar \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuáles son las funciones del NIST CSF 2.0?"}'
```

Respuesta de ejemplo:

```json
{
  "respuesta": "El CSF 2.0 define seis funciones: Govern, Identify, Protect, Detect, Respond y Recover [1]...",
  "fuentes": [{"id": 1, "documento": "NIST.CSWP.29.pdf", "pagina": 5}]
}
```

## Próximas mejoras

- Interfaz web sencilla (Streamlit o HTML + JS)
- Evaluación de la calidad de respuestas con un set de preguntas de prueba
- Soporte para Azure OpenAI
