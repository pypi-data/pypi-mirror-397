"""Citation tracking and source attribution for RAG."""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Citation:
    """Citation reference with metadata."""

    source: str
    doc_id: str
    chunk_index: int
    text: str
    similarity: float
    timestamp: datetime
    page: Optional[int] = None
    line_range: Optional[Tuple[int, int]] = None


@dataclass
class CitationContext:
    """Context around a citation."""

    quote: str
    full_text: str
    surrounding_context: str
    character_offset: int


@dataclass
class CitationChain:
    """Chain of citations for a response."""

    citations: List[Citation] = field(default_factory=list)
    sources: Set[str] = field(default_factory=set)
    source_weights: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_citation(self, citation: Citation) -> None:
        """Add citation to chain."""
        self.citations.append(citation)
        self.sources.add(citation.source)

        # Update source weights based on citation similarity
        if citation.source not in self.source_weights:
            self.source_weights[citation.source] = 0.0
        self.source_weights[citation.source] += citation.similarity

    def merge_citations(self, other: "CitationChain") -> "CitationChain":
        """Merge two citation chains."""
        merged = CitationChain()
        for citation in self.citations + other.citations:
            merged.add_citation(citation)
        return merged

    def get_sorted_sources(self) -> List[Tuple[str, float]]:
        """Get sources sorted by weight."""
        return sorted(
            self.source_weights.items(),
            key=lambda x: -x[1],
        )

    def get_citation_stats(self) -> Dict[str, any]:
        """Get citation statistics."""
        return {
            "total_citations": len(self.citations),
            "unique_sources": len(self.sources),
            "avg_similarity": (sum(c.similarity for c in self.citations) / len(self.citations) if self.citations else 0.0),
            "top_source": (self.get_sorted_sources()[0][0] if self.get_sorted_sources() else None),
            "sources": self.get_sorted_sources(),
        }


class CitationTracker:
    """Tracks and manages citations throughout RAG pipeline."""

    def __init__(self):
        """Initialize citation tracker."""
        self._active_chain: Optional[CitationChain] = None
        self._completed_chains: List[CitationChain] = []

    def start_chain(self) -> CitationChain:
        """Start new citation chain."""
        self._active_chain = CitationChain()
        return self._active_chain

    def add_citation(self, citation: Citation) -> None:
        """Add citation to active chain."""
        if self._active_chain is None:
            self.start_chain()
        self._active_chain.add_citation(citation)

    def finalize_chain(self) -> CitationChain:
        """Finalize and store active chain."""
        if self._active_chain is None:
            return CitationChain()

        chain = self._active_chain
        self._completed_chains.append(chain)
        self._active_chain = None
        return chain

    def format_citations(
        self,
        chain: CitationChain,
        format_type: str = "markdown",
    ) -> str:
        """Format citations for display.

        Args:
            chain: Citation chain to format
            format_type: Format type (markdown, html, plain)

        Returns:
            Formatted citation string
        """
        if not chain.citations:
            return ""

        if format_type == "markdown":
            return self._format_markdown(chain)
        elif format_type == "html":
            return self._format_html(chain)
        else:
            return self._format_plain(chain)

    def _format_markdown(self, chain: CitationChain) -> str:
        """Format citations as markdown."""
        lines = ["## Sources\n"]

        for i, citation in enumerate(chain.citations, 1):
            lines.append(
                f"{i}. **{citation.source}** "
                f"(Relevance: {citation.similarity:.2%})\n"
                f"   - Document ID: `{citation.doc_id}`\n"
                f"   - Chunk: {citation.chunk_index}\n"
            )

        return "".join(lines)

    def _format_html(self, chain: CitationChain) -> str:
        """Format citations as HTML."""
        lines = ["<div class='citations'>\n<h3>Sources</h3>\n<ol>\n"]

        for citation in chain.citations:
            lines.append(
                f"<li><strong>{citation.source}</strong> "
                f"(Relevance: {citation.similarity:.2%})<br/>"
                f"<code>{citation.doc_id}</code> Chunk {citation.chunk_index}</li>\n"
            )

        lines.append("</ol>\n</div>")
        return "".join(lines)

    def _format_plain(self, chain: CitationChain) -> str:
        """Format citations as plain text."""
        lines = ["Sources:\n"]

        for i, citation in enumerate(chain.citations, 1):
            lines.append(f"{i}. {citation.source} " f"(Relevance: {citation.similarity:.2%})\n")

        return "".join(lines)

    def get_stats(self) -> Dict[str, any]:
        """Get tracker statistics."""
        all_chains = self._completed_chains
        if self._active_chain:
            all_chains = self._completed_chains + [self._active_chain]

        total_citations = sum(len(c.citations) for c in all_chains)

        return {
            "completed_chains": len(self._completed_chains),
            "active_chain": self._active_chain is not None,
            "total_citations": total_citations,
            "avg_citations_per_chain": (total_citations / len(all_chains) if all_chains else 0.0),
        }

    def clear(self) -> None:
        """Clear all tracked citations."""
        self._active_chain = None
        self._completed_chains.clear()
