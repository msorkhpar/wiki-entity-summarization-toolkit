import logging
from collections import defaultdict
from typing import Union, Tuple, Dict, List

import networkx as nx
import pandas as pd

from wikes_toolkit.base.versions import DatasetName
from wikes_toolkit.esbm.esbm_graph_components import ESBMBaseGraph, ESBMRootEntity, ESBMTriple

logger = logging.getLogger(__name__)


class PandasESBMGraph(ESBMBaseGraph):
    def __init__(self, G: nx.MultiDiGraph, dataset: DatasetName):
        super().__init__(G, dataset)

    @staticmethod
    def _build_pandas_gold_top_k(gold_data: Dict[Tuple[str, int], List[Tuple[str, str, str, str]]]):
        df = (pd.DataFrame(
            [
                {
                    'root_entity': key[0],
                    'annotator_index': key[1],
                    'order': inner_item[0],
                    'subject': inner_item[1],
                    'predicate': inner_item[2],
                    'object': inner_item[3]
                } for key, value in gold_data.items() for inner_item in value
            ], columns=[
                'root_entity', 'annotator_index', 'order', 'subject', 'predicate', 'object'
            ])
              .set_index(['root_entity', 'annotator_index', 'order'])
              .sort_index()
              .reset_index(level='order'))
        return df

    def _initialize(self):
        logger.debug("Initializing PandasESBMGraph...")

        nodes_data = [
            {
                'identifier': node,
                'eid': data.get('eid'),
                'label': data.get('label'),
                'category': data.get('category')
            }
            for node, data in self._G.nodes(data=True) if data.get('is_root', False)
        ]
        self._root_entities = pd.DataFrame(nodes_data, columns=[
            'identifier', 'eid', 'label', 'category'
        ]).set_index('identifier')
        del nodes_data
        self._root_entities.sort_values('eid', inplace=True)
        logger.debug(f"Root Entities: {self._root_entities.shape[0]} initialized.")

        nodes_data = [
            {
                'identifier': node,
            }
            for node, data in self._G.nodes(data=True)
        ]
        self._entities = pd.DataFrame(nodes_data, columns=['identifier']).set_index('identifier')
        logger.debug(f"Entities: {self._entities.shape[0]} initialized.")
        del nodes_data

        logger.debug("Initializing triples...")
        edges_data = []
        predicates_data = set()

        gold5_data: Dict[Tuple[str, int], List[Tuple[str, str, str, str]]] = defaultdict(list)
        gold10_data: Dict[Tuple[str, int], List[Tuple[str, str, str, str]]] = defaultdict(list)

        for u, v, data in self._G.edges(data=True):
            predicate_id = data['predicate']
            edges_data.append({'subject': u, 'predicate': predicate_id, 'object': v})

            if predicate_id not in predicates_data:
                predicates_data.add(predicate_id)

            if 'summary_for' in data:
                for i in range(6):
                    if f"in_gold_top5_{i}" in data:
                        order = data[f"in_gold_top5_{i}"]
                        gold5_data[(data['summary_for'], i)].append((order, u, predicate_id, v))
                    if f"in_gold_top10_{i}" in data:
                        order = data[f"in_gold_top10_{i}"]
                        gold10_data[(data['summary_for'], i)].append((order, u, predicate_id, v))

        self._predicates = pd.DataFrame(
            list(predicates_data),
            columns=['identifier']
        ).set_index('identifier')
        del predicates_data

        self._triples = pd.DataFrame(edges_data, columns=['subject', 'predicate', 'object'])
        del edges_data
        logger.debug(f"Triples: {self._triples.shape[0]} initialized.")

        self._gold_top_5 = PandasESBMGraph._build_pandas_gold_top_k(gold5_data)
        del gold5_data

        self._gold_top_10 = PandasESBMGraph._build_pandas_gold_top_k(gold10_data)
        del gold10_data

    def root_entities(self) -> pd.DataFrame:
        return super().root_entities()

    def entities(self) -> pd.DataFrame:
        return super().entities()

    def triples(self) -> pd.DataFrame:
        return super().triples()

    def predicates(self) -> pd.DataFrame:
        return super().predicates()

    def fetch_entity(self, entity: [str, pd.Series]) -> pd.Series:
        return super().fetch_entity(entity)

    def fetch_root_entity(self, entity: [str, pd.Series]) -> pd.Series:
        return super().fetch_root_entity(entity)

    def fetch_predicate(self, predicate: [str, pd.Series]) -> pd.Series:
        return super().fetch_predicate(predicate)

    def fetch_triple(self, triple: Union[Tuple[str, str, str], pd.Series]) -> pd.Series:
        return super().fetch_triple(triple)

    def neighbors(self, entity: [str, pd.Series]) -> pd.DataFrame:
        return super().neighbors(entity)

    def all_gold_top_k(self, k: int) -> Dict[str, List[List[Tuple[str, str, str]]]]:
        if k not in [5, 10]:
            raise ValueError("k should be 5 or 10")
        result: Dict[str, List[List[Tuple[str, str, str]]]] = dict()
        gold_top_k = self._gold_top_5 if k == 5 else self._gold_top_10
        all_golds = gold_top_k.groupby(['root_entity', 'annotator_index']).apply(
            lambda x: tuple(x[['subject', 'predicate', 'object']].values.tolist())
        ).groupby('root_entity').agg(list).to_dict()
        for index, row in self._root_entities.iterrows():
            result[str(index)] = all_golds[index]
        return result

    def gold_top_5(self, root_entity: Union[ESBMRootEntity, str], annotator_index: int) -> pd.DataFrame:
        if annotator_index < 0 or annotator_index > 5:
            raise ValueError("Annotator index should be between 0 and 5.")
        root_entity = self.fetch_root_entity(root_entity).name
        return self._gold_top_5.loc[(root_entity, annotator_index)]

    def gold_top_10(self, root_entity: Union[ESBMRootEntity, str], annotator_index: int) -> pd.DataFrame:
        if annotator_index < 0 or annotator_index > 5:
            raise ValueError("Annotator index should be between 0 and 5.")
        root_entity = self.fetch_root_entity(root_entity).name
        return self._gold_top_10.loc[(root_entity, annotator_index)]

    def export_as_csv(self, path: str):
        raise NotImplementedError("Exporting to CSV is not yet implemented for PandasESBMGraph.")
