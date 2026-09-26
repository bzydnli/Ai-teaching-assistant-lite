# AI Teaching Assistant Lite

A small source-grounded AI application that turns course material into a simple teaching workflow.

## Demo

![AI Teaching Assistant Overview](docs/demo-overview.png)

![Source-Grounded Topic Teaching](docs/demo-teach.png)

## Why This Project?

This project is a small prototype related to my master's work on AI-supported teaching systems.

I built it to practice and demonstrate a clear end-to-end RAG workflow without hiding the core logic behind large frameworks.

## What It Does

- Upload a PDF course document
- Extract and split the document into chunks
- Create embeddings and store them in PostgreSQL with pgvector
- Generate a short teaching plan from the material
- Teach a selected topic using only relevant source content
- Answer questions using semantic retrieval
- Return page references and retrieval similarity scores

## Flow

### Document indexing

```text
PDF
 ↓
Text extraction
 ↓
Chunking
 ↓
Embeddings
 ↓
PostgreSQL + pgvector
```

### Question answering

```text
Question
 ↓
Question embedding
 ↓
Semantic search
 ↓
Top relevant chunks
 ↓
LLM
 ↓
Source-grounded answer + page references
```

### Topic teaching

```text
Topic
 ↓
Topic embedding
 ↓
Semantic search
 ↓
Relevant course material
 ↓
LLM
 ↓
Source-grounded explanation
```

## Tech Stack

- Python
- FastAPI
- Streamlit
- OpenAI API
- PostgreSQL
- pgvector
- Docker
- PyPDF

## Project Structure

```text
Ai-teaching-assistant-lite/
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── pdf.py
│   └── schemas.py
├── ui.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Check API status |
| POST | `/documents` | Upload and index a PDF |
| POST | `/plan` | Create a teaching plan |
| POST | `/teach` | Explain a selected topic |
| POST | `/ask` | Ask a source-grounded question |

## Running the Project

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file from `.env.example`:

```env
OPENAI_API_KEY=your_api_key
CHAT_MODEL=gpt-5.6-luna
EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ai_teacher
```

### 4. Start PostgreSQL + pgvector

```bash
docker compose up -d
```

### 5. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the Streamlit interface

Open another terminal:

```bash
streamlit run ui.py
```

The interface will be available at:

```text
http://localhost:8501
```

## Example

After uploading a machine learning course PDF, the application can create a teaching plan such as:

```text
1. Introduction to Machine Learning
2. Types of Machine Learning
3. Supervised Learning
4. Classification and Regression
5. Unsupervised and Reinforcement Learning
6. Model Evaluation and Overfitting
```

A user can then select a topic such as `Model Evaluation and Overfitting`.

The system retrieves the most relevant document chunks and generates an explanation grounded in those sections of the uploaded material.

## Design Choices

This project intentionally avoids additional orchestration frameworks in its first version.

The goal is to keep the core RAG pipeline visible:

- embedding generation
- vector storage
- similarity search
- context construction
- grounded generation

This makes the architecture small enough to inspect end-to-end without hiding the main logic behind abstractions.

## Current Scope

The current version is intentionally simple:

- text-based PDF input
- fixed word-based chunking with overlap
- top-k vector similarity retrieval
- page-level source references
- no OCR
- no reranking
- no authentication

These are natural extension points for a production version.

## Background

This prototype is related to my ongoing work on AI-supported teaching systems during my Software Engineering master's studies.

My broader interest is in building AI applications that do more than generate text: systems that structure source material, retrieve the right context, and produce controlled, useful outputs for real workflows.
