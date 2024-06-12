from typing import Dict, List, Tuple

# We are going to use https://github.com/nju-websoft/ESBM/blob/master/v1.2/Evaluator/esummeval-src_v1.2.jar source code

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

    # TODO Implement this method
    def evaluate_f1(self):
        raise NotImplementedError("Method not implemented")

    # TODO Implement this method
    def evaluate_map(self):
        raise NotImplementedError("Method not implemented")
