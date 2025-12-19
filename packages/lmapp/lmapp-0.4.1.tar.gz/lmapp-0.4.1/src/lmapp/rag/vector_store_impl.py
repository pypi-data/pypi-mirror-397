"""Vector store implementation with in-memory and persistent backends."""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone

from src.lmapp.rag.vector_store import VectorStore, VectorDocument, SearchResult, VectorSearchResult


class InMemoryVectorStore(VectorStore):
    """In-memory vector store for testing and development."""

    def __init__(self):
        """Initialize memory store."""
        self.documents: Dict[str, VectorDocument] = {}
        self._stats = {
            "documents_added": 0,
            "searches_performed": 0,
            "documents_deleted": 0,
        }

    async def add_document(self, doc: VectorDocument) -> str:
        """Add document to memory store."""
        self.documents[doc.doc_id] = doc
        self._stats["documents_added"] += 1
        return doc.doc_id

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search memory store using cosine similarity."""
        self._stats["searches_performed"] += 1

        results = []
        for doc_id, doc in self.documents.items():
            # Apply metadata filter
            if filter_metadata:
                match = all(doc.metadata.get(k) == v for k, v in filter_metadata.items())
                if not match:
                    continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_vector, doc.vector)
            distance = 1.0 - similarity

            results.append(
                SearchResult(
                    doc_id=doc_id,
                    text=doc.text,
                    similarity=similarity,
                    metadata=doc.metadata,
                    distance=distance,
                )
            )

        # Sort by similarity (descending) and return top k
        results.sort(key=lambda x: -x.similarity)
        return results[:top_k]

    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from store."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._stats["documents_deleted"] += 1
            return True
        return False

    async def update_document(self, doc: VectorDocument) -> bool:
        """Update document in store."""
        if doc.doc_id in self.documents:
            self.documents[doc.doc_id] = doc
            return True
        return False

    async def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Retrieve document by ID."""
        return self.documents.get(doc_id)

    async def list_documents(
        self,
        source_filter: Optional[str] = None,
        limit: int = 100,
    ) -> List[VectorDocument]:
        """List documents in store."""
        docs = self.documents.values()
        if source_filter:
            docs = [d for d in docs if d.source == source_filter]
        return list(docs)[:limit]

    async def clear(self) -> None:
        """Clear all documents."""
        self.documents.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            **self._stats,
            "total_documents": len(self.documents),
            "type": "memory",
        }

    # Legacy methods
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents (legacy)."""
        for doc in documents:
            vector_doc = VectorDocument(
                doc_id=doc.get("id", ""),
                text=doc.get("content", ""),
                vector=doc.get("embedding", []),
                metadata=doc.get("metadata", {}),
                timestamp=datetime.now(timezone.utc),
                source=doc.get("source", ""),
            )
            asyncio.run(self.add_document(vector_doc))

    def search_legacy(
        self,
        query: str,
        limit: int = 5,
        filter: Optional[Dict] = None,
    ) -> List[VectorSearchResult]:
        """Search (legacy)."""
        # Mock search - would need embedding model in real usage
        results = []
        for doc_id, doc in list(self.documents.items())[:limit]:
            results.append(
                VectorSearchResult(
                    doc_id=doc_id,
                    score=0.8,
                    metadata=doc.metadata,
                    content=doc.text,
                )
            )
        return results

    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents (legacy)."""
        for doc_id in doc_ids:
            if doc_id in self.documents:
                del self.documents[doc_id]

    def persist(self) -> None:
        """Persist to disk (legacy - no-op for memory store)."""
        pass

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)


class ChromaDBVectorStore(VectorStore):
    """ChromaDB-backed persistent vector store."""

    def __init__(self, collection_name: str = "lmapp", persist_dir: str = ".chroma"):
        """Initialize ChromaDB store.

        Args:
            collection_name: Name of collection
            persist_dir: Directory for persistence
        """
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self._initialized = False
        self._client = None
        self._collection = None
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of ChromaDB client."""
        if self._initialized:
            return

        try:
            import chromadb
        except ImportError:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")

        self._client = chromadb.Client(
            chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_dir,
                anonymized_telemetry=False,
            )
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._initialized = True

    async def add_document(self, doc: VectorDocument) -> str:
        """Add document to ChromaDB."""
        await self._ensure_initialized()

        # Store metadata separately for retrieval
        self._metadata_cache[doc.doc_id] = {
            "text": doc.text,
            "source": doc.source,
            "timestamp": doc.timestamp.isoformat(),
            **doc.metadata,
        }

        self._collection.add(
            ids=[doc.doc_id],
            embeddings=[doc.vector],
            documents=[doc.text],
            metadatas=[
                {
                    "source": doc.source,
                    "timestamp": doc.timestamp.isoformat(),
                    **doc.metadata,
                }
            ],
        )

        return doc.doc_id

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search ChromaDB collection."""
        await self._ensure_initialized()

        where_filter = None
        if filter_metadata:
            # Build where clause for metadata filtering
            where_filter = {}
            for key, value in filter_metadata.items():
                where_filter[key] = {"$eq": value}

        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_filter,
            include=["embeddings", "documents", "distances", "metadatas"],
        )

        search_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                # Distance from ChromaDB (already computed)
                distance = results["distances"][0][i]
                similarity = 1.0 - distance

                text = results["documents"][0][i] if results["documents"] else ""
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}

                search_results.append(
                    SearchResult(
                        doc_id=doc_id,
                        text=text,
                        similarity=similarity,
                        metadata=metadata,
                        distance=distance,
                    )
                )

        return search_results

    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from ChromaDB."""
        await self._ensure_initialized()

        try:
            self._collection.delete(ids=[doc_id])
            self._metadata_cache.pop(doc_id, None)
            return True
        except Exception:
            return False

    async def update_document(self, doc: VectorDocument) -> bool:
        """Update document in ChromaDB."""
        await self._ensure_initialized()

        try:
            self._metadata_cache[doc.doc_id] = {
                "text": doc.text,
                "source": doc.source,
                "timestamp": doc.timestamp.isoformat(),
                **doc.metadata,
            }

            self._collection.update(
                ids=[doc.doc_id],
                embeddings=[doc.vector],
                documents=[doc.text],
                metadatas=[
                    {
                        "source": doc.source,
                        "timestamp": doc.timestamp.isoformat(),
                        **doc.metadata,
                    }
                ],
            )
            return True
        except Exception:
            return False

    async def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Retrieve document by ID from ChromaDB."""
        await self._ensure_initialized()

        try:
            result = self._collection.get(
                ids=[doc_id],
                include=["embeddings", "documents", "metadatas"],
            )

            if result and result["ids"] and len(result["ids"]) > 0:
                metadata = result["metadatas"][0] if result["metadatas"] else {}
                timestamp_str = metadata.pop("timestamp", None)
                timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now(timezone.utc)

                return VectorDocument(
                    doc_id=doc_id,
                    text=result["documents"][0] if result["documents"] else "",
                    vector=result["embeddings"][0] if result["embeddings"] else [],
                    metadata=metadata,
                    timestamp=timestamp,
                    source=metadata.get("source", ""),
                )
        except Exception:
            pass

        return None

    async def list_documents(
        self,
        source_filter: Optional[str] = None,
        limit: int = 100,
    ) -> List[VectorDocument]:
        """List documents in ChromaDB."""
        await self._ensure_initialized()

        try:
            where_filter = None
            if source_filter:
                where_filter = {"source": {"$eq": source_filter}}

            result = self._collection.get(
                where=where_filter,
                limit=limit,
                include=["embeddings", "documents", "metadatas"],
            )

            docs = []
            if result and result["ids"]:
                for i, doc_id in enumerate(result["ids"]):
                    metadata = result["metadatas"][i] if result["metadatas"] else {}
                    timestamp_str = metadata.pop("timestamp", None)
                    timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now(timezone.utc)

                    docs.append(
                        VectorDocument(
                            doc_id=doc_id,
                            text=result["documents"][i] if result["documents"] else "",
                            vector=result["embeddings"][i] if result["embeddings"] else [],
                            metadata=metadata,
                            timestamp=timestamp,
                            source=metadata.get("source", ""),
                        )
                    )

            return docs
        except Exception:
            return []

    async def clear(self) -> None:
        """Clear all documents from ChromaDB."""
        await self._ensure_initialized()

        try:
            # Delete collection and recreate
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._metadata_cache.clear()
        except Exception:
            pass

    async def get_stats(self) -> Dict[str, Any]:
        """Get ChromaDB collection statistics."""
        await self._ensure_initialized()

        try:
            result = self._collection.get(limit=1, include=[])
            count = len(result.get("ids", []))

            return {
                "type": "chromadb",
                "collection": self.collection_name,
                "total_documents": count,
                "persist_dir": self.persist_dir,
                "metadata_cache_size": len(self._metadata_cache),
            }
        except Exception:
            return {"type": "chromadb", "error": "unable to get stats"}

    # Legacy methods
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents (legacy)."""
        for doc in documents:
            vector_doc = VectorDocument(
                doc_id=doc.get("id", ""),
                text=doc.get("content", ""),
                vector=doc.get("embedding", []),
                metadata=doc.get("metadata", {}),
                timestamp=datetime.now(timezone.utc),
                source=doc.get("source", ""),
            )
            asyncio.run(self.add_document(vector_doc))

    def search_legacy(
        self,
        query: str,
        limit: int = 5,
        filter: Optional[Dict] = None,
    ) -> List[VectorSearchResult]:
        """Search (legacy)."""
        # Would need embedding model to search by text
        return []

    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents (legacy)."""
        for doc_id in doc_ids:
            asyncio.run(self.delete_document(doc_id))

    def persist(self) -> None:
        """Persist to disk (legacy - ChromaDB handles automatically)."""
        pass
