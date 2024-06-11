import logging
from collections import defaultdict
from typing import Union, List, Optional, Dict, Tuple

import networkx as nx

from wikes_toolkit.base.graph_components import Entity, RootEntity, Triple, Predicate
from wikes_toolkit.base.versions import DatasetName
from wikes_toolkit.esbm.esbm_graph_components import ESBMBaseGraph, ESBMEntity, ESBMTriple, ESBMPredicate, \
    ESBMRootEntity

logger = logging.getLogger(__name__)


class ESBMGraph(ESBMBaseGraph):
    def __init__(self, G: nx.MultiDiGraph, dataset: DatasetName,
                 root_entity_formatter: Optional[callable] = None,
                 entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None, triple_formatter: Optional[callable] = None):
        super().__init__(G, dataset, root_entity_formatter, entity_formatter, predicate_formatter, triple_formatter)

    def _extract_gold_summaries(self, data: dict[str, any], triple: ESBMTriple):
        for i in range(6):
            if f"in_gold_top5_{i}" in data:
                order = data[f"in_gold_top5_{i}"]
                self._gold_top_5[data['summary_for']][i].insert(order, triple)
            if f"in_gold_top10_{i}" in data:
                order = data[f"in_gold_top10_{i}"]
                self._gold_top_10[data['summary_for']][i].insert(order, triple)

    def _initialize(self):
        super()._initialize()
        self._entities: Dict[str, Union[ESBMEntity, ESBMRootEntity]] = {}
        self._root_entities: Dict[str, ESBMRootEntity] = {}
        self._predicates: Dict[str, ESBMPredicate] = {}
        self._triples: Dict[Tuple[str, str, str], ESBMTriple] = {}
        self._gold_top_5: Dict[str, List[List[ESBMTriple]]] = defaultdict(lambda: [list() for _ in range(6)])
        self._gold_top_10: Dict[str, List[List[ESBMTriple]]] = defaultdict(lambda: [list() for _ in range(6)])

        logger.debug(f"Initializing ESBMGraph {self._dataset_name}...")

        for node, data in self._G.nodes(data=True):
            if data.get('is_root', False):
                root_entity = ESBMRootEntity(
                    identifier=node,
                    eid=data.get('eid'),
                    category=data.get('category'),
                    str_formatter=self._root_entity_formatter
                )
                self._root_entities[node] = root_entity

            entity = ESBMEntity(
                identifier=node,
                str_formatter=self._entity_formatter
            )
            self._entities[node] = entity
        logger.debug(f"Entities: {len(self._entities)} initialized.")

        # sort root entities based on eid
        self._root_entities = dict(sorted(self._root_entities.items(), key=lambda x: x[1].eid))
        logger.debug(f"Root Entities: {len(self._root_entities)} initialized.")

        logger.debug("Initializing triples...")
        for u, v, data in self._G.edges(data=True):
            predicate_id = data['predicate']
            if predicate_id not in self._predicates:
                self._predicates[predicate_id] = ESBMPredicate(
                    predicate_id=predicate_id,
                    str_formatter=self._predicate_formatter
                )

            triple = ESBMTriple(
                subject_entity=self._entities[u],
                predicate=self._predicates[predicate_id],
                object_entity=self._entities[v],
                str_formatter=self._triple_formatter
            )
            self._triples[(u, predicate_id, v)] = triple

            if 'summary_for' in data:
                self._extract_gold_summaries(data, triple)

    def root_entities(self) -> List[ESBMRootEntity]:
        return super().root_entities()

    def entities(self) -> List[ESBMEntity]:
        return super().entities()

    def triples(self) -> List[ESBMTriple]:
        return super().triples()

    def predicates(self) -> List[ESBMPredicate]:
        return super().predicates()

    def fetch_entity(self, entity: Union[Entity, str]) -> ESBMEntity:
        return super().fetch_entity(entity)

    def fetch_root_entity(self, entity: Union[RootEntity, str]) -> ESBMRootEntity:
        return super().fetch_root_entity(entity)

    def fetch_predicate(self, predicate: Union[Predicate, str]) -> ESBMPredicate:
        return super().fetch_predicate(predicate)

    def fetch_triple(self, triple: Union[
        Triple, Tuple[
            Union[Entity, str],
            Union[Predicate, str],
            Union[Entity, str]
        ],

    ]) -> ESBMTriple:
        return super().fetch_triple(triple)

    def neighbors(self, entity: Union[Entity, str]) -> List[Entity]:
        return super().neighbors(entity)

    def all_gold_top_k(self, k: int) -> Dict[str, List[List[Tuple[str, str, str]]]]:
        if k not in [5, 10]:
            raise ValueError("k should be 5 or 10")
        gold_top_k = self._gold_top_5 if k == 5 else self._gold_top_10
        result = defaultdict(lambda: [list() for _ in range(6)])
        for root_entity_id, top_list in gold_top_k.items():
            for i, items in enumerate(top_list):
                result[root_entity_id][i] = [
                    (t.subject_entity.identifier, t.predicate.predicate_id, t.object_entity.identifier) for t in items]
        return result

    def gold_top_5(self, root_entity: Union[ESBMRootEntity, str], annotator_index: int) -> List[ESBMTriple]:
        if annotator_index < 0 or annotator_index > 5:
            raise ValueError("Annotator index should be between 0 and 5.")
        return self._gold_top_5[self.fetch_root_entity_id(root_entity)][annotator_index]

    def gold_top_10(self, root_entity: Union[ESBMRootEntity, str], annotator_index: int) -> List[ESBMTriple]:
        if annotator_index < 0 or annotator_index > 5:
            raise ValueError("Annotator index should be between 0 and 5.")
        return self._gold_top_10[self.fetch_root_entity_id(root_entity)][annotator_index]
