"""
Evaluation metrics for the Legal Assistance Agent.

Measures:
1. Retrieval Performance (Precision, Recall, F1)
2. Reasoning Validity (Evidence Grounding Score)
3. Explanation Quality (Readability metrics)
"""

from typing import List, Dict
from collections import defaultdict


def calculate_retrieval_precision(retrieved_docs: List[str], relevant_docs: List[str]) -> float:
    """
    Calculate precision: proportion of retrieved documents that are relevant.

    Precision = |Retrieved ∩ Relevant| / |Retrieved|

    Args:
        retrieved_docs: List of retrieved document identifiers
        relevant_docs: List of ground truth relevant documents

    Returns:
        Precision score (0.0 to 1.0)
    """
    if not retrieved_docs:
        return 0.0

    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)

    true_positives = len(retrieved_set.intersection(relevant_set))
    precision = true_positives / len(retrieved_set)

    return precision


def calculate_retrieval_recall(retrieved_docs: List[str], relevant_docs: List[str]) -> float:
    """
    Calculate recall: proportion of relevant documents that were retrieved.

    Recall = |Retrieved ∩ Relevant| / |Relevant|

    Args:
        retrieved_docs: List of retrieved document identifiers
        relevant_docs: List of ground truth relevant documents

    Returns:
        Recall score (0.0 to 1.0)
    """
    if not relevant_docs:
        return 0.0

    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)

    true_positives = len(retrieved_set.intersection(relevant_set))
    recall = true_positives / len(relevant_set)

    return recall


def calculate_f1_score(precision: float, recall: float) -> float:
    """
    Calculate F1 score: harmonic mean of precision and recall.

    F1 = 2 * (Precision * Recall) / (Precision + Recall)

    Args:
        precision: Precision score
        recall: Recall score

    Returns:
        F1 score (0.0 to 1.0)
    """
    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)


def calculate_mrr(retrieved_docs: List[str], relevant_docs: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank.

    MRR = 1 / rank of first relevant document

    Args:
        retrieved_docs: Ordered list of retrieved documents
        relevant_docs: List of relevant documents

    Returns:
        MRR score (0.0 to 1.0)
    """
    relevant_set = set(relevant_docs)

    for i, doc in enumerate(retrieved_docs, 1):
        if doc in relevant_set:
            return 1.0 / i

    return 0.0


def evaluate_evidence_grounding(reasoning_chain: List[str], retrieved_docs: List[str]) -> Dict[str, float]:
    """
    Evaluate how well the reasoning is grounded in retrieved evidence.

    Checks:
    1. Citation rate: How many reasoning steps cite evidence
    2. Evidence coverage: How much of retrieved evidence is used
    3. Unsupported claims: Statements without evidence

    Args:
        reasoning_chain: List of reasoning steps
        retrieved_docs: List of retrieved document texts

    Returns:
        Dictionary with grounding metrics
    """
    citation_markers = ["Document", "[", "evidence", "according to", "states that", "mentions"]

    # Count citations in reasoning
    cited_steps = 0
    for step in reasoning_chain:
        if any(marker.lower() in step.lower() for marker in citation_markers):
            cited_steps += 1

    citation_rate = cited_steps / len(reasoning_chain) if reasoning_chain else 0.0

    # Check for unsupported claim indicators
    uncertainty_markers = ["insufficient", "not found", "no evidence", "unclear", "uncertain"]
    unsupported_count = 0
    for step in reasoning_chain:
        if any(marker in step.lower() for marker in uncertainty_markers):
            unsupported_count += 1

    unsupported_rate = unsupported_count / len(reasoning_chain) if reasoning_chain else 0.0

    return {
        "citation_rate": citation_rate,
        "unsupported_claim_rate": unsupported_rate,
        "grounding_score": citation_rate * (1 - unsupported_rate)
    }


def calculate_readability_score(text: str) -> Dict[str, float]:
    """
    Calculate readability metrics for explanation text.

    Metrics:
    - Average sentence length
    - Average word length
    - Simple readability index

    Args:
        text: Explanation text

    Returns:
        Dictionary with readability metrics
    """
    # Split into sentences
    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    if not sentences:
        return {"avg_sentence_length": 0, "avg_word_length": 0, "readability_score": 0}

    # Calculate metrics
    total_words = 0
    total_chars = 0
    total_sentences = len(sentences)

    for sentence in sentences:
        words = sentence.split()
        total_words += len(words)
        total_chars += sum(len(word) for word in words)

    avg_sentence_length = total_words / total_sentences
    avg_word_length = total_chars / total_words if total_words > 0 else 0

    # Simple readability: penalize long sentences and complex words
    # Lower is better (easier to read)
    readability_index = (avg_sentence_length * 0.5) + (avg_word_length * 3)

    # Convert to 0-1 score where higher is better
    # Ideal: sentence length ~15 words, word length ~5 chars
    readability_score = max(0, 1 - (readability_index - 22.5) / 50)

    return {
        "avg_sentence_length": avg_sentence_length,
        "avg_word_length": avg_word_length,
        "readability_score": min(1.0, max(0.0, readability_score))
    }


def evaluate_agent_response(
    query: str,
    retrieved_docs: List[str],
    reasoning_chain: List[str],
    final_explanation: str,
    ground_truth_relevant: List[str] = None
) -> Dict[str, any]:
    """
    Comprehensive evaluation of agent response.

    Args:
        query: User's original query
        retrieved_docs: Documents retrieved by agent
        reasoning_chain: Reasoning steps from Reasoner Agent
        final_explanation: Final explanation from Explainer Agent
        ground_truth_relevant: Optional ground truth for retrieval evaluation

    Returns:
        Dictionary with all evaluation metrics
    """
    results = {
        "query": query,
        "num_retrieved": len(retrieved_docs),
        "num_reasoning_steps": len(reasoning_chain),
        "explanation_length": len(final_explanation),
        "retrieved_docs": retrieved_docs,
        "reasoning_chain": reasoning_chain,
        "final_explanation": final_explanation
    }

    # Retrieval metrics (if ground truth available)
    if ground_truth_relevant:
        precision = calculate_retrieval_precision(retrieved_docs, ground_truth_relevant)
        recall = calculate_retrieval_recall(retrieved_docs, ground_truth_relevant)
        f1 = calculate_f1_score(precision, recall)
        mrr = calculate_mrr(retrieved_docs, ground_truth_relevant)

        results["retrieval"] = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "mrr": mrr
        }

    # Evidence grounding with detailed citation info
    grounding = evaluate_evidence_grounding(reasoning_chain, retrieved_docs)
    citation_details = _analyze_citations_detailed(reasoning_chain)
    grounding["citation_details"] = citation_details
    results["grounding"] = grounding

    # Readability
    readability = calculate_readability_score(final_explanation)
    results["readability"] = readability

    # Overall score (weighted combination)
    overall_score = (
        grounding["grounding_score"] * 0.4 +
        readability["readability_score"] * 0.3
    )

    if "retrieval" in results:
        overall_score += results["retrieval"]["f1_score"] * 0.3
    else:
        overall_score = overall_score / 0.7  # Normalize if no retrieval ground truth

    results["overall_score"] = min(1.0, overall_score)

    # # Add performance grade and suggestions
    # results["grade"] = _calculate_grade(results["overall_score"])
    # results["suggestions"] = _generate_improvement_suggestions(results)

    return results


def _analyze_citations_detailed(reasoning_chain: List[str]) -> List[Dict]:
    """
    Analyze citations in each reasoning step in detail.

    Args:
        reasoning_chain: List of reasoning steps

    Returns:
        List of dictionaries with citation details for each step
    """
    citation_markers = {
        "Document": "document_reference",
        "[": "bracket_citation",
        "evidence": "evidence_mention",
        "according to": "attribution",
        "states that": "direct_quote",
        "mentions": "mention"
    }

    details = []
    for i, step in enumerate(reasoning_chain):
        step_info = {
            "step_index": i,
            "text": step,
            "length": len(step),
            "found_markers": [],
            "has_citation": False
        }

        for marker, marker_type in citation_markers.items():
            if marker.lower() in step.lower():
                step_info["found_markers"].append({
                    "marker": marker,
                    "type": marker_type
                })
                step_info["has_citation"] = True

        details.append(step_info)

    return details


def _calculate_grade(score: float) -> Dict[str, str]:
    """
    Calculate performance grade based on overall score.

    Args:
        score: Overall score (0.0 to 1.0)

    Returns:
        Dictionary with grade and description
    """
    if score >= 0.9:
        return {"letter": "A", "description": "Excellent", "color": "green"}
    elif score >= 0.8:
        return {"letter": "B", "description": "Very Good", "color": "blue"}
    elif score >= 0.7:
        return {"letter": "C", "description": "Good", "color": "yellow"}
    elif score >= 0.6:
        return {"letter": "D", "description": "Fair", "color": "orange"}
    else:
        return {"letter": "F", "description": "Poor", "color": "red"}


def _generate_improvement_suggestions(results: Dict) -> List[str]:
    """
    Generate specific improvement suggestions based on evaluation results.

    Args:
        results: Evaluation results dictionary

    Returns:
        List of improvement suggestions
    """
    suggestions = []

    # Grounding suggestions
    grounding = results.get("grounding", {})
    if grounding.get("citation_rate", 0) < 0.5:
        suggestions.append("Low citation rate: Add more explicit references to source documents in reasoning steps")
    if grounding.get("unsupported_claim_rate", 0) > 0.3:
        suggestions.append("High unsupported claim rate: Ensure all claims are backed by evidence from the retrieved documents")
    if grounding.get("grounding_score", 0) < 0.6:
        suggestions.append("Improve evidence grounding: Use phrases like 'According to Document X...'")

    # Readability suggestions
    readability = results.get("readability", {})
    if readability.get("avg_sentence_length", 0) > 25:
        suggestions.append("Sentences too long: Break down complex sentences into shorter, clearer ones (around 15-20 words)")
    if readability.get("avg_sentence_length", 0) < 8:
        suggestions.append("Sentences too short: Provide more detailed explanations with complete sentences")
    if readability.get("avg_word_length", 0) > 6:
        suggestions.append("Words too complex: Use simpler vocabulary when possible for better readability")
    if readability.get("readability_score", 0) < 0.6:
        suggestions.append("Overall readability low: Simplify language and structure for better comprehension")

    # Retrieval suggestions
    if "retrieval" in results:
        retrieval = results["retrieval"]
        if retrieval.get("precision", 0) < 0.5:
            suggestions.append("Low precision: Retrieved documents contain many irrelevant results. Refine search queries")
        if retrieval.get("recall", 0) < 0.5:
            suggestions.append("Low recall: Missing relevant documents. Consider expanding search or using different keywords")
        if retrieval.get("mrr", 0) < 0.5:
            suggestions.append("Low MRR: Relevant documents not ranked highly. Improve ranking algorithm")

    # General suggestions
    if results.get("num_reasoning_steps", 0) < 3:
        suggestions.append("Few reasoning steps: Add more intermediate reasoning steps to show thought process")
    if results.get("explanation_length", 0) < 100:
        suggestions.append("Explanation too brief: Provide more comprehensive explanation with details")
    if results.get("explanation_length", 0) > 2000:
        suggestions.append("Explanation too long: Consider being more concise while maintaining key information")

    if not suggestions:
        suggestions.append("Performance is good! Continue maintaining high quality responses")

    return suggestions


def print_evaluation_report(eval_results: Dict, verbose: bool = True) -> str:
    """
    Format evaluation results as a readable report.

    Args:
        eval_results: Results from evaluate_agent_response
        verbose: If True, include detailed information (reasoning chain, documents, etc.)

    Returns:
        Formatted string report
    """
    lines = []
    lines.append("=" * 60)
    lines.append("EVALUATION REPORT")
    lines.append("=" * 60)

    # # Grade display
    # if "grade" in eval_results:
    #     grade = eval_results["grade"]
    #     lines.append(f"\n*** GRADE: {grade['letter']} ({grade['description']}) ***")

    lines.append(f"\nQuery: {eval_results['query']}")
    lines.append(f"Documents Retrieved: {eval_results['num_retrieved']}")
    lines.append(f"Reasoning Steps: {eval_results['num_reasoning_steps']}")
    lines.append(f"Explanation Length: {eval_results['explanation_length']} characters")

    # Retrieved Documents List
    if verbose and "retrieved_docs" in eval_results:
        lines.append("\n--- Retrieved Documents ---")
        for i, doc in enumerate(eval_results["retrieved_docs"], 1):
            doc_preview = doc[:200] + "..." if len(doc) > 200 else doc
            doc_preview = doc_preview.replace("\n", " ")
            lines.append(f"  [{i}] {doc_preview}")

    # Reasoning Chain Content
    if verbose and "reasoning_chain" in eval_results:
        lines.append("\n--- Reasoning Chain ---")
        for i, step in enumerate(eval_results["reasoning_chain"], 1):
            lines.append(f"  Step {i}: {step}")

    if "retrieval" in eval_results:
        lines.append("\n--- Retrieval Performance ---")
        ret = eval_results["retrieval"]
        lines.append(f"  Precision: {ret['precision']:.3f}")
        lines.append(f"  Recall: {ret['recall']:.3f}")
        lines.append(f"  F1 Score: {ret['f1_score']:.3f}")
        lines.append(f"  MRR: {ret['mrr']:.3f}")

    lines.append("\n--- Evidence Grounding ---")
    grnd = eval_results["grounding"]
    lines.append(f"  Citation Rate: {grnd['citation_rate']:.3f}")
    lines.append(f"  Unsupported Claims: {grnd['unsupported_claim_rate']:.3f}")
    lines.append(f"  Grounding Score: {grnd['grounding_score']:.3f}")

    # # Citation Details
    # if verbose and "citation_details" in grnd:
    #     lines.append("\n  Citation Analysis by Step:")
    #     for detail in grnd["citation_details"]:
    #         status = "V" if detail["has_citation"] else "X"
    #         markers = ", ".join([m["marker"] for m in detail["found_markers"]]) if detail["found_markers"] else "None"
    #         lines.append(f"    Step {detail['step_index'] + 1}: {status} Markers found: [{markers}]")

    lines.append("\n--- Explanation Readability ---")
    read = eval_results["readability"]
    lines.append(f"  Avg Sentence Length: {read['avg_sentence_length']:.1f} words")
    lines.append(f"  Avg Word Length: {read['avg_word_length']:.1f} chars")
    lines.append(f"  Readability Score: {read['readability_score']:.3f}")

    # # Improvement Suggestions
    # if "suggestions" in eval_results:
    #     lines.append("\n--- Improvement Suggestions ---")
    #     for i, suggestion in enumerate(eval_results["suggestions"], 1):
    #         lines.append(f"  {i}. {suggestion}")

    lines.append(f"\n{'=' * 60}")
    lines.append(f"OVERALL SCORE: {eval_results['overall_score']:.3f}")
    lines.append("=" * 60)

    return "\n".join(lines)


class EvaluationRunner:
    """
    Runs evaluation on multiple queries and aggregates results.
    """

    def __init__(self):
        self.results = []

    def add_result(self, eval_result: Dict):
        """Add a single evaluation result."""
        self.results.append(eval_result)

    def get_aggregate_metrics(self) -> Dict[str, float]:
        """Calculate aggregate metrics across all evaluations."""
        if not self.results:
            return {}

        aggregate = defaultdict(list)

        for result in self.results:
            aggregate["overall_score"].append(result["overall_score"])
            aggregate["grounding_score"].append(result["grounding"]["grounding_score"])
            aggregate["readability_score"].append(result["readability"]["readability_score"])

            if "retrieval" in result:
                aggregate["precision"].append(result["retrieval"]["precision"])
                aggregate["recall"].append(result["retrieval"]["recall"])
                aggregate["f1_score"].append(result["retrieval"]["f1_score"])

        # Calculate means
        means = {}
        for key, values in aggregate.items():
            means[f"mean_{key}"] = sum(values) / len(values)
            means[f"min_{key}"] = min(values)
            means[f"max_{key}"] = max(values)

        means["num_evaluations"] = len(self.results)

        return means

    def print_summary(self) -> str:
        """Print summary of all evaluations."""
        metrics = self.get_aggregate_metrics()

        lines = []
        lines.append("=" * 60)
        lines.append("AGGREGATE EVALUATION SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Total Evaluations: {metrics.get('num_evaluations', 0)}")

        lines.append("\n--- Overall Performance ---")
        lines.append(f"  Mean Overall Score: {metrics.get('mean_overall_score', 0):.3f}")
        lines.append(f"  Range: [{metrics.get('min_overall_score', 0):.3f}, {metrics.get('max_overall_score', 0):.3f}]")

        lines.append("\n--- Grounding ---")
        lines.append(f"  Mean Grounding Score: {metrics.get('mean_grounding_score', 0):.3f}")

        lines.append("\n--- Readability ---")
        lines.append(f"  Mean Readability Score: {metrics.get('mean_readability_score', 0):.3f}")

        if "mean_f1_score" in metrics:
            lines.append("\n--- Retrieval ---")
            lines.append(f"  Mean Precision: {metrics.get('mean_precision', 0):.3f}")
            lines.append(f"  Mean Recall: {metrics.get('mean_recall', 0):.3f}")
            lines.append(f"  Mean F1: {metrics.get('mean_f1_score', 0):.3f}")

        lines.append("=" * 60)

        return "\n".join(lines)
