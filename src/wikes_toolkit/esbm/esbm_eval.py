from typing import Dict, List, Tuple
from wikes_toolkit.base.evaluate import f1, map


class ESBMSummaryEvaluator:
    def __init__(self, root_entities: List[str], gold_summaries: Dict[str, List[List[Tuple[str, str, str]]]],
                 predictions: Dict[str, List[Tuple[str, str, str]]], top_k: int):
        self.gold_summaries = gold_summaries
        self.predictions = predictions
        self.root_entities = root_entities
        self.top_k = top_k

    def get_gold_summaries(self, entity_id: str) -> List[List[Tuple[str, str, str]]]:
        result = list()
        summaries = self.gold_summaries.get(entity_id, [])
        for summary in summaries:
            result.append(summary[:self.top_k])
        return result

    def get_predications(self, entity_id: str) -> List[Tuple[str, str, str]]:
        predictions = self.predictions.get(entity_id, [])
        return predictions[:self.top_k]

    def evaluate_f1(self):
        def calculate_average_prf(gold_summaries: List[List[Tuple[str, str, str]]],
                                  algo_summary: List[Tuple[str, str, str]]):
            f1_sum = 0
            user_count = len(gold_summaries)

            for gold_summary in gold_summaries:
                f1_sum += f1(gold_summary, algo_summary)

            return f1_sum / user_count

        entity_count = len(self.root_entities)
        dataset_f1_sum = 0

        for entity_id in self.root_entities:
            gold_summaries = self.get_gold_summaries(entity_id)
            algo_summary = self.get_predications(entity_id)

            if algo_summary:
                dataset_f1_sum += calculate_average_prf(gold_summaries, algo_summary)

        return dataset_f1_sum / entity_count

    def evaluate_map(self):
        def calculate_average_map(gold_summaries: List[List[Tuple[str, str, str]]],
                                  algo_rank: List[Tuple[str, str, str]]):
            map_sum = 0
            user_count = len(gold_summaries)

            for gold_summary in gold_summaries:
                map_score = map(gold_summary, algo_rank)
                map_sum += map_score

            return map_sum / user_count

        entity_count = len(self.root_entities)
        dataset_map_sum = 0

        for entity_id in self.root_entities:
            gold_summaries = self.get_gold_summaries(entity_id)
            algo_summary = self.get_predications(entity_id)

            if algo_summary:
                dataset_map_sum += calculate_average_map(gold_summaries, algo_summary)

        avg_map = dataset_map_sum / entity_count

        return avg_map
