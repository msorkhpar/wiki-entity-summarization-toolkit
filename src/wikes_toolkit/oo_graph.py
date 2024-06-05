import logging
from collections import defaultdict
from typing import Union, Tuple, Set, List, Optional, Dict

import networkx as nx

from wikes_toolkit.wikies_graph_components import BaseWikESGraph, Entity, RootEntity, Predicate, Triple

logger = logging.getLogger(__name__)


class WikESGraph(BaseWikESGraph):
    def __init__(self, G: nx.MultiDiGraph, entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None, triple_formatter: Optional[callable] = None
                 ):
        super().__init__(G, entity_formatter, predicate_formatter, triple_formatter)

    def _initialize(self):
        self._entities: Dict[str, Union[Entity, RootEntity]] = {}
        self._root_entities: Dict[str, RootEntity] = {}
        self._predicates: Dict[str, Predicate] = {}
        self._triples: Dict[Tuple[str, str, str], Triple] = {}
        self._ground_truths: Dict[str, Set[Triple]] = defaultdict(set)
        logger.debug("Initializing WikESGraph...")
        for node, data in self._G.nodes(data=True):
            if data.get('is_root', False):
                root_entity = RootEntity(
                    wikidata_id=node,
                    wikidata_label=data.get('wikidata_label'),
                    wikidata_description=data.get('wikidata_desc'),
                    wikipedia_id=data.get('wikipedia_id'),
                    wikipedia_title=data.get('wikipedia_title'),
                    category=data.get('category'),
                    str_formatter=self._entity_formatter
                )
                self._root_entities[node] = root_entity
                self._entities[node] = root_entity
            else:
                entity = Entity(
                    wikidata_id=node,
                    wikidata_label=data.get('wikidata_label'),
                    wikidata_description=data.get('wikidata_desc'),
                    wikipedia_id=data.get('wikipedia_id'),
                    wikipedia_title=data.get('wikipedia_title'),
                    str_formatter=self._entity_formatter
                )
                self._entities[node] = entity
        logger.debug(f"Entities: {len(self._entities)} initialized.")

        logger.debug("Initializing triples...")
        for u, v, data in self._G.edges(data=True):
            predicate_id = data['predicate']
            if predicate_id not in self._predicates:
                self._predicates[predicate_id] = Predicate(
                    predicate_id=predicate_id,
                    label=data.get('predicate_label'),
                    description=data.get('predicate_desc'),
                    str_formatter=self._predicate_formatter
                )

            triple = Triple(
                subject_entity=self._entities[u],
                predicate=self._predicates[predicate_id],
                object_entity=self._entities[v],
                str_formatter=self._triple_formatter
            )
            self._triples[(u, predicate_id, v)] = triple
            if 'summary_for' in data:
                self._ground_truths[data['summary_for']].add(triple)
        logger.debug(f"Triples: {len(self._triples)} initialized.")

    def __get_predicate(self, predicate: Union[Predicate, str]) -> Predicate:
        if isinstance(predicate, Predicate):
            return predicate
        if predicate not in self._predicates:
            raise ValueError(f"Predicate with predicate_id: {predicate} not found")
        return self._predicates[predicate]

    def root_entities(self) -> list[RootEntity]:
        return list(self._root_entities.values())

    def root_entity_ids(self) -> Set[str]:
        return set(self._root_entities.keys())

    def entities(self) -> List[Entity]:
        return list(self._entities.values())

    def triples(self) -> List[Triple]:
        return list(self._triples.values())

    def predicates(self) -> List[Predicate]:
        return list(self._predicates.values())

    def total_entities(self) -> int:
        return len(self._entities)

    def total_triples(self) -> int:
        return len(self._triples)

    def fetch_entity(self, entity: Union[Entity, RootEntity, str]) -> Entity:
        if isinstance(entity, RootEntity) or isinstance(entity, Entity):
            wikidata_id = entity.wikidata_id
        else:
            wikidata_id = entity

        if wikidata_id not in self._entities:
            raise ValueError(f"Entity with wikidata_id: {wikidata_id} not found.")
        return self._entities[wikidata_id]

    def fetch_root_entity(self, entity: Union[RootEntity, str]) -> Entity:
        if type(entity) is Entity:
            raise ValueError(f"Entity {entity} is not a root entity.")
        if isinstance(entity, RootEntity):
            wikidata_id = entity.wikidata_id
        else:
            wikidata_id = entity
        if wikidata_id not in self._root_entities:
            raise ValueError(f"Entity with wikidata_id: {wikidata_id} not found in root entities.")
        return self._root_entities[wikidata_id]

    def fetch_root_entity_id(self, entity: Union[RootEntity, str]) -> str:
        return self.fetch_root_entity(entity).wikidata_id

    def fetch_triple(self, triple: Union[Triple, Tuple[
        Union[Entity, RootEntity, str],
        Union[Entity, RootEntity, str],
        Union[Entity, RootEntity, str]
    ]]) -> Triple:
        if isinstance(triple, Tuple):
            subject_entity = self.fetch_entity(triple[0])
            predicate = self.__get_predicate(triple[1])
            object_entity = self.fetch_entity(triple[2])
            triple_key = (subject_entity.wikidata_id, predicate.predicate_id, object_entity.wikidata_id)
        else:
            triple_key = (
                triple.subject_entity.wikidata_id,
                triple.predicate.predicate_id,
                triple.object_entity.wikidata_id
            )
        if triple_key not in self._triples:
            raise ValueError(f"Triple {triple_key} not found.")
        return self._triples[triple_key]

    def fetch_triple_ids(self, triple: Union[
        Triple, Tuple[
            Union[Entity, RootEntity, str],
            Union[Entity, RootEntity, str],
            Union[Entity, RootEntity, str]
        ]
    ]) -> Tuple[str, str, str]:
        triple = self.fetch_triple(triple)
        return triple.subject_entity.wikidata_id, triple.predicate.predicate_id, triple.object_entity.wikidata_id

    def fetch_predicate(self, predicate: Union[Predicate, str]) -> Predicate:
        if isinstance(predicate, Predicate):
            predicate_id = predicate.predicate_id
        else:
            predicate_id = predicate

        if predicate_id not in self._predicates:
            raise ValueError(f"Predicate with predicate_id: {predicate_id} not found")
        return self._predicates[predicate_id]

    def neighbors(self, entity: Union[Entity, RootEntity, str]) -> List[Triple]:
        entity = self.fetch_entity(entity)
        entity_id = entity.wikidata_id

        neighbors = [
            self._triples[(u, data['predicate'], v)]
            for u, v, data in self._G.edges(entity_id, data=True)
        ]
        neighbors.extend([
            self._triples[(u, data['predicate'], v)]
            for u, v, data in self._G.in_edges(entity_id, data=True)
        ])
        return neighbors

    def degree(self, entity: Union[Entity, RootEntity, str]) -> int:
        entity = self.fetch_entity(entity)
        return self._G.degree(entity.wikidata_id)

    def ground_truths(self, root_entity: Union[RootEntity, str]) -> Set[Triple]:
        root_entity_id = self.fetch_root_entity(root_entity).wikidata_id
        if root_entity_id not in self._ground_truths:
            raise ValueError(f"No ground truth summaries found for root_entity: {root_entity_id}.")
        return self._ground_truths[root_entity_id]

    def ground_truth_triple_ids(self, root_entity: Union[RootEntity, str]) -> Set[Tuple[str, str, str]]:
        return {(s.wikidata_id, p.predicate_id, o.wikidata_id) for s, p, o in self.ground_truths(root_entity)}

    def mark_triple_as_summary(
            self,
            root_entity: Union[RootEntity, str],
            triple: Union[
                Triple, Tuple[
                    Union[Entity, RootEntity, str],
                    Union[Entity, RootEntity, str],
                    Union[Entity, RootEntity, str]
                ]
            ]
    ):
        root_entity_id = self.fetch_entity(root_entity).wikidata_id
        triple = self.fetch_triple(triple)
        if root_entity_id not in {triple.subject_entity.wikidata_id, triple.object_entity.wikidata_id}:
            raise ValueError(
                f"Root entity: {root_entity_id} should be either a subject or an object of the triple in a summary.")

        self._predicted_summaries[root_entity_id].add((
            triple.subject_entity.wikidata_id,
            triple.predicate.predicate_id,
            triple.object_entity.wikidata_id
        ))

    def mark_triples_as_summaries(
            self, root_entity: Union[RootEntity, str],
            triples: List[Union[Triple, Tuple[str, str, str]]]
    ):
        for triple in triples:
            self.mark_triple_as_summary(root_entity, triple)
