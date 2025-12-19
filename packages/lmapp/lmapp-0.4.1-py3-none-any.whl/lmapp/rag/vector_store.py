"""Vector store implementations for persistent embedding storage."""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class VectorDocument:
    """Document with vector embedding."""

    doc_id: str
    text: str
    vector: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    source: str


@dataclass
class SearchResult:
    """Vector search result with distance metric."""

    doc_id: str
    text: str
    similarity: float
    metadata: Dict[str, Any]
    distance: float


@dataclass
class VectorSearchResult:
    """Legacy search result (for compatibility)."""

    doc_id: str
    score: float
    metadata: Dict[str, Any]
    content: Optional[str] = None


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def add_document(self, doc: VectorDocument) -> str:
        """Add document with vector to store.

        Args:
            doc: VectorDocument with embedding

        Returns:
            Document ID
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search vector store.

        Args:
            query_vector: Query embedding
            top_k: Number of results
            filter_metadata: Optional metadata filters

        Returns:
            List of SearchResult
        """
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from store.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def update_document(self, doc: VectorDocument) -> bool:
        """Update document in store.

        Args:
            doc: Updated VectorDocument

        Returns:
            True if updated, False if not found
        """
        pass

    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Retrieve document by ID.

        Args:
            doc_id: Document ID

        Returns:
            VectorDocument or None
        """
        pass

    @abstractmethod
    async def list_documents(
        self,
        source_filter: Optional[str] = None,
        limit: int = 100,
    ) -> List[VectorDocument]:
        """List documents in store.

        Args:
            source_filter: Optional source filter
            limit: Max documents to return

        Returns:
            List of VectorDocument
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents from store."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        pass

    # Legacy methods for backwards compatibility
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the store (legacy)."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5, filter: Optional[Dict] = None) -> List[VectorSearchResult]:
        """Search for similar documents (legacy)."""
        pass

    @abstractmethod
    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents by ID (legacy)."""
        pass

    @abstractmethod
    def persist(self) -> None:
        """Save to disk (legacy)."""
        pass
        pass
