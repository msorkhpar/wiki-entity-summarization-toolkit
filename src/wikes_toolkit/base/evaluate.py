from typing import List, Tuple


def f1(
        gold_summary: List[Tuple[str, str, str]],
        algo_summary: List[Tuple[str, str, str]]
) -> float:
    gold_set = set(gold_summary)
    algo_set = set(algo_summary)

    correct = len(gold_set.intersection(algo_set))
    precision = correct / len(algo_summary)
    recall = correct / len(gold_summary)
    return 2 * precision * recall / (precision + recall) if correct != 0 else 0


def map(gold_summary: List[Tuple[str, str, str]],
        algo_rank: List[Tuple[str, str, str]]) -> float:
    relevant_count = 0
    cumulative_precision = 0
    gold_set = set(gold_summary)

    for i, summary in enumerate(algo_rank):
        if summary in gold_set:
            relevant_count += 1
            precision_at_i = relevant_count / (i + 1)
            cumulative_precision += precision_at_i

    return cumulative_precision / len(gold_summary) if relevant_count != 0 else 0
