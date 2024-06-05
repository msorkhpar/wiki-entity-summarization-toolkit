from __future__ import annotations

import logging
from abc import abstractmethod, ABC
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Tuple, Set, Callable

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    wikidata_id: str
    wikidata_label: Optional[str] = None
    wikidata_description: Optional[str] = None
    wikipedia_id: Optional[int] = None
    wikipedia_title: Optional[str] = None
    str_formatter: Optional[Callable[[Entity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Entity(wikidata_id={self.wikidata_id}, wikidata_label={self.wikidata_label})"

    def __eq__(self, other):
        return self.wikidata_id == other.wikidata_id

    def __hash__(self):
        return hash(self.wikidata_id)


@dataclass
class RootEntity(Entity):
    category: Optional[str] = None

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"RootEntity(wikidata_id={self.wikidata_id}, wikidata_label={self.wikidata_label})"

    def __eq__(self, other):
        return self.wikidata_id == other.wikidata_id

    def __hash__(self):
        return hash(self.wikidata_id)


@dataclass
class Predicate:
    predicate_id: str
    label: Optional[str] = None
    description: Optional[str] = None
    str_formatter: Optional[Callable[[Predicate], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Predicate(predicate_id={self.predicate_id}, label={self.label})"

    def __eq__(self, other):
        return self.predicate_id == other.predicate_id

    def __hash__(self):
        return hash(self.predicate_id)



@dataclass
class Triple:
    subject_entity: Union[Entity, RootEntity]
    predicate: Predicate
    object_entity: Union[Entity, RootEntity]
    str_formatter: Optional[Callable[[Triple], str]] = field(default=None, repr=False)

    def key(self):
        return self.subject_entity.wikidata_id, self.predicate.predicate_id, self.object_entity.wikidata_id

    def __iter__(self):
        return iter([self.subject_entity, self.predicate, self.object_entity])
    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Triple(({self.subject_entity.wikidata_id})-[{self.predicate.predicate_id}]->({self.object_entity.wikidata_id})"

    def __eq__(self, other):
        return (
                self.subject_entity.wikidata_id == other.subject_entity.wikidata_id
                and self.predicate.predicate_id == other.predicate.predicate_id
                and self.object_entity.wikidata_id == other.object_entity.wikidata_id
        )

    def __hash__(self):
        return hash(self.key())


class BaseWikESGraph(ABC):
    _entities: Union[Dict[str, Entity], pd.DataFrame]
    _root_entities: Union[Dict[str, RootEntity], pd.DataFrame]
    _predicates: Union[Dict[str, Predicate], pd.DataFrame]
    _triples: Union[Dict[Tuple[str, str, str], Triple], pd.DataFrame]
    _ground_truths: Union[Dict[str, Set[Triple]], pd.DataFrame]
    _predicted_summaries: Dict[str, Set[Tuple[str, str, str]]] = defaultdict(set)
    _entity_formatter: Callable
    _predicate_formatter: Callable
    _triple_formatter = Callable

    def __init__(self, G: nx.MultiDiGraph, entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None, triple_formatter: Optional[callable] = None):
        self._G: nx.MultiDiGraph = G
        self._entity_formatter = entity_formatter
        self._predicate_formatter = predicate_formatter
        self._triple_formatter = triple_formatter
        self._initialize()

    @abstractmethod
    def _initialize(self):
        pass

    @abstractmethod
    def root_entities(self):
        pass

    @abstractmethod
    def root_entity_ids(self) -> Set[str]:
        pass

    @abstractmethod
    def entities(self):
        pass

    @abstractmethod
    def triples(self):
        pass

    @abstractmethod
    def predicates(self):
        pass

    @abstractmethod
    def total_entities(self) -> int:
        pass

    @abstractmethod
    def total_triples(self) -> int:
        pass

    @abstractmethod
    def fetch_entity(self, entity: Union[Entity, RootEntity, str]):
        pass

    @abstractmethod
    def fetch_root_entity(self, entity: Union[RootEntity, str]):
        pass

    @abstractmethod
    def fetch_root_entity_id(self, entity: Union[RootEntity, str]) -> str:
        pass

    @abstractmethod
    def fetch_predicate(self, predicate: Union[Predicate, str]):
        pass

    @abstractmethod
    def fetch_triple(self, triple: Union[
        Triple, Tuple[
            Union[Entity, RootEntity, str],
            Union[Entity, RootEntity, str],
            Union[Entity, RootEntity, str]
        ],

    ]):
        pass

    @abstractmethod
    def fetch_triple_ids(self, triple: Union[
        Triple, Tuple[
            Union[Entity, RootEntity, str],
            Union[Entity, RootEntity, str],
            Union[Entity, RootEntity, str]
        ]
    ]) -> Tuple[str, str, str]:
        pass

    @abstractmethod
    def neighbors(self, entity: Union[Entity, RootEntity, str]):
        pass

    @abstractmethod
    def degree(self, entity: Union[Entity, RootEntity, str]) -> int:
        pass

    @abstractmethod
    def ground_truths(self, root_entity: Union[RootEntity, str]):
        pass

    @abstractmethod
    def ground_truth_triple_ids(self, root_entity: Union[RootEntity, str]) -> Set[Tuple[str, str, str]]:
        pass

    @abstractmethod
    def mark_triple_as_summary(self, root_entity: Union[RootEntity, str], triple: Union[Triple, Tuple[str, str, str]]):
        pass

    def clear_summaries(self):
        self._predicted_summaries.clear()

    def mark_triples_as_summaries(
            self,
            root_entity: Union[RootEntity, str],
            triples: Set[Union[Triple, Tuple[str, str, str]]]
    ):
        if isinstance(triples, list):
            triples = set(triples)
        for triple in triples:
            self.mark_triple_as_summary(root_entity, triple)

    def predications(self) -> Dict[str, Set[Tuple[str, str, str]]]:
        return self._predicted_summaries

    def predication_for_root(self, wikidata_id: str) -> Set[Tuple[str, str, str]]:
        if wikidata_id in self._predicted_summaries:
            return self._predicted_summaries[wikidata_id]
        else:
            return set()
