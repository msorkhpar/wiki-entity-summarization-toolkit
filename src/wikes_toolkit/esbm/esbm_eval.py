from typing import Dict, List, Tuple

# We have used https://github.com/nju-websoft/ESBM/blob/master/v1.2/Evaluator/esummeval-src_v1.2.jar source code

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
            def calculate_prf(
                    gold_summary: List[Tuple[str, str, str]],
                    algo_summary: List[Tuple[str, str, str]]
            ) -> float:
                gold_set = set(gold_summary)
                algo_set = set(algo_summary)

                true_positives = len(gold_set.intersection(algo_set))
                false_positives = len(algo_set - gold_set)
                false_negatives = len(gold_set - algo_set)

                precision = true_positives / (true_positives + false_positives) if \
                    (true_positives + false_positives) > 0 else 0
                recall = true_positives / (true_positives + false_negatives) if \
                    (true_positives + false_negatives) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

                return f1

            f1_sum = 0
            user_count = len(gold_summaries)

            for gold_summary in gold_summaries:
                f1_sum += calculate_prf(gold_summary, algo_summary)

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
            def calculate_map(gold_summary: List[Tuple[str, str, str]],
                              algo_rank: List[Tuple[str, str, str]]) -> float:
                gold_set = set(gold_summary)
                algo_set = set(algo_rank)

                true_positives = gold_set.intersection(algo_set)
                ap_sum = 0
                num_relevant = 0

                for i, triple in enumerate(algo_rank, start=1):
                    if triple in true_positives:
                        num_relevant += 1
                        ap_sum += num_relevant / i

                return ap_sum / len(gold_set) if len(gold_set) > 0 else 0

            map_sum = 0
            user_count = len(gold_summaries)

            for gold_summary in gold_summaries:
                map_score = calculate_map(gold_summary, algo_rank)
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
