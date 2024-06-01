from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Union, Dict, Tuple, Set, List

import networkx as nx


@dataclass
class Entity:
    wikidata_id: str
    wikidata_label: Optional[str] = None
    wikidata_description: Optional[str] = None
    wikipdia_id: Optional[int] = None
    wikipdia_title: Optional[str] = None

@dataclass
class RootEntity(Entity):
    category: Optional[str] = None


@dataclass
class Predicate:
    predicate_id: str
    predicate_label: Optional[str] = None
    predicate_description: Optional[str] = None


@dataclass
class Triple:
    subject_entity: Union[Entity, RootEntity]
    predicate: Predicate
    object_entity: Union[Entity, RootEntity]

    def __hash__(self):
        return hash((self.subject_entity.wikidata_id, self.predicate.predicate_id, self.object_entity.wikidata_id))


class WikESGraph:
    def __init__(self, G: nx.MultiDiGraph):
        self.__entities: Dict[str, Entity] = {}
        self.__root_entities: Dict[str, RootEntity] = {}
        self.__predicates: Dict[str, Predicate] = {}
        self.__triples: Dict[Tuple[str, str, str], Triple] = {}
        self.__ground_truths: Dict[str, Set[Triple]] = defaultdict(set)
        self.__predicted_summaries: Dict[str, Set[Triple]] = defaultdict(set)
        self.__G: nx.MultiDiGraph = G
        self.__initialize()

    def __initialize(self):
        for node, data in self.__G.nodes(data=True):
            if data.get('is_root', False):
                root_entity = RootEntity(
                    wikidata_id=node,
                    wikidata_label=data.get('wikidata_label'),
                    wikidata_description=data.get('wikidata_desc'),
                    wikipdia_id=data.get('wikipedia_id'),
                    wikipdia_title=data.get('wikipedia_title'),
                    category=data.get('category')
                )
                self.__root_entities[node] = root_entity
                self.__entities[node] = root_entity
            else:
                entity = Entity(
                    wikidata_id=node,
                    wikidata_label=data.get('wikidata_label'),
                    wikidata_description=data.get('wikidata_desc'),
                    wikipdia_id=data.get('wikipedia_id'),
                    wikipdia_title=data.get('wikipedia_title'),
                )
                self.__entities[node] = entity

        for u, v, data in self.__G.edges(data=True):
            predicate_id = data['predicate']
            if predicate_id not in self.__predicates:
                self.__predicates[predicate_id] = Predicate(
                    predicate_id=predicate_id,
                    predicate_label=data.get('predicate_label'),
                    predicate_description=data.get('predicate_desc')
                )

            triple = Triple(
                subject_entity=self.__entities[u],
                predicate=self.__predicates[predicate_id],
                object_entity=self.__entities[v]
            )
            self.__triples[(u, predicate_id, v)] = triple
            if 'summary_for' in data:
                self.__ground_truths[data['summary_for']].add(triple)

    def __get_entity(self, entity: Union[Entity, RootEntity, str]) -> Entity:
        if isinstance(entity, (Entity, RootEntity)):
            return self.fetch_entity(entity.wikidata_id)
        return self.fetch_entity(entity)

    def __get_root_entity(self, entity: Union[RootEntity, str]) -> Entity:
        if type(entity) is Entity:
            raise ValueError(f"Entity {entity} is not a root entity.")
        if isinstance(entity, RootEntity):
            return self.fetch_entity(entity.wikidata_id)
        return self.fetch_entity(entity)

    def __get_predicate(self, predicate: Union[Predicate, str]) -> Predicate:
        if isinstance(predicate, Predicate):
            return predicate
        if predicate not in self.__predicates:
            raise ValueError(f"Predicate with predicate_id: {predicate} not found")
        return self.__predicates[predicate]

    def __get_triple(self, triple: Union[Triple, Tuple[str, str, str]]) -> Triple:
        if isinstance(triple, Triple):
            return self.fetch_triple(triple.subject_entity, triple.predicate, triple.object_entity)
        return self.fetch_triple(triple[0], triple[1], triple[2])

    def root_entities(self) -> list[RootEntity]:
        return list(self.__root_entities.values())

    def entities(self) -> List[Entity]:
        return list(self.__entities.values())

    def triples(self) -> List[Triple]:
        return list(self.__triples.values())

    def predicates(self) -> List[Predicate]:
        return list(self.__predicates.values())

    def count_entities(self) -> int:
        return len(self.__entities)

    def count_triples(self) -> int:
        return len(self.__triples)

    def fetch_entity(self, wikidata_id: str) -> Entity:
        if not isinstance(wikidata_id, str):
            raise ValueError(f"wikidata_id: {wikidata_id} is not string.")

        if wikidata_id not in self.__entities:
            raise ValueError(f"Entity with wikidata_id: {wikidata_id} not found")
        return self.__entities[wikidata_id]

    def fetch_root_entity(self, wikidata_id: str) -> Entity:
        if not isinstance(wikidata_id, str):
            raise ValueError(f"wikidata_id: {wikidata_id} is not string.")

        if wikidata_id not in self.__root_entities:
            raise ValueError(f"RootEntity with wikidata_id: {wikidata_id} not found")
        return self.__root_entities[wikidata_id]

    def fetch_triple(self, subject_entity: Union[Entity, RootEntity, str], predicate: Union[Predicate, str], object_entity: Union[Entity, RootEntity, str]) -> Triple:
        subject_entity = self.__get_entity(subject_entity)
        object_entity = self.__get_entity(object_entity)
        predicate = self.__get_predicate(predicate)

        triple_key = (subject_entity.wikidata_id, predicate.predicate_id, object_entity.wikidata_id)
        if triple_key not in self.__triples:
            raise ValueError(f"Triple {triple_key} not found.")
        return self.__triples[triple_key]

    def neighbors(self, entity: Union[Entity, RootEntity, str]) -> List[Triple]:
        entity = self.__get_entity(entity)
        entity_id = entity.wikidata_id

        neighbors = [
            self.__triples[(u, data['predicate'], v)]
            for u, v, data in self.__G.edges(entity_id, data=True)
        ]
        neighbors.extend([
            self.__triples[(u, data['predicate'], v)]
            for u, v, data in self.__G.in_edges(entity_id, data=True)
        ])
        return neighbors

    def degree(self, entity: Union[Entity, RootEntity, str]) -> int:
        entity = self.__get_entity(entity)
        return self.__G.degree(entity.wikidata_id)

    def ground_truth_summaries(self, root_entity: Union[RootEntity, str]) -> Set[Triple]:
        root_entity_id = self.__get_root_entity(root_entity).wikidata_id
        if root_entity_id not in self.__ground_truths:
            raise ValueError(f"No ground truth summaries found for root_entity: {root_entity_id}.")
        return self.__ground_truths[root_entity_id]

    def mark_triple_as_summary(self, root_entity: Union[RootEntity, str], triple: Union[Triple, Tuple[str, str, str]]):
        root_entity_id = self.__get_entity(root_entity).wikidata_id
        triple = self.__get_triple(triple)
        if root_entity_id not in {triple.subject_entity.wikidata_id, triple.object_entity.wikidata_id}:
            raise ValueError(
                f"Root entity: {root_entity_id} should be either subject or object of the triple to be marked as summary.")

        self.__predicted_summaries[root_entity_id].add(triple)

    def mark_triples_as_summaries(self, root_entity: RootEntity | str, triples: List[Triple | Tuple[str, str, str]]):
        for triple in triples:
            self.mark_triple_as_summary(root_entity, triple)
