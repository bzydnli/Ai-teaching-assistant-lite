from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.ai import (
    answer_question,
    create_teaching_plan,
    embed_texts,
    teach_topic,
)
from app.database import (
    create_document,
    get_document_chunks,
    init_db,
    save_chunks,
    search_chunks,
)
from app.pdf import extract_pages, split_text
from app.schemas import (
    AskRequest,
    AskResponse,
    DocumentResponse,
    PlanRequest,
    PlanResponse,
    Source,
    TeachRequest,
    TeachResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Teaching Assistant Lite",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_content = await file.read()
    pages = extract_pages(file_content)

    chunk_rows = []

    for page_number, text in pages:
        for chunk in split_text(text):
            chunk_rows.append((page_number, chunk))

    if not chunk_rows:
        raise HTTPException(
            status_code=422,
            detail="No text found in the PDF.",
        )

    texts = [content for _, content in chunk_rows]
    embeddings = embed_texts(texts)

    document_id = create_document(file.filename or "document.pdf")

    chunks = [
        (page, content, embedding)
        for (page, content), embedding in zip(chunk_rows, embeddings)
    ]

    save_chunks(document_id, chunks)

    return DocumentResponse(
        document_id=document_id,
        filename=file.filename or "document.pdf",
        chunks=len(chunks),
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    query_embedding = embed_texts([request.question])[0]

    matches = search_chunks(
        document_id=request.document_id,
        query_embedding=query_embedding,
    )

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="Document not found or has no indexed content.",
        )

    context = "\n\n".join(
        f"[Sayfa {match['page']}]\n{match['content']}"
        for match in matches
    )

    answer = answer_question(
        question=request.question,
        context=context,
    )

    sources = [
        Source(
            page=match["page"],
            score=round(float(match["score"]), 4),
        )
        for match in matches
    ]

    return AskResponse(
        answer=answer,
        sources=sources,
    )


@app.post("/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest):
    chunks = get_document_chunks(request.document_id)

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    context = "\n\n".join(
        f"[Sayfa {chunk['page']}]\n{chunk['content']}"
        for chunk in chunks
    )

    plan = create_teaching_plan(context)

    return PlanResponse(plan=plan)


@app.post("/teach", response_model=TeachResponse)
def teach(request: TeachRequest):
    topic_embedding = embed_texts([request.topic])[0]

    matches = search_chunks(
        document_id=request.document_id,
        query_embedding=topic_embedding,
    )

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="Document not found or has no indexed content.",
        )

    context = "\n\n".join(
        f"[Sayfa {match['page']}]\n{match['content']}"
        for match in matches
    )

    explanation = teach_topic(
        topic=request.topic,
        context=context,
    )

    sources = [
        Source(
            page=match["page"],
            score=round(float(match["score"]), 4),
        )
        for match in matches
    ]

    return TeachResponse(
        explanation=explanation,
        sources=sources,
    )
