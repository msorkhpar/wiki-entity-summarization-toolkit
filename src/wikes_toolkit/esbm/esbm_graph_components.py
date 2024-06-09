from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple, Set, Callable, List, Dict

import networkx as nx

from wikes_toolkit.base.graph_components import Entity, Predicate, Triple, BaseESGraph
from wikes_toolkit.base.versions import DatasetName

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
class ESBMRootEntity(ESBMEntity):
    eid: int = None
    category: Optional[str] = None

    def __str__(self):
        if self.str_formatter:
            return self.str_formatter(self)
        return f"ESBMRootEntity(identifier={self.identifier}, eid:{self.eid}, category={self.category})"

    def __eq__(self, other):
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
    subject_entity: Union[ESBMEntity, ESBMRootEntity]
    predicate: ESBMPredicate
    object_entity: Union[ESBMEntity, ESBMRootEntity]
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

    def __init__(self, G: nx.MultiDiGraph, dataset_name: DatasetName, entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None, triple_formatter: Optional[callable] = None):
        self._dataset_name = dataset_name
        super().__init__(G, ESBMRootEntity, ESBMEntity, ESBMTriple, ESBMPredicate, entity_formatter,
                         predicate_formatter,
                         triple_formatter)

    def ground_truths(self, root_entity: Union[ESBMRootEntity, str]):
        raise NotImplementedError("Instead of ground_truths, use gold_top5 and gold_top10 methods.")

    def ground_truth_triple_ids(self, root_entity: Union[ESBMRootEntity, str]) -> Set[Tuple[str, str, str]]:
        raise NotImplementedError("Instead of ground_truths, use gold_top5 and gold_top10 methods.")

    def all_gold_top_k(self, k: int) -> Dict[str, List[List[Tuple[str, str, str]]]]:
        pass

    def gold_top_5(self, root_entity: Union[ESBMRootEntity, str], annotator_index: int) -> List[Triple]:
        pass

    def gold_top_10(self, root_entity: Union[ESBMRootEntity, str], annotator_index: int) -> List[Triple]:
        pass
