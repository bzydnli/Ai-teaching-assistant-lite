from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    document_id: UUID
    filename: str
    chunks: int


class AskRequest(BaseModel):
    document_id: UUID
    question: str = Field(min_length=1)


class Source(BaseModel):
    page: int
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class PlanRequest(BaseModel):
    document_id: UUID


class PlanResponse(BaseModel):
    plan: str


class TeachRequest(BaseModel):
    document_id: UUID
    topic: str = Field(min_length=1)


class TeachResponse(BaseModel):
    explanation: str
    sources: list[Source]
