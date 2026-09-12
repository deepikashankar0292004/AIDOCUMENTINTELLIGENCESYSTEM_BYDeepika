from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    file_type = Column(
        String(50),
        nullable=True
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    document_type = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )