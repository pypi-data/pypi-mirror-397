"""
RAG (Retrieval-Augmented Generation) system for LMAPP v0.3.2.

Enables LMAPP to search local files and inject relevant context into LLM prompts.
Supports semantic search with simple vector similarity and file-based retrieval.

Features:
- Vector-based semantic search using embedding similarity
- Local file indexing (text, markdown, code)
- Automatic relevance ranking
- Context injection into system prompts
- Integration with CRECALL for knowledge base search
- Smart Chunking for better context retrieval
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import hashlib
import logging

from .models import Document, SearchResult
from .vector_store import VectorStore
from .chroma_store import ChromaDBStore
from .ingestion import DocumentIngestor

logger = logging.getLogger(__name__)


class Chunker:
    """Splits text into manageable chunks."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize Chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size

            # If we are not at the end, try to find a natural break point
            if end < text_len:
                # Look for paragraph break
                last_break = text.rfind("\n\n", start, end)
                if last_break != -1:
                    end = last_break + 2
                else:
                    # Look for sentence break
                    last_period = text.rfind(". ", start, end)
                    if last_period != -1:
                        end = last_period + 2
                    else:
                        # Look for space
                        last_space = text.rfind(" ", start, end)
                        if last_space != -1:
                            end = last_space + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start forward, accounting for overlap
            start = end - self.overlap

            # Ensure we always move forward
            if start >= end:
                start = end

        return chunks


class SimpleVectorizer:
    """Simple vectorizer using TF-IDF-like approach without external dependencies."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words."""
        import re

        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens

    @staticmethod
    def get_term_frequency(tokens: List[str]) -> Dict[str, float]:
        """Calculate term frequency."""
        if not tokens:
            return {}

        freq: Dict[str, int] = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1

        # Normalize by total tokens
        total = len(tokens)
        return {token: count / total for token, count in freq.items()}

    @staticmethod
    def calculate_similarity(query_tokens: List[str], doc_tokens: List[str]) -> float:
        """
        Calculate similarity between query and document using simple overlap.

        Returns a score from 0.0 to 1.0.
        """
        if not query_tokens or not doc_tokens:
            return 0.0

        query_set = set(query_tokens)
        doc_set = set(doc_tokens)

        if not query_set or not doc_set:
            return 0.0

        # Jaccard similarity
        intersection = len(query_set & doc_set)
        union = len(query_set | doc_set)

        jaccard = intersection / union if union > 0 else 0.0

        # Boost score if query terms appear in order
        doc_text = " ".join(doc_tokens)
        query_text = " ".join(query_tokens)
        sequential_boost = 1.0

        if query_text in doc_text:
            sequential_boost = 1.5

        return min(1.0, jaccard * sequential_boost)


class DocumentIndex:
    """Index for documents with search capabilities."""

    def __init__(self, index_dir: Optional[Path] = None):
        """
        Initialize DocumentIndex.

        Args:
            index_dir: Directory to store index (default: ~/.lmapp/index/)
        """
        if index_dir is None:
            home = Path.home()
            index_dir = home / ".lmapp" / "index"

        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.documents_file = self.index_dir / "documents.jsonl"
        self.documents: Dict[str, Document] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load documents from index file."""
        if not self.documents_file.exists():
            return

        try:
            with open(self.documents_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        doc = Document.from_dict(data)
                        self.documents[doc.doc_id] = doc
        except (json.JSONDecodeError, IOError):
            pass

    def _save_index(self) -> None:
        """Save documents to index file."""
        with open(self.documents_file, "w") as f:
            for doc in self.documents.values():
                f.write(json.dumps(doc.to_dict()) + "\n")

    def add_document(self, document: Document) -> None:
        """Add a document to the index."""
        self.documents[document.doc_id] = document
        self._save_index()

    def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents."""
        for doc in documents:
            self.documents[doc.doc_id] = doc
        self._save_index()

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(doc_id)

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from index."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_index()
            return True
        return False

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search documents using semantic similarity.

        Args:
            query: Search query
            top_k: Return top K results

        Returns:
            List of SearchResult sorted by relevance
        """
        if not query or not self.documents:
            return []

        query_tokens = SimpleVectorizer.tokenize(query)
        results = []

        for doc in self.documents.values():
            doc_tokens = SimpleVectorizer.tokenize(doc.content)
            score = SimpleVectorizer.calculate_similarity(query_tokens, doc_tokens)

            if score > 0.0:
                # Find matched text excerpt
                matched_text = self._extract_matched_text(query_tokens, doc.content)
                result = SearchResult(
                    document=doc,
                    relevance_score=score,
                    matched_text=matched_text,
                )
                results.append(result)

        # Sort by score descending
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def _extract_matched_text(self, query_tokens: List[str], content: str, window: int = 50) -> str:
        """Extract a snippet of text around the first match."""
        content_lower = content.lower()

        # Find first occurrence of any query token
        first_pos = -1
        for token in query_tokens:
            pos = content_lower.find(token)
            if pos != -1:
                if first_pos == -1 or pos < first_pos:
                    first_pos = pos

        if first_pos == -1:
            return content[:100] + "..."

        start = max(0, first_pos - window)
        end = min(len(content), first_pos + window)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet


class RAGSystem:
    """Main RAG system controller."""

    def __init__(self, index_dir: Optional[Path] = None):
        """
        Initialize RAG System.

        Args:
            index_dir: Directory to store index
        """
        if index_dir is None:
            home = Path.home()
            index_dir = home / ".lmapp" / "index"

        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.chunker = Chunker()
        self.ingestor = DocumentIngestor()

        # Try to initialize VectorStore (ChromaDB), fallback to SimpleIndex
        self.vector_store: Optional[VectorStore] = None
        try:
            self.vector_store = ChromaDBStore(str(self.index_dir / "chroma"))
            logger.info("Initialized ChromaDB Vector Store")
        except ImportError:
            logger.warning("ChromaDB not available, falling back to SimpleIndex")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

        # Always keep SimpleIndex for fallback/hybrid
        self.simple_index = DocumentIndex(self.index_dir)

    @property
    def index(self) -> DocumentIndex:
        """Alias for simple_index for backward compatibility."""
        return self.simple_index

    def index_file(self, file_path: Path) -> Optional[str]:
        """
        Index a single file.

        Args:
            file_path: Path to file to index

        Returns:
            Document ID if successful, None otherwise
        """
        try:
            # Use ingestor to load file
            doc = self.ingestor.load_file(str(file_path))
            if not doc:
                return None

            # Chunk the content
            chunks = self.chunker.chunk_text(doc.content)
            first_chunk_id = None

            # Prepare documents for vector store
            vector_docs = []

            for i, chunk_content in enumerate(chunks):
                chunk_id = f"{doc.doc_id}_chunk_{i}"
                if i == 0:
                    first_chunk_id = chunk_id

                chunk_doc = Document(
                    doc_id=chunk_id,
                    title=f"{doc.title} (Part {i+1})",
                    content=chunk_content,
                    file_path=doc.file_path,
                    source_type=doc.source_type,
                    metadata=doc.metadata,
                    parent_id=doc.doc_id,
                    chunk_index=i,
                )

                # Add to Simple Index
                self.simple_index.add_document(chunk_doc)

                # Prepare for Vector Store
                vector_docs.append(
                    {
                        "doc_id": chunk_id,
                        "content": chunk_content,
                        "metadata": {"title": doc.title, "file_path": str(doc.file_path), "source_type": doc.source_type, "chunk_index": i},
                    }
                )

            # Add to Vector Store if available
            if self.vector_store and vector_docs:
                self.vector_store.add_documents(vector_docs)

            return first_chunk_id

        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            return None

    def index_directory(self, directory: Path, extensions: Optional[List[str]] = None) -> int:
        """
        Index all files in a directory.

        Args:
            directory: Directory to index
            extensions: File extensions to index (default: common text/code formats)

        Returns:
            Number of files indexed
        """
        if extensions is None:
            extensions = [".txt", ".md", ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".json", ".yaml", ".yml", ".xml", ".html", ".css", ".pdf", ".docx"]

        indexed_count = 0

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                if self.index_file(file_path):
                    indexed_count += 1

        return indexed_count

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search the document index using Hybrid Search (Vector + Keyword).

        Args:
            query: Search query
            top_k: Return top K results

        Returns:
            List of SearchResult
        """
        results = []
        seen_ids = set()

        # 1. Vector Search (Semantic)
        if self.vector_store:
            try:
                vector_results = self.vector_store.search(query, limit=top_k)
                for vr in vector_results:
                    # Convert VectorSearchResult to SearchResult
                    # We need to fetch the full document from simple_index to get full details if needed
                    # But VectorSearchResult has content, so we can reconstruct a partial Document
                    doc = Document(
                        doc_id=vr.doc_id,
                        title=vr.metadata.get("title", "Unknown"),
                        content=vr.content or "",
                        file_path=vr.metadata.get("file_path"),
                        source_type=vr.metadata.get("source_type", "text"),
                        metadata=vr.metadata,
                    )

                    snippet = vr.content[:200] + "..." if vr.content else "..."
                    results.append(SearchResult(document=doc, relevance_score=vr.score, matched_text=snippet))  # Normalize if needed  # Simple snippet
                    seen_ids.add(vr.doc_id)
            except Exception as e:
                logger.error(f"Vector search failed: {e}")

        # 2. Keyword Search (Fallback/Hybrid)
        # If we have enough results from vector search, we might skip this or mix them
        # For now, let's fill up the remaining slots with keyword search
        remaining = top_k - len(results)
        if remaining > 0:
            keyword_results = self.simple_index.search(query, top_k=top_k)
            for kr in keyword_results:
                if kr.document.doc_id not in seen_ids:
                    results.append(kr)
                    seen_ids.add(kr.document.doc_id)

        # Re-sort combined results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def get_context_for_prompt(self, query: str, max_context_length: int = 2000) -> str:
        """
        Get context string to inject into system prompt.

        Args:
            query: Query to search for
            max_context_length: Maximum characters to include

        Returns:
            Context string ready for prompt injection
        """
        results = self.search(query, top_k=5)

        if not results:
            return ""

        context_parts = []
        total_length = 0

        for result in results:
            # Use the chunk content directly
            doc_context = f"Source: {result.document.title}\n{result.document.content}"

            if total_length + len(doc_context) <= max_context_length:
                context_parts.append(doc_context)
                total_length += len(doc_context)
            else:
                break

        if context_parts:
            return "\n\n---\n\n".join(context_parts)

        return ""

    def clear_index(self) -> None:
        """Clear all indexed documents."""
        self.simple_index.documents.clear()
        self.simple_index._save_index()
        if self.vector_store:
            # Chroma doesn't have a simple clear, usually delete collection
            # For now, we just rely on simple index clearing or implement delete_all later
            pass

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        total_docs = len(self.simple_index.documents)
        total_content_size = sum(len(doc.content) for doc in self.simple_index.documents.values())

        return {
            "total_documents": total_docs,
            "total_content_size": total_content_size,
            "average_doc_size": (total_content_size // total_docs if total_docs > 0 else 0),
            "vector_store_active": self.vector_store is not None,
        }

    @staticmethod
    def _generate_doc_id(file_path: Path) -> str:
        """Generate a unique document ID."""
        path_str = str(file_path.absolute())
        return hashlib.md5(path_str.encode()).hexdigest()[:12]

    @staticmethod
    def _detect_source_type(file_path: Path) -> str:
        """Detect source type based on file extension."""
        suffix = file_path.suffix.lower()

        if suffix in [".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go", ".rs"]:
            return "code"
        elif suffix in [".md", ".rst"]:
            return "markdown"
        elif suffix in [".html", ".htm"]:
            return "html"
        elif suffix in [".json", ".yaml", ".yml", ".xml"]:
            return "config"
        else:
            return "text"


# Global RAG system instance
_rag_system: Optional[RAGSystem] = None


def get_rag_system(index_dir: Optional[Path] = None) -> RAGSystem:
    """Get or create the global RAGSystem instance."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem(index_dir)
    return _rag_system
