"""Document processing and chunking for RAG."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class Chunk:
    """A chunk of processed document content."""

    text: str
    source: str
    chunk_index: int
    total_chunks: int
    metadata: Optional[dict] = None


class DocumentProcessor(ABC):
    """Abstract base for document processors."""

    @abstractmethod
    def extract_chunks(self, file_path: str) -> List[Chunk]:
        """Process document file.

        Args:
            file_path: Path to document

        Returns:
            List of text chunks
        """
        pass

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Check if processor supports file type.

        Args:
            file_path: Path to document

        Returns:
            True if processor can handle this file
        """
        pass


class ChunkingStrategy(ABC):
    """Abstract strategy for chunking text."""

    @abstractmethod
    def chunk(self, text: str, source: str) -> List[Chunk]:
        """Split text into chunks.

        Args:
            text: Text to chunk
            source: Source file reference

        Returns:
            List of text chunks
        """
        pass


class SlidingWindowChunking(ChunkingStrategy):
    """Chunk text using sliding window with overlap."""

    def __init__(self, window_size: int = 512, overlap: int = 50):
        """Initialize sliding window chunking.

        Args:
            window_size: Size of each chunk in tokens (approx)
            overlap: Overlap between chunks
        """
        self.window_size = window_size
        self.overlap = overlap

    def chunk(self, text: str, source: str) -> List[Chunk]:
        """Chunk text with sliding window."""
        # Simple token-like split on sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks_list = []
        current_chunk = []
        current_size = 0

        for i, sentence in enumerate(sentences):
            tokens = len(sentence.split())

            if current_size + tokens > self.window_size and current_chunk:
                # Flush current chunk
                chunk_text = " ".join(current_chunk)
                chunks_list.append(
                    Chunk(
                        text=chunk_text,
                        source=source,
                        chunk_index=len(chunks_list),
                        total_chunks=0,  # Will update after full pass
                        metadata={"window_size": self.window_size, "overlap": self.overlap},
                    )
                )

                # Keep overlap
                overlap_items = max(1, len(current_chunk) // 2)
                current_chunk = current_chunk[-overlap_items:]
                current_size = sum(len(s.split()) for s in current_chunk)

            current_chunk.append(sentence)
            current_size += tokens

        # Final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks_list.append(
                Chunk(
                    text=chunk_text,
                    source=source,
                    chunk_index=len(chunks_list),
                    total_chunks=0,
                    metadata={"window_size": self.window_size, "overlap": self.overlap},
                )
            )

        # Update total chunks count
        total = len(chunks_list)
        for chunk in chunks_list:
            chunk.total_chunks = total

        return chunks_list


class MarkdownProcessor(DocumentProcessor):
    """Process Markdown files."""

    def __init__(self, chunking_strategy: Optional[ChunkingStrategy] = None):
        self.chunking_strategy = chunking_strategy or SlidingWindowChunking()

    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith((".md", ".markdown"))

    def extract_chunks(self, file_path: str) -> List[Chunk]:
        """Process Markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract metadata from frontmatter if present
            metadata = {}
            if content.startswith("---"):
                lines = content.split("\n")
                end_idx = 0
                for i, line in enumerate(lines[1:], 1):
                    if line.startswith("---"):
                        end_idx = i + 1
                        break
                if end_idx > 0:
                    # TODO: Parse YAML frontmatter
                    content = "\n".join(lines[end_idx:])

            # Chunk content
            chunks = self.chunking_strategy.chunk(content, file_path)

            # Add metadata to each chunk
            for chunk in chunks:
                if not chunk.metadata:
                    chunk.metadata = {}
                chunk.metadata.update(metadata)
                chunk.metadata["file_type"] = "markdown"

            return chunks
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []


class PlainTextProcessor(DocumentProcessor):
    """Process plain text files."""

    def __init__(self, chunking_strategy: Optional[ChunkingStrategy] = None):
        self.chunking_strategy = chunking_strategy or SlidingWindowChunking()

    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith((".txt", ".text"))

    def extract_chunks(self, file_path: str) -> List[Chunk]:
        """Process plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = self.chunking_strategy.chunk(content, file_path)

            for chunk in chunks:
                if not chunk.metadata:
                    chunk.metadata = {}
                chunk.metadata["file_type"] = "text"

            return chunks
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []


class DocumentProcessorRegistry:
    """Registry of available document processors."""

    def __init__(self):
        self.processors: List[DocumentProcessor] = [
            MarkdownProcessor(),
            PlainTextProcessor(),
        ]

    def process_document(self, file_path: str) -> List[Chunk]:
        """Process document with appropriate processor.

        Args:
            file_path: Path to document

        Returns:
            List of chunks
        """
        for processor in self.processors:
            if processor.supports(file_path):
                return processor.extract_chunks(file_path)

        print(f"No processor found for: {file_path}")
        return []

    def register(self, processor: DocumentProcessor) -> None:
        """Register a custom processor."""
        self.processors.insert(0, processor)  # Higher priority
