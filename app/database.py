from uuid import UUID, uuid4

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from app.config import settings


def get_connection():
    connection = psycopg.connect(settings.database_url)
    register_vector(connection)
    return connection


def init_db():
    with psycopg.connect(settings.database_url) as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id BIGSERIAL PRIMARY KEY,
                document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                page INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR(1536) NOT NULL
            )
            """
        )


def create_document(name: str) -> UUID:
    document_id = uuid4()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (id, name)
            VALUES (%s, %s)
            """,
            (document_id, name),
        )

    return document_id


def save_chunks(
    document_id: UUID,
    chunks: list[tuple[int, str, list[float]]],
):
    rows = [
        (document_id, page, content, Vector(embedding))
        for page, content, embedding in chunks
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO chunks (
                    document_id,
                    page,
                    content,
                    embedding
                )
                VALUES (%s, %s, %s, %s)
                """,
                rows,
            )


def search_chunks(
    document_id: UUID,
    query_embedding: list[float],
    limit: int = 5,
) -> list[dict]:
    vector = Vector(query_embedding)

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    page,
                    content,
                    1 - (embedding <=> %s) AS score
                FROM chunks
                WHERE document_id = %s
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (
                    vector,
                    document_id,
                    vector,
                    limit,
                ),
            )

            return cursor.fetchall()


def get_document_chunks(document_id: UUID) -> list[dict]:
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT page, content
                FROM chunks
                WHERE document_id = %s
                ORDER BY page, id
                """,
                (document_id,),
            )

            return cursor.fetchall()
