from typing import List, Tuple, Union


def f1(
        gold_summary: List[Union[Tuple[str, str, str], Tuple[str, str]]],
        algo_summary: List[Union[Tuple[str, str, str], Tuple[str, str]]]
) -> float:
    gold_set = set(gold_summary)
    algo_set = set(algo_summary)

    correct = len(gold_set.intersection(algo_set))
    precision = correct / len(algo_summary)
    recall = correct / len(gold_summary)
    return 2 * precision * recall / (precision + recall) if correct != 0 else 0


def map(gold_summary: List[Union[Tuple[str, str, str], Tuple[str, str]]],
        algo_rank: List[Union[Tuple[str, str, str], Tuple[str, str]]]) -> float:
    relevant_count = 0
    cumulative_precision = 0
    gold_set = set(gold_summary)

    for i, summary in enumerate(algo_rank):
        if summary in gold_set:
            relevant_count += 1
            precision_at_i = relevant_count / (i + 1)
            cumulative_precision += precision_at_i

    return cumulative_precision / len(gold_summary) if relevant_count != 0 else 0


def f1_norel(
        gold_summary: List[Tuple[str, str, str]],
        algo_summary: List[Tuple[str, str, str]]
) -> float:
    gold_set = [(s, o) for s, p, o in gold_summary]
    algo_set = [(s, o) for s, p, o in algo_summary]
    return f1(gold_set, algo_set)


def map_norel(gold_summary: List[Tuple[str, str, str]],
              algo_rank: List[Tuple[str, str, str]]) -> float:
    gold_set = [(s, o) for s, p, o in gold_summary]
    algo_rank = [(s, o) for s, p, o in algo_rank]
    return map(gold_set, algo_rank)
