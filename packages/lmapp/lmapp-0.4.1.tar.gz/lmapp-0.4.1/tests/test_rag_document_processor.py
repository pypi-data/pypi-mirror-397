"""Unit tests for RAG document processing."""

import pytest
from pathlib import Path

from lmapp.rag.document_processor import (
    Chunk,
    DocumentProcessorRegistry,
    MarkdownProcessor,
    PlainTextProcessor,
    SlidingWindowChunking,
)


class TestSlidingWindowChunking:
    """Test sliding window chunking strategy."""

    def test_chunk_short_text(self):
        """Test chunking short text."""
        strategy = SlidingWindowChunking(window_size=10, overlap=2)
        text = "This is a short text. It has two sentences."

        chunks = strategy.chunk(text, "test.txt")

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.total_chunks == len(chunks) for c in chunks)

    def test_chunk_medium_text(self):
        """Test chunking medium-sized text."""
        strategy = SlidingWindowChunking(window_size=50, overlap=10)
        text = " ".join(["Sentence number {}.".format(i) for i in range(20)])

        chunks = strategy.chunk(text, "test.txt")

        assert len(chunks) > 1
        # Verify metadata
        for chunk in chunks:
            assert chunk.metadata["window_size"] == 50
            assert chunk.metadata["overlap"] == 10

    def test_chunk_preserves_source(self):
        """Test that source is preserved in chunks."""
        strategy = SlidingWindowChunking()
        source = "document.md"

        chunks = strategy.chunk("Text. More text.", source)

        assert all(c.source == source for c in chunks)

    def test_chunk_indexing(self):
        """Test chunk indexing is correct."""
        strategy = SlidingWindowChunking()
        chunks = strategy.chunk(" ".join(["Sentence."] * 10), "test.txt")

        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))


class TestMarkdownProcessor:
    """Test Markdown document processor."""

    def test_supports_markdown_files(self):
        """Test Markdown file detection."""
        processor = MarkdownProcessor()

        assert processor.supports("doc.md") is True
        assert processor.supports("file.markdown") is True
        assert processor.supports("other.txt") is False

    def test_process_markdown_file(self, tmp_path):
        """Test processing Markdown file."""
        processor = MarkdownProcessor()

        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Title\n\nThis is content. More content.")

        chunks = processor.process(str(test_file))

        assert len(chunks) > 0
        assert all(c.metadata["file_type"] == "markdown" for c in chunks)

    def test_process_markdown_with_metadata(self, tmp_path):
        """Test processing Markdown with metadata."""
        processor = MarkdownProcessor()

        test_file = tmp_path / "test.md"
        content = "# Title\n\nContent here."
        test_file.write_text(content)

        chunks = processor.process(str(test_file))

        assert len(chunks) > 0


class TestPlainTextProcessor:
    """Test plain text document processor."""

    def test_supports_text_files(self):
        """Test text file detection."""
        processor = PlainTextProcessor()

        assert processor.supports("doc.txt") is True
        assert processor.supports("file.text") is True
        assert processor.supports("other.md") is False

    def test_process_text_file(self, tmp_path):
        """Test processing text file."""
        processor = PlainTextProcessor()

        test_file = tmp_path / "test.txt"
        test_file.write_text("First line. Second line. Third line.")

        chunks = processor.process(str(test_file))

        assert len(chunks) > 0
        assert all(c.metadata["file_type"] == "text" for c in chunks)


class TestDocumentProcessorRegistry:
    """Test document processor registry."""

    def test_registry_selection(self, tmp_path):
        """Test automatic processor selection."""
        registry = DocumentProcessorRegistry()

        # Test Markdown
        md_file = tmp_path / "test.md"
        md_file.write_text("# Markdown content")
        md_chunks = registry.process(str(md_file))

        assert len(md_chunks) > 0
        assert all(c.metadata["file_type"] == "markdown" for c in md_chunks)

        # Test Text
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Plain text content")
        txt_chunks = registry.process(str(txt_file))

        assert len(txt_chunks) > 0
        assert all(c.metadata["file_type"] == "text" for c in txt_chunks)

    def test_unknown_format(self, tmp_path):
        """Test handling of unknown file format."""
        registry = DocumentProcessorRegistry()

        unknown_file = tmp_path / "test.xyz"
        unknown_file.write_text("Unknown content")

        chunks = registry.process(str(unknown_file))

        # Should return empty list for unknown format
        assert len(chunks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
