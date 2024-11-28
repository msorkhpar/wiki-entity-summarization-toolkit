from __future__ import annotations

import logging
import os
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple, Callable, List, Dict

import networkx as nx
import pandas as pd

from wikes_toolkit.base.graph_components import Entity, Predicate, Triple, BaseESGraph, RootEntity
from wikes_toolkit.base.versions import DatasetName
from wikes_toolkit.esbm.esbm_eval import ESBMSummaryEvaluator
from wikes_toolkit.esbm.esbm_nt_file_reader import extract_triples

logger = logging.getLogger(__name__)


@dataclass
class ESBMEntity(Entity):
    identifier: str
    str_formatter: Optional[Callable[[ESBMEntity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"ESBMEntity(identifier={self.identifier})"

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)


@dataclass
class ESBMRootEntity(ESBMEntity, RootEntity):
    eid: int = None
    category: Optional[str] = None
    str_formatter: Optional[Callable[[ESBMRootEntity], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"ESBMRootEntity(identifier={self.identifier}, eid:{self.eid}, category={self.category})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.identifier == other
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)


@dataclass
class ESBMPredicate(Predicate):
    predicate_id: str
    str_formatter: Optional[Callable[[ESBMPredicate], str]] = field(default=None, repr=False)

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"ESBMPredicate(predicate_id={self.predicate_id})"

    def __eq__(self, other):
        return self.predicate_id == other.predicate_id

    def __hash__(self):
        return hash(self.predicate_id)


@dataclass
class ESBMTriple(Triple):
    subject_entity: ESBMEntity
    predicate: ESBMPredicate
    object_entity: ESBMEntity
    str_formatter: Optional[Callable[[Triple], str]] = field(default=None, repr=False)

    def key(self):
        return self.subject_entity.identifier, self.predicate.predicate_id, self.object_entity.identifier

    def __iter__(self):
        return iter([self.subject_entity, self.predicate, self.object_entity])

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"ESBMTriple(({self.subject_entity.identifier})-[{self.predicate.predicate_id}]->({self.object_entity.identifier})"

    def __eq__(self, other):
        return (
                self.subject_entity.identifier == other.subject_entity.identifier
                and self.predicate.predicate_id == other.predicate.predicate_id
                and self.object_entity.identifier == other.object_entity.identifier
        )

    def __hash__(self):
        return hash(self.key())


class ESBMBaseGraph(BaseESGraph):
    _dataset_name: DatasetName

    def __init__(self, G: nx.MultiDiGraph, dataset: DatasetName,
                 root_entity_formatter: Optional[callable] = None,
                 entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None,
                 triple_formatter: Optional[callable] = None):
        super().__init__(
            G, dataset,
            ESBMRootEntity, ESBMEntity, ESBMTriple, ESBMPredicate,
            root_entity_formatter, entity_formatter, predicate_formatter, triple_formatter
        )

    @abstractmethod
    def all_gold_top_k(self, k: int) -> Dict[str, List[List[Tuple[str, str, str]]]]:
        pass

    @abstractmethod
    def gold_top_5(self, root_entity: Union[ESBMRootEntity, str, pd.Series], annotator_index: int) -> Union[
        List[ESBMTriple], pd.DataFrame
    ]:
        pass

    @abstractmethod
    def gold_top_10(self, root_entity: Union[ESBMRootEntity, str, pd.Series], annotator_index: int) -> Union[
        List[ESBMTriple], pd.DataFrame
    ]:
        pass

    def fetch_root_entity(self, entity: Union[RootEntity, str, int]) -> Union[ESBMRootEntity, pd.Series]:
        if isinstance(entity, int):
            root_entities = self.root_entities()
            if isinstance(root_entities, list):
                for r in root_entities:
                    if r.eid == entity:
                        return r
                raise ValueError(f"Entity with eid: {entity} not found in root entities.")
            else:
                target = root_entities[root_entities['eid'] == entity]
                if not target.empty:
                    return target.iloc[0]
        return super().fetch_root_entity(entity)

    def f1_score(self, k: int = None, no_rel: bool = False):
        if k is None:
            raise ValueError("top_k should be provided for ESBM")
        if k not in [5, 10]:
            raise ValueError("k should be 5 or 10")
        return ESBMSummaryEvaluator(
            super().root_entity_ids(),
            self.all_gold_top_k(k),
            self._predicted_summaries,
            k
        ).evaluate_f1(no_rel)

    def map_score(self, k: int = None, no_rel: bool = False):
        if k is None:
            raise ValueError("top_k should be provided for ESBM")
        if k not in [5, 10]:
            raise ValueError("k should be 5 or 10")
        return ESBMSummaryEvaluator(
            super().root_entity_ids(),
            self.all_gold_top_k(k),
            self._predicted_summaries,
            k
        ).evaluate_map(no_rel)

    def mark_nt_file_as_summary(self, root_entity: Union[ESBMRootEntity, str, int], nt_file_path):
        if not os.path.exists(nt_file_path):
            raise ValueError(f"N-Triples summary file does not exist under path {nt_file_path}")

        root_entity = self.fetch_root_entity(root_entity)
        triples = extract_triples(nt_file_path)
        triples = [self.fetch_triple(t) for t in triples]
        super().mark_triples_as_summaries(root_entity, triples)
