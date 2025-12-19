"""
Epistemic Uncertainty Detection for LLM Responses.

Cross-references linguistic markers with RAG retrieval confidence
to identify hallucination risk.

Core insight: confident language + weak retrieval = danger zone.

Theoretical Foundation:
    Ternary Logic:
        Lukasiewicz, J. (1920). On Three-Valued Logic. Ruch Filozoficzny.
        Brusentsov, N.P. (1960). Setun: Ternary Computer. Moscow State University.

    Epistemic Modality:
        Palmer, F.R. (2001). Mood and Modality (2nd ed.). Cambridge University Press.
        Nuyts, J. (2001). Epistemic Modality, Language, and Conceptualization.
            John Benjamins Publishing.

    LLM Calibration & Hallucination:
        Kadavath et al. (2022). Language Models (Mostly) Know What They Know.
            arXiv:2207.05221.
        Ji et al. (2023). Survey of Hallucination in Natural Language Generation.
            ACM Computing Surveys, 55(12).
"""

import re
from typing import Dict, Any, List, Optional, Tuple

from .state import EpistemicState, TernaryState
from .languages import get_markers, available_languages


def calculate_retrieval_confidence(chunks: List[Dict[str, Any]]) -> Tuple[float, int]:
    """
    Calculate aggregate confidence from RAG retrieval results.
    Uses rank-weighted mean of top chunks relevance scores.
    """
    if not chunks:
        return 0.0, 0

    top_chunks = chunks[:5]
    scores = []

    for chunk in top_chunks:
        if "relevance" in chunk and chunk["relevance"] is not None:
            scores.append(float(chunk["relevance"]))
        elif "distance" in chunk and chunk["distance"] is not None:
            scores.append(max(0.0, min(1.0, 1.0 - float(chunk["distance"]))))
        elif "score" in chunk and chunk["score"] is not None:
            score = float(chunk["score"])
            scores.append(min(1.0, score / 10.0) if score > 1.0 else score)
        elif "similarity" in chunk and chunk["similarity"] is not None:
            scores.append(float(chunk["similarity"]))

    if not scores:
        return 0.0, len(chunks)

    weights = [1.0 - (i * 0.15) for i in range(len(scores))]
    confidence = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

    return min(1.0, max(0.0, confidence)), len(chunks)

class EpistemicDetector:
    """
    Detects epistemic uncertainty using ternary logic.

    States (following Lukasiewicz three-valued logic):
        CONFIDENT (+1): Response grounded in evidence
        UNCERTAIN (0): Insufficient evidence, should abstain
        OVERCONFIDENT (-1): Confident without grounding (hallucination risk)

    The -1 state is key: it catches confident responses lacking evidence.
    """

    def __init__(
        self,
        language: str = "en",
        threshold_confident: float = 0.7,
        threshold_uncertain: float = 0.3,
        min_retrieval_confidence: float = 0.3,
        custom_markers: Optional[Dict[str, List[str]]] = None,
    ):
        self.language = language
        self.threshold_confident = threshold_confident
        self.threshold_uncertain = threshold_uncertain
        self.min_retrieval_confidence = min_retrieval_confidence

        markers = custom_markers if custom_markers else get_markers(language)

        def compile_patterns(key):
            return [re.compile(p, re.IGNORECASE) for p in markers.get(key, [])]

        self._uncertainty_patterns = compile_patterns("uncertainty")
        self._overconfidence_patterns = compile_patterns("overconfidence")
        self._fabrication_patterns = compile_patterns("fabrication")
        self._unanswerable_patterns = compile_patterns("unanswerable")
        self._speculation_patterns = compile_patterns("speculation")
        self._falsehood_patterns = compile_patterns("falsehood")
        self._hallucination_flag_patterns = compile_patterns("hallucination_flags")

        self._weighted_uncertainty = [
            (re.compile(p, re.IGNORECASE), w)
            for p, w in markers.get("uncertainty_weighted", [])
        ]

    def _count_matches(self, patterns, text):
        """Count matches across multiple patterns."""
        count, found = 0, []
        for p in patterns:
            matches = p.findall(text)
            if matches:
                count += len(matches)
                found.extend(matches[:2])
        return count, found

    def _calculate_weighted_uncertainty(self, text):
        """Calculate weighted uncertainty per Lakoff (1973) hedge categories."""
        text_lower = text.lower()
        total_weight, markers = 0, []
        max_weight = len(self._weighted_uncertainty) * 3

        for pattern, weight in self._weighted_uncertainty:
            matches = pattern.findall(text_lower)
            if matches:
                total_weight += weight * len(matches)
                markers.extend(matches[:2])

        return min(1.0, total_weight / max(max_weight * 0.3, 1)), markers

    def _detect_contradiction(self, text):
        """Detect self-contradictions (affirmation + negation pairs)."""
        text_lower = text.lower()
        pairs = [
            ("is", "is not"), ("can", "cannot"), ("will", "will not"),
            ("does", "does not"), ("true", "false"), ("correct", "incorrect"),
        ]
        return any(
            re.search(a, text_lower) and re.search(n, text_lower)
            for a, n in pairs
        )

    def _check_hallucination_flags(self, text):
        """Count suspicious specificity per Ji et al. (2023)."""
        return sum(len(p.findall(text.lower())) for p in self._hallucination_flag_patterns)

    def _any_match(self, patterns, text):
        """Check if any pattern matches."""
        return any(p.search(text.lower()) for p in patterns)

    def should_abstain_on_question(self, question):
        """Check if question is inherently unanswerable."""
        if self._any_match(self._unanswerable_patterns, question):
            return True, "Question asks for prediction or unknowable information"
        return False, ""

    def analyze(
        self,
        text: str,
        question: str = "",
        retrieval_confidence: Optional[float] = None,
        chunks_found: Optional[int] = None
    ) -> EpistemicState:
        """
        Analyze text for epistemic uncertainty with optional RAG grounding.
        Priority follows evidentialist epistemology: evidence quality (RAG)
        takes precedence over linguistic signals.
        """
        text_lower = text.lower().strip()
        markers = []

        # Trivial response
        if len(text_lower) <= 3:
            return EpistemicState(
                state=TernaryState.UNCERTAIN, confidence=0.0, should_abstain=True,
                reason="Response is empty or trivial", markers_found=["empty_response"],
                retrieval_confidence=retrieval_confidence, chunks_found=chunks_found,
                grounded=False
            )

        # Linguistic analysis
        unc_count, unc_markers = self._count_matches(self._uncertainty_patterns, text_lower)
        markers.extend(unc_markers)

        weighted_unc, weighted_markers = self._calculate_weighted_uncertainty(text)
        markers.extend(weighted_markers)

        overconf_count = sum(1 for p in self._overconfidence_patterns if p.search(text_lower))

        fabrication = self._any_match(self._fabrication_patterns, text_lower)
        if fabrication:
            markers.append("fabrication_marker")

        spec_count, spec_markers = self._count_matches(self._speculation_patterns, text_lower)
        markers.extend(spec_markers)

        correcting = self._any_match(self._falsehood_patterns, text_lower)
        if correcting:
            markers.append("falsehood_correction")

        halluc_flags = self._check_hallucination_flags(text)
        if halluc_flags > 3:
            markers.append(f"suspicious_specificity:{halluc_flags}")

        contradiction = self._detect_contradiction(text)
        if contradiction:
            markers.append("self_contradiction")

        is_short = len(text.split()) < 5
        if is_short:
            markers.append("short_response")

        unanswerable = False
        if question and self._any_match(self._unanswerable_patterns, question):
            unanswerable = True
            markers.append("unanswerable_question")

        # Calculate linguistic confidence
        text_len = len(text.split())
        norm_unc = max(unc_count / max(text_len / 50, 1), weighted_unc)
        ling_conf = 1.0 - min(norm_unc, 1.0)

        if overconf_count > 2:
            ling_conf = min(1.0, ling_conf + 0.3)
        if halluc_flags > 3 and overconf_count > 0:
            ling_conf = max(0.0, ling_conf - 0.2)
        if correcting:
            ling_conf = min(1.0, ling_conf + 0.1)

        # RAG grounding
        has_rag = retrieval_confidence is not None
        rag_weak = has_rag and retrieval_confidence < self.threshold_uncertain
        rag_strong = has_rag and retrieval_confidence >= self.threshold_confident
        rag_medium = has_rag and self.threshold_uncertain <= retrieval_confidence < self.threshold_confident
        no_chunks = chunks_found is not None and chunks_found == 0

        # State determination (priority order)
        if unanswerable:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, 0.1,
                "Question requires prediction or unknowable information", False)
        elif no_chunks:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, 0.0,
                "No relevant context found", False)
            markers.append("no_rag_context")
        elif rag_weak and overconf_count >= 1:
            state, conf, reason, grounded = (
                TernaryState.OVERCONFIDENT, retrieval_confidence,
                f"Confident without grounding (RAG: {retrieval_confidence:.0%})", False)
            markers.append("overconfident_no_grounding")
        elif rag_weak:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, retrieval_confidence,
                f"Insufficient grounding (RAG: {retrieval_confidence:.0%})", False)
            markers.append("weak_rag_grounding")
        elif fabrication:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, 0.2,
                "Response contains knowledge limitation markers", False)
        elif contradiction:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, 0.3,
                "Response contains contradictory statements", False)
        elif is_short and not has_rag:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, 0.4,
                "Response unusually short", False)
        elif norm_unc > 0.5:
            state, conf, reason, grounded = (
                TernaryState.UNCERTAIN, 1.0 - norm_unc,
                f"High uncertainty ({unc_count} markers)", rag_strong)
        elif overconf_count > 2 and unc_count == 0 and not rag_strong:
            state, conf, reason, grounded = (
                TernaryState.OVERCONFIDENT, 0.4,
                "Overconfidence without hedging", False)
        elif rag_strong:
            state, conf, reason, grounded = (
                TernaryState.CONFIDENT, min(retrieval_confidence, ling_conf),
                f"Response grounded (RAG: {retrieval_confidence:.0%})", True)
        elif rag_medium:
            state, conf, reason, grounded = (
                TernaryState.CONFIDENT, retrieval_confidence * ling_conf,
                f"Partially grounded (RAG: {retrieval_confidence:.0%})", True)
        else:
            state, conf, reason, grounded = (
                TernaryState.CONFIDENT, ling_conf,
                "Response appears confident (no RAG)", False)

        return EpistemicState(
            state=state, confidence=conf,
            should_abstain=state in (TernaryState.UNCERTAIN, TernaryState.OVERCONFIDENT),
            reason=reason, markers_found=markers[:5],
            retrieval_confidence=retrieval_confidence, chunks_found=chunks_found,
            grounded=grounded
        )
