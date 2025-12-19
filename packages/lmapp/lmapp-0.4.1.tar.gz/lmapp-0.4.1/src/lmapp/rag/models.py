from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone


@dataclass
class Document:
    """Represents a searchable document or chunk."""

    doc_id: str
    title: str
    content: str
    file_path: Optional[str] = None
    source_type: str = "text"  # text, markdown, code, url
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    parent_id: Optional[str] = None  # ID of the parent file if this is a chunk
    chunk_index: int = 0  # Index of this chunk in the parent file

    def __post_init__(self):
        """Initialize derived fields."""
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.metadata:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "file_path": self.file_path,
            "source_type": self.source_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "parent_id": self.parent_id,
            "chunk_index": self.chunk_index,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Document":
        """Create Document from dictionary."""
        doc = Document(
            doc_id=data["doc_id"],
            title=data["title"],
            content=data["content"],
            file_path=data.get("file_path"),
            source_type=data.get("source_type", "text"),
            metadata=data.get("metadata"),
            created_at=data.get("created_at"),
            parent_id=data.get("parent_id"),
            chunk_index=data.get("chunk_index", 0),
        )
        return doc


@dataclass
class SearchResult:
    """Represents a search result."""

    document: Document
    relevance_score: float
    matched_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document": self.document.to_dict(),
            "relevance_score": self.relevance_score,
            "matched_text": self.matched_text,
        }
