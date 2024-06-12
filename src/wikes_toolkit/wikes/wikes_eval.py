from typing import Dict, List, Tuple


class WikESSummaryEvaluator:
    def __init__(self, root_entities: List[str], ground_truth: Dict[str, List[Tuple[str, str, str]]],
                 predictions: Dict[str, List[Tuple[str, str, str]]], top_k: int):
        self.root_entities = root_entities
        self.ground_truth = ground_truth
        self.predictions = predictions
        self.top_k = top_k

    def get_summaries(self, entity_id: str) -> List[Tuple[str, str, str]]:
        return self.ground_truth.get(entity_id, [])

    def get_predications(self, entity_id: str) -> List[Tuple[str, str, str]]:
        predictions = self.predictions.get(entity_id, [])
        return predictions[:self.top_k]

    # TODO Implement this method
    def evaluate_f1(self):
        raise NotImplementedError("Method not implemented")

    # TODO Implement this method
    def evaluate_map(self):
        raise NotImplementedError("Method not implemented")
