import re
from typing import Callable, Union
from collections import Counter

from agentlin.core.types import ContentData
from agentlin.reward.grade_boxed_answer import validate_boxed_answer



def _normalize_text(text: str) -> str:
    """Normalize text for comparison by lowercasing and removing punctuation."""
    if not text:
        return ""
    text = text.lower()
    # Keep spaces and alphanumeric, remove others
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = " ".join(text.split())  # Remove extra whitespace
    return text


def _compute_f1_score(prediction: str, ground_truth: str) -> float:
    """Compute F1 score between prediction and ground truth."""
    pred_tokens = _normalize_text(prediction).split()
    gt_tokens = _normalize_text(ground_truth).split()

    if not pred_tokens and not gt_tokens:
        return 1.0
    if not pred_tokens or not gt_tokens:
        return 0.0

    pred_counter = Counter(pred_tokens)
    gt_counter = Counter(gt_tokens)

    # Calculate intersection
    intersection = sum((pred_counter & gt_counter).values())

    # Calculate precision and recall
    precision = intersection / len(pred_tokens) if pred_tokens else 0.0
    recall = intersection / len(gt_tokens) if gt_tokens else 0.0

    # Calculate F1
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return f1


def _compute_exact_match(prediction: str, ground_truth: str) -> float:
    """Compute exact match score between prediction and ground truth."""
    pred_normalized = _normalize_text(prediction)
    gt_normalized = _normalize_text(ground_truth)
    return 1.0 if pred_normalized == gt_normalized else 0.0


def _compute_boxed_answer_score(prediction: str, ground_truth: str) -> float:
    """Compute boxed answer score between prediction and ground truth."""
    validate = validate_boxed_answer(prediction, ground_truth)
    return 1.0 if validate else 0.0


def compute_answer_score(
    prediction: Union[str, list[ContentData]],
    ground_truth: str,
    _compute_answer_score: Callable[[str, str], float]=_compute_boxed_answer_score,
) -> float:
    if isinstance(prediction, str):
        return _compute_answer_score(prediction, ground_truth)
    elif isinstance(prediction, list):
        texts = []
        for item in prediction:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                if "text" in item:
                    texts.append(item["text"])
        if texts:
            combined_text = "\n".join(texts)
            return _compute_answer_score(combined_text, ground_truth)
        else:
            return 0.0
    return 0.0

