"""
ChromaDB Adapter for LMAPP RAG.
"""

import logging
from typing import List, Dict, Any, Optional
import uuid

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    chromadb = None

from .vector_store import VectorStore, VectorSearchResult

logger = logging.getLogger(__name__)


class ChromaDBStore(VectorStore):
    """ChromaDB implementation of VectorStore."""

    def __init__(self, persist_path: str, collection_name: str = "lmapp_docs"):
        if chromadb is None:
            raise ImportError("chromadb is not installed. Run: pip install chromadb")

        self.client = chromadb.PersistentClient(path=persist_path)

        # Use default SentenceTransformer embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

        self.collection = self.client.get_or_create_collection(name=collection_name, embedding_function=self.embedding_fn)

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to ChromaDB.
        Expects dicts with: content, metadata, id (optional)
        """
        ids = []
        documents_text = []
        metadatas = []

        for doc in documents:
            doc_id = doc.get("doc_id") or str(uuid.uuid4())
            ids.append(doc_id)
            documents_text.append(doc["content"])
            # Ensure metadata is flat and valid types
            meta = doc.get("metadata", {}).copy()
            # Add title to metadata if present in doc root
            if "title" in doc:
                meta["title"] = doc["title"]
            metadatas.append(meta)

        if ids:
            self.collection.add(ids=ids, documents=documents_text, metadatas=metadatas)
            logger.debug(f"Added {len(ids)} documents to ChromaDB")

    def search(self, query: str, limit: int = 5, filter: Optional[Dict] = None) -> List[VectorSearchResult]:
        """Search ChromaDB."""
        results = self.collection.query(query_texts=[query], n_results=limit, where=filter)

        # Chroma returns lists of lists (one per query)
        if not results["ids"]:
            return []

        search_results = []
        # We only sent one query, so take the first list
        ids = results["ids"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        documents = results["documents"][0]

        for i in range(len(ids)):
            # Convert distance to similarity score (approximate)
            # Chroma uses L2 distance by default (lower is better)
            # Simple inversion for score: 1 / (1 + distance)
            score = 1 / (1 + distances[i])

            search_results.append(VectorSearchResult(doc_id=ids[i], score=score, metadata=metadatas[i], content=documents[i]))

        return search_results

    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents."""
        self.collection.delete(ids=doc_ids)

    def persist(self) -> None:
        """ChromaDB persists automatically."""
        pass
