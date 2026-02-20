from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()

DOC_TYPES = ("image", "pdf", "video")
DOC_STATUS = ("uploaded", "processing", "ready", "failed")
CHUNK_TYPES = ("pdf_text", "video_frame", "video_transcript", "image")


class Document(db.Model):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_name: Mapped[str] = mapped_column(nullable=False)
    stored_name: Mapped[str] = mapped_column(nullable=False)
    mime_type: Mapped[str] = mapped_column(nullable=False)
    doc_type: Mapped[str] = mapped_column(Enum(*DOC_TYPES, name="doc_type"), nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    status: Mapped[str] = mapped_column(Enum(*DOC_STATUS, name="doc_status"), default="uploaded")
    sha256_hash: Mapped[str] = mapped_column(nullable=False)
    preview_path: Mapped[str | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(nullable=True)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(db.Model):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    chunk_type: Mapped[str] = mapped_column(Enum(*CHUNK_TYPES, name="chunk_type"), nullable=False)
    ref: Mapped[str | None] = mapped_column(nullable=True)
    text_content: Mapped[str | None] = mapped_column(nullable=True)
    vector_id: Mapped[str | None] = mapped_column(nullable=True)

    document: Mapped[Document] = relationship(back_populates="chunks")


class JobStatus(db.Model):
    __tablename__ = "job_status"

    id: Mapped[str] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(default="queued")
    progress: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(nullable=True)
