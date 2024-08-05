from typing import Dict, List, Tuple
from wikes_toolkit.base.evaluate import f1, map, f1_norel, map_norel


class WikESSummaryEvaluator:
    def __init__(self, root_entities: List[str], ground_truth: Dict[str, List[Tuple[str, str, str]]],
                 predictions: Dict[str, List[Tuple[str, str, str]]]):
        self.root_entities = root_entities
        self.ground_truth = ground_truth
        self.predictions = predictions

    def get_summaries(self, entity_id: str) -> List[Tuple[str, str, str]]:
        return self.ground_truth.get(entity_id, [])

    def get_predications(self, entity_id: str, top_k: int = None) -> List[Tuple[str, str, str]]:
        predictions = self.predictions.get(entity_id, [])
        ground_truth = self.ground_truth.get(entity_id, [])
        if top_k and top_k < len(ground_truth):
            predictions = predictions[:top_k]
        else:
            predictions = predictions[:len(ground_truth)]
        return predictions

    def evaluate_f1(self, top_k: int = None, no_rel: bool = False):
        score_function = f1_norel if no_rel else f1
        entity_count = len(self.root_entities)
        dataset_f1_sum = 0

        for entity_id in self.root_entities:
            gold_summaries = self.get_summaries(entity_id)
            algo_summary = self.get_predications(entity_id, top_k)

            if algo_summary:
                dataset_f1_sum += score_function(gold_summaries, algo_summary)

        return dataset_f1_sum / entity_count

    def evaluate_map(self, top_k: int = None, no_rel: bool = False):
        score_function = map_norel if no_rel else map
        entity_count = len(self.root_entities)
        dataset_map_sum = 0

        for entity_id in self.root_entities:
            gold_summaries = self.get_summaries(entity_id)
            algo_summary = self.get_predications(entity_id, top_k)

            if algo_summary:
                dataset_map_sum += score_function(gold_summaries, algo_summary)

        avg_map = dataset_map_sum / entity_count

        return avg_map
