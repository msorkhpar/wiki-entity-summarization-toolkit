from __future__ import annotations

import logging
from abc import abstractmethod, ABC
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Tuple, Callable, List, TypeVar, Type

import networkx as nx
import pandas as pd

from wikes_toolkit.base.versions import DatasetName

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    identifier: str
    str_formatter: Optional[Callable[[Entity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Entity(identifier={self.identifier})"

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)


@dataclass
class RootEntity(Entity):
    category: Optional[str] = None
    str_formatter: Optional[Callable[[RootEntity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"RootEntity(identifier={self.identifier})"

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)


@dataclass
class Predicate:
    predicate_id: str
    str_formatter: Optional[Callable[[Predicate], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Predicate(predicate_id={self.predicate_id})"

    def __eq__(self, other):
        return self.predicate_id == other.predicate_id

    def __hash__(self):
        return hash(self.predicate_id)


@dataclass
class Triple:
    subject_entity: Entity
    predicate: Predicate
    object_entity: Entity
    str_formatter: Optional[Callable[[Triple], str]] = field(default=None, repr=False)

    def key(self):
        return self.subject_entity.identifier, self.predicate.predicate_id, self.object_entity.identifier

    def __iter__(self):
        return iter([self.subject_entity, self.predicate, self.object_entity])

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Triple(({self.subject_entity.identifier})-[{self.predicate.predicate_id}]->({self.object_entity.identifier})"

    def __eq__(self, other):
        return (
                self.subject_entity.identifier == other.subject_entity.identifier
                and self.predicate.predicate_id == other.predicate.predicate_id
                and self.object_entity.identifier == other.object_entity.identifier
        )

    def __hash__(self):
        return hash(self.key())


ROOT_E = TypeVar('ROOT_E', bound=RootEntity)
E = TypeVar('E', bound=Entity)
T = TypeVar('T', bound=Triple)
P = TypeVar('P', bound=Predicate)


class BaseESGraph(ABC):
    _dataset_name: DatasetName
    _entities: Union[Dict[str, Entity], pd.DataFrame]
    _root_entities: Union[Dict[str, RootEntity], pd.DataFrame]
    _predicates: Union[Dict[str, Predicate], pd.DataFrame]
    _triples: Union[Dict[Tuple[str, str, str], Triple], pd.DataFrame]
    _ground_truths: Union[Dict[str, List[Tuple[str, str, str]]], pd.DataFrame]
    _predicted_summaries: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    _G: nx.MultiDiGraph
    _root_entity_formatter: Callable
    _entity_formatter: Callable
    _predicate_formatter: Callable
    _triple_formatter = Callable

    def __init__(self, G: nx.MultiDiGraph, dataset: DatasetName,
                 root_type: Type, entity_type: Type,
                 predicate_type: Type, triple_type: Type,
                 root_entity_formatter: Optional[callable] = None,
                 entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None,
                 triple_formatter: Optional[callable] = None):
        self._G: nx.MultiDiGraph = G
        self._dataset_name = dataset
        self._root_type = root_type
        self._entity_type = entity_type
        self._predicate_type = predicate_type
        self._triple_type = triple_type
        self._root_entity_formatter = root_entity_formatter
        self._entity_formatter = entity_formatter
        self._predicate_formatter = predicate_formatter
        self._triple_formatter = triple_formatter
        self._initialize()

    @abstractmethod
    def _initialize(self):
        pass

    @abstractmethod
    def root_entities(self):
        if isinstance(self._root_entities, pd.DataFrame):
            return self._root_entities
        else:
            return list(self._root_entities.values())

    def root_entity_ids(self) -> List[str]:
        if isinstance(self._root_entities, pd.DataFrame):
            return self._root_entities.index.tolist()
        else:
            return list(self._root_entities.keys())

    @abstractmethod
    def entities(self):
        if isinstance(self._entities, pd.DataFrame):
            return self._entities
        else:
            return list(self._entities.values())

    @abstractmethod
    def triples(self):
        if isinstance(self._triples, pd.DataFrame):
            return self._triples
        else:
            return list(self._triples.values())

    @abstractmethod
    def predicates(self):
        if isinstance(self._predicates, pd.DataFrame):
            return self._predicates
        else:
            return list(self._predicates.values())

    def total_entities(self) -> int:
        if isinstance(self._entities, pd.DataFrame):
            return self._entities.shape[0]
        else:
            return len(self._entities)

    def total_triples(self) -> int:
        if isinstance(self._triples, pd.DataFrame):
            return self._triples.shape[0]
        else:
            return len(self._triples)

    @abstractmethod
    def fetch_entity(self, entity: Union[Entity, str, pd.Series]):

        if isinstance(self._entities, pd.DataFrame):
            try:
                if isinstance(entity, pd.Series):
                    entity = entity.name
                entity = self._entities.loc[entity]
            except KeyError:
                raise ValueError(f"Entity with identifier: {entity} not found.")
            return entity
        if isinstance(entity, self._root_type) or isinstance(entity, self._entity_type):
            identifier = entity.identifier
        else:
            identifier = entity
        if identifier not in self._entities:
            raise ValueError(f"Entity with identifier: {identifier} not found.")
        return self._entities[identifier]

    @abstractmethod
    def fetch_root_entity(self, entity: Union[RootEntity, str, pd.Series]):
        if isinstance(self._root_entities, pd.DataFrame):
            try:
                if isinstance(entity, pd.Series):
                    entity = entity.name
                entity = self._root_entities.loc[entity]
            except KeyError:
                raise ValueError(f"Entity with identifier: {entity} is not a root entity.")
            return entity
        else:
            if isinstance(entity, self._entity_type) and not isinstance(entity, self._root_type) and not isinstance(
                    entity, str):
                raise ValueError(f"Entity {entity} is not a root entity.")
            if isinstance(entity, self._root_type):
                identifier = entity.identifier
            else:
                identifier = entity
            if identifier not in self._root_entities:
                raise ValueError(f"Entity with identifier: {identifier} not found in root entities.")
            return self._root_entities[identifier]

    def fetch_root_entity_id(self, entity: Union[RootEntity, str, pd.Series]) -> str:
        return self.fetch_root_entity(entity).identifier

    @abstractmethod
    def fetch_predicate(self, predicate: Union[Predicate, str, pd.Series]):
        if isinstance(self._predicates, pd.DataFrame):
            try:
                if isinstance(predicate, pd.Series):
                    predicate = predicate.name
                predicate = self._predicates.loc[predicate]
            except KeyError:
                raise ValueError(f"Predicate with predicate_id: {predicate} not found")
            return predicate
        else:
            if isinstance(predicate, self._predicate_type):
                predicate_id = predicate.predicate_id
            else:
                predicate_id = predicate

            if predicate_id not in self._predicates:
                raise ValueError(f"Predicate with predicate_id: {predicate_id} not found")
            return self._predicates[predicate_id]

    @abstractmethod
    def fetch_triple(self, triple: Union[
        Triple, Tuple[
            Union[Entity, str],
            Union[Predicate, str],
            Union[Entity, str]
        ],
        pd.Series
    ]):
        if isinstance(self._triples, pd.DataFrame):
            if isinstance(triple, pd.Series):
                triple = triple['subject'], triple['predicate'], triple['object']
            triple = self._triples[
                (self._triples['subject'] == triple[0]) &
                (self._triples['predicate'] == triple[1]) &
                (self._triples['object'] == triple[2])
                ]
            if triple.empty:
                raise ValueError(f"Triple ({triple[0]})-[{triple[1]}]->({triple[2]}) not found.")
            return triple.iloc[0]
        else:
            if isinstance(triple, Tuple):
                subject_entity = self.fetch_entity(triple[0])
                predicate = self.fetch_predicate(triple[1])
                object_entity = self.fetch_entity(triple[2])
                triple_key = (subject_entity.identifier, predicate.predicate_id, object_entity.identifier)
            else:
                triple_key = (
                    triple.subject_entity.identifier,
                    triple.predicate.predicate_id,
                    triple.object_entity.identifier
                )
            if triple_key not in self._triples:
                raise ValueError(f"Triple {triple_key} not found.")
            return self._triples[triple_key]

    def fetch_triple_ids(self, triple: Union[
        Triple, Tuple[
            Union[Entity, str],
            Union[Predicate, str],
            Union[Entity, str]
        ],
        pd.Series
    ]) -> Tuple[str, str, str]:
        if isinstance(self._triples, pd.DataFrame):
            return self.fetch_triple(triple)[['subject', 'predicate', 'object']].apply(tuple, axis=1)
        else:
            triple = self.fetch_triple(triple)
            return triple.subject_entity.identifier, triple.predicate.predicate_id, triple.object_entity.identifier

    @abstractmethod
    def neighbors(self, entity: Union[Entity, str, pd.Series]):
        if isinstance(self._entities, pd.DataFrame):
            entity = self.fetch_entity(entity)
            return self._triples[
                (self._triples['subject'] == entity.name) |
                (self._triples['object'] == entity.name)
                ]
        else:
            entity = self.fetch_entity(entity)
            entity_id = entity.identifier
            neighbors = [
                self._triples[(u, data['predicate'], v)]
                for u, v, data in self._G.edges(entity_id, data=True)
            ]
            neighbors.extend([
                self._triples[(u, data['predicate'], v)]
                for u, v, data in self._G.in_edges(entity_id, data=True)
            ])
            return neighbors

    def degree(self, entity: Union[Entity, str, pd.Series]) -> int:
        if isinstance(self._entities, pd.DataFrame):
            return self.neighbors(entity).shape[0]
        else:
            entity = self.fetch_entity(entity)
            return self._G.degree(entity.identifier)

    def _add_predication_if_not_exists(self, root_entity: str, triple: Tuple[str, str, str]):
        if triple not in self._predicted_summaries[root_entity]:
            self._predicted_summaries[root_entity].append(triple)

    def mark_triple_as_summary(self, root_entity: Union[RootEntity, str, pd.Series], triple: Union[
        Triple,
        Tuple[
            Union[Entity, str],
            Union[Predicate, str],
            Union[Entity, str]
        ],
        pd.Series
    ]):
        if isinstance(self._entities, pd.DataFrame):
            if isinstance(triple, pd.Series):
                raise ValueError("Triple should be a Tuple of (subject, predicate, object) or a pd.Series.")
            identifier = str(self.fetch_root_entity(root_entity).name)
            triple = self.fetch_triple(triple)

            if identifier != triple['subject'] and identifier != triple['object']:
                raise ValueError(f"Root entity: {identifier} should be either a subject or an"
                                 f" object of the triple in a summary.")

            self._add_predication_if_not_exists(identifier, (triple['subject'], triple['predicate'], triple['object']))
        else:
            root_entity_id = self.fetch_entity(root_entity).identifier
            triple = self.fetch_triple(triple)
            if root_entity_id not in {triple.subject_entity.identifier, triple.object_entity.identifier}:
                raise ValueError(
                    f"Root entity: {root_entity_id} should be either a subject or an object of the triple in a summary.")

            self._add_predication_if_not_exists(
                root_entity_id,
                (
                    triple.subject_entity.identifier,
                    triple.predicate.predicate_id,
                    triple.object_entity.identifier
                )
            )

    def clear_summaries(self):
        self._predicted_summaries.clear()

    def mark_triples_as_summaries(
            self,
            root_entity: Union[RootEntity, str, pd.Series],
            triples: List[Union[Triple, Union[Triple, Tuple[str, str, str], pd.Series]]]
    ):
        for triple in triples:
            self.mark_triple_as_summary(root_entity, triple)

    def predications(self) -> Dict[str, List[Tuple[str, str, str]]]:
        return self._predicted_summaries

    def predications_for_root(self, identifier: str) -> List[Tuple[str, str, str]]:
        if identifier in self._predicted_summaries:
            return self._predicted_summaries[identifier]
        else:
            return list()

    @abstractmethod
    def ground_truths(self, root_entity: Union[RootEntity, str, pd.Series]) -> List[Tuple[str, str, str]]:
        if isinstance(self._ground_truths, pd.DataFrame):
            root_entity = self.fetch_root_entity(root_entity)
            return self._ground_truths[self._ground_truths.index == root_entity.name]
        else:
            root_entity_id = self.fetch_root_entity(root_entity).identifier
            if root_entity_id not in self._ground_truths:
                raise ValueError(f"No ground truth summaries found for root_entity: {root_entity_id}.")
            return self._ground_truths[root_entity_id]

    @abstractmethod
    def ground_truth_triple_ids(self, root_entity: Union[RootEntity, str, pd.Series]) -> List[Tuple[str, str, str]]:
        if isinstance(self._ground_truths, pd.DataFrame):
            return list(self.ground_truths(root_entity)[['subject', 'predicate', 'object']].apply(tuple, axis=1))
        else:
            return [(s, p, o) for s, p, o in self.ground_truths(root_entity)]