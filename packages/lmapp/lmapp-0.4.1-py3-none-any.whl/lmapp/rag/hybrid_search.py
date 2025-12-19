"""Hybrid search combining semantic and keyword search."""

import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class SearchRanking:
    """Result ranking with combined scores."""

    doc_id: str
    semantic_score: float
    keyword_score: float
    combined_score: float
    content_preview: str


class KeywordSearcher(ABC):
    """Abstract keyword search interface."""

    @abstractmethod
    def search(self, query: str, documents: List[str], k: int = 5) -> List[Tuple[int, float]]:
        """Search documents by keywords.

        Args:
            query: Search query
            documents: List of document texts
            k: Number of results

        Returns:
            List of (doc_index, score) tuples
        """
        pass


class BM25Searcher(KeywordSearcher):
    """Simple BM25 keyword search implementation."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.idf_cache = {}

    def search(self, query: str, documents: List[str], k: int = 5) -> List[Tuple[int, float]]:
        """BM25 search."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Calculate IDF for query terms
        doc_freqs = self._get_doc_freqs(documents)
        n_docs = len(documents)

        scores = []
        for doc_idx, doc in enumerate(documents):
            score = self._bm25_score(query_tokens, doc, doc_freqs, n_docs)
            scores.append((doc_idx, score))

        # Sort by score and return top k
        scores.sort(key=lambda x: -x[1])
        return scores[:k]

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Convert to lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r"\w+", text)
        # Remove common stopwords
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        return [t for t in tokens if t not in stopwords]

    def _get_doc_freqs(self, documents: List[str]) -> dict:
        """Get document frequencies for each token."""
        freqs = {}
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                freqs[token] = freqs.get(token, 0) + 1
        return freqs

    def _bm25_score(self, query_tokens: List[str], doc: str, doc_freqs: dict, n_docs: int) -> float:
        """Calculate BM25 score."""
        doc_tokens = self._tokenize(doc)
        doc_len = len(doc_tokens)
        avg_doc_len = sum(len(self._tokenize(d)) for d in [doc]) / 1.0 or 1.0

        score = 0.0
        for token in query_tokens:
            # IDF calculation
            df = doc_freqs.get(token, 1)
            idf = (n_docs - df + 0.5) / (df + 0.5)

            # Term frequency in document
            tf = doc_tokens.count(token)

            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / (avg_doc_len or 1)))

            score += idf * (numerator / denominator)

        return score


class HybridSearcher:
    """Hybrid search combining semantic and keyword search."""

    def __init__(
        self,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        keyword_searcher: Optional[KeywordSearcher] = None,
    ):
        """Initialize hybrid searcher.

        Args:
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword match (0-1)
            keyword_searcher: Keyword search implementation
        """
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.keyword_searcher = keyword_searcher or BM25Searcher()

    def search(
        self,
        query: str,
        documents: List[str],
        semantic_scores: List[Tuple[int, float]],
        k: int = 5,
        fusion_method: str = "weighted",
    ) -> List[SearchRanking]:
        """Perform hybrid search.

        Args:
            query: Search query
            documents: List of document texts
            semantic_scores: Pre-computed semantic scores [(doc_idx, score), ...]
            k: Number of results
            fusion_method: Score fusion method (weighted, reciprocal_rank)

        Returns:
            List of SearchRanking results
        """
        # Get keyword scores
        keyword_results = self.keyword_searcher.search(query, documents, k=len(documents))
        keyword_scores = {doc_idx: score for doc_idx, score in keyword_results}

        # Normalize scores to [0, 1]
        semantic_scores_dict = self._normalize_scores({idx: score for idx, score in semantic_scores})
        keyword_scores = self._normalize_scores(keyword_scores)

        # Combine scores
        combined = {}
        all_docs = set(semantic_scores_dict.keys()) | set(keyword_scores.keys())

        for doc_idx in all_docs:
            sem_score = semantic_scores_dict.get(doc_idx, 0.0)
            kw_score = keyword_scores.get(doc_idx, 0.0)

            if fusion_method == "weighted":
                combined_score = self.semantic_weight * sem_score + self.keyword_weight * kw_score
            elif fusion_method == "reciprocal_rank":
                combined_score = self._reciprocal_rank_fusion(sem_score, kw_score)
            else:
                combined_score = (sem_score + kw_score) / 2.0

            combined[doc_idx] = {
                "semantic": sem_score,
                "keyword": kw_score,
                "combined": combined_score,
            }

        # Sort by combined score
        ranked = sorted(
            [(idx, scores["combined"]) for idx, scores in combined.items()],
            key=lambda x: -x[1],
        )

        # Create results
        results = []
        for doc_idx, _ in ranked[:k]:
            scores = combined[doc_idx]
            preview = documents[doc_idx][:100].replace("\n", " ") + "..."

            results.append(
                SearchRanking(
                    doc_id=str(doc_idx),
                    semantic_score=scores["semantic"],
                    keyword_score=scores["keyword"],
                    combined_score=scores["combined"],
                    content_preview=preview,
                )
            )

        return results

    def _normalize_scores(self, scores: dict) -> dict:
        """Normalize scores to [0, 1]."""
        if not scores:
            return {}

        max_score = max(scores.values())
        if max_score == 0:
            return {k: 0.0 for k in scores}

        return {k: v / max_score for k, v in scores.items()}

    def _reciprocal_rank_fusion(self, sem_score: float, kw_score: float) -> float:
        """Reciprocal rank fusion for score combination."""
        # Simple version using the scores directly
        return 2.0 / (1.0 / (sem_score + 1e-6) + 1.0 / (kw_score + 1e-6))
