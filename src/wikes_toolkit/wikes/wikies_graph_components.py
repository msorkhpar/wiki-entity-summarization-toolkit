from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple, Callable, List, Dict

import networkx as nx
import pandas as pd

from wikes_toolkit.base.graph_components import Entity, Predicate, Triple, BaseESGraph
from wikes_toolkit.base.versions import DatasetName
from wikes_toolkit.wikes.wikes_eval import WikESSummaryEvaluator

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
        return f"RootEntity(identifier={self.identifier}, wikidata_label={self.wikidata_label})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.identifier == other
        return self.identifier == other.identifier

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


class WikESBaseGraph(BaseESGraph):
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

    def ground_truths(self, root_entity: Union[WikiRootEntity, str, pd.Series]) -> Union[
        List[Tuple[str, str, str]],
        pd.Series
    ]:
        if isinstance(self._ground_truths, pd.DataFrame):
            root_entity = self.fetch_root_entity(root_entity)
            return self._ground_truths[self._ground_truths.index == root_entity.name]
        else:
            root_entity_id = self.fetch_root_entity(root_entity).identifier
            if root_entity_id not in self._ground_truths:
                raise ValueError(f"No ground truth summaries found for root_entity: {root_entity_id}.")
            return self._ground_truths[root_entity_id]

    def ground_truth_triple_ids(self, root_entity: Union[WikiRootEntity, str, pd.Series]) -> List[Tuple[str, str, str]]:
        if isinstance(self._ground_truths, pd.DataFrame):
            return list(self.ground_truths(root_entity)[['subject', 'predicate', 'object']].apply(tuple, axis=1))
        else:
            return [(s, p, o) for s, p, o in self.ground_truths(root_entity)]

    def all_ground_truth_triple_ids(self, k: int = None) -> Dict[str, List[Tuple[str, str, str]]]:
        if k is not None:
            result = {}
            for root_entity in self.root_entity_ids():
                ground_truth_triples = self.ground_truth_triple_ids(root_entity)
                if len(ground_truth_triples) < k:
                    result[root_entity] = ground_truth_triples
                else:
                    result[root_entity] = self.ground_truth_triple_ids(root_entity)[:k]
        return {root_entity: self.ground_truth_triple_ids(root_entity) for root_entity in self.root_entity_ids()}

    def f1_score(self, k: int = None, no_rel: bool = False):
        return WikESSummaryEvaluator(
            super().root_entities(),
            self._ground_truths,
            self._predicted_summaries
        ).evaluate_f1(k, no_rel)

    def map_score(self, k: int = None, no_rel: bool = False):
        return WikESSummaryEvaluator(
            super().root_entities(),
            self._ground_truths,
            self._predicted_summaries
        ).evaluate_map(k, no_rel)
