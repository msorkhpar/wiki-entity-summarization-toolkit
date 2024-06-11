from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple, Callable, List

import networkx as nx

from wikes_toolkit.base.graph_components import Entity, Predicate, Triple, BaseESGraph
from wikes_toolkit.base.versions import DatasetName

logger = logging.getLogger(__name__)


@dataclass
class WikiEntity(Entity):
    identifier: str
    wikidata_label: Optional[str] = None
    wikidata_description: Optional[str] = None
    wikipedia_id: Optional[int] = None
    wikipedia_title: Optional[str] = None
    str_formatter: Optional[Callable[[WikiEntity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Entity(identifier={self.identifier}, wikidata_label={self.wikidata_label})"

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)


@dataclass
class WikiRootEntity(WikiEntity):
    category: Optional[str] = None
    str_formatter: Optional[Callable[[WikiRootEntity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"RootEntity(id={self.identifier}, wikidata_label={self.wikidata_label})"

    def __eq__(self, other):
        return self.identifier == other.id

    def __hash__(self):
        return hash(self.identifier)


@dataclass
class WikiPredicate(Predicate):
    predicate_id: str
    label: Optional[str] = None
    description: Optional[str] = None
    str_formatter: Optional[Callable[[WikiPredicate], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"Predicate(predicate_id={self.predicate_id}, label={self.label})"

    def __eq__(self, other):
        return self.predicate_id == other.predicate_id

    def __hash__(self):
        return hash(self.predicate_id)


@dataclass
class WikiTriple(Triple):
    subject_entity: WikiEntity
    predicate: WikiPredicate
    object_entity: WikiEntity
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
                self.subject_entity.identifier == other.subject_entity.id
                and self.predicate.predicate_id == other.predicate.predicate_id
                and self.object_entity.identifier == other.object_entity.id
        )

    def __hash__(self):
        return hash(self.key())


class WikiBaseWikESGraph(BaseESGraph):
    def __init__(self, G: nx.MultiDiGraph,
                 dataset: DatasetName,
                 root_entity_formatter: Optional[callable] = None,
                 entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None,
                 triple_formatter: Optional[callable] = None):
        super().__init__(
            G, dataset,
            WikiRootEntity, WikiEntity, WikiTriple, WikiPredicate,
            root_entity_formatter, entity_formatter, predicate_formatter, triple_formatter
        )

    @abstractmethod
    def _initialize(self):
        pass

    def ground_truths(self, root_entity: Union[WikiRootEntity, str]):
        return super().ground_truths(root_entity)

    def ground_truth_triple_ids(self, root_entity: Union[WikiRootEntity, str]) -> List[Tuple[str, str, str]]:
        return super().ground_truth_triple_ids(root_entity)
