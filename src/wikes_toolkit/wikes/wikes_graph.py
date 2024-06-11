import logging
from collections import defaultdict
from typing import Union, Tuple, List, Optional, Dict

import networkx as nx

from wikes_toolkit.base.graph_components import Entity, RootEntity, Triple, Predicate
from wikes_toolkit.base.versions import DatasetName
from wikes_toolkit.wikes.wikies_graph_components import WikiBaseWikESGraph, WikiEntity, WikiRootEntity, WikiPredicate, \
    WikiTriple

logger = logging.getLogger(__name__)


class WikESGraph(WikiBaseWikESGraph):

    def __init__(self,
                 G: nx.MultiDiGraph,
                 dataset: DatasetName,
                 root_entity_formatter: Optional[callable] = None,
                 entity_formatter: Optional[callable] = None,
                 predicate_formatter: Optional[callable] = None,
                 triple_formatter: Optional[callable] = None
                 ):
        super().__init__(G, dataset, root_entity_formatter, entity_formatter, predicate_formatter, triple_formatter)

    def _initialize(self):
        self._entities: Dict[str, WikiEntity] = {}
        self._root_entities: Dict[str, WikiRootEntity] = {}
        self._predicates: Dict[str, WikiPredicate] = {}
        self._triples: Dict[Tuple[str, str, str], WikiTriple] = {}
        self._ground_truths: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
        logger.debug("Initializing WikESGraph...")
        for node, data in self._G.nodes(data=True):
            if data.get('is_root', False):
                root_entity = WikiRootEntity(
                    identifier=node,
                    wikidata_label=data.get('wikidata_label'),
                    wikidata_description=data.get('wikidata_desc'),
                    wikipedia_id=data.get('wikipedia_id'),
                    wikipedia_title=data.get('wikipedia_title'),
                    category=data.get('category'),
                    str_formatter=self._root_entity_formatter
                )
                self._root_entities[node] = root_entity

            entity = WikiEntity(
                identifier=node,
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
                self._predicates[predicate_id] = WikiPredicate(
                    predicate_id=predicate_id,
                    label=data.get('predicate_label'),
                    description=data.get('predicate_desc'),
                    str_formatter=self._predicate_formatter
                )

            triple = WikiTriple(
                subject_entity=self._entities[u],
                predicate=self._predicates[predicate_id],
                object_entity=self._entities[v],
                str_formatter=self._triple_formatter
            )
            self._triples[(u, predicate_id, v)] = triple
            if 'summary_for' in data:
                self._ground_truths[data['summary_for']].append(
                    (
                        triple.subject_entity.identifier,
                        triple.predicate.predicate_id,
                        triple.object_entity.identifier
                    )
                )
        logger.debug(f"Triples: {len(self._triples)} initialized.")

    def root_entities(self) -> List[WikiRootEntity]:
        return super().root_entities()

    def entities(self) -> List[WikiEntity]:
        return super().entities()

    def triples(self) -> List[WikiTriple]:
        return super().triples()

    def predicates(self) -> List[WikiPredicate]:
        return super().predicates()

    def fetch_entity(self, entity: Union[Entity, str]) -> WikiEntity:
        return super().fetch_entity(entity)

    def fetch_root_entity(self, entity: Union[RootEntity, str]) -> WikiRootEntity:
        return super().fetch_root_entity(entity)

    def fetch_predicate(self, predicate: Union[Predicate, str]) -> WikiPredicate:
        return super().fetch_predicate(predicate)

    def fetch_triple(self, triple: Union[
        Triple, Tuple[
            Union[Entity, RootEntity, str],
            Union[Predicate, str],
            Union[Entity, RootEntity, str]
        ],

    ]) -> WikiTriple:
        return super().fetch_triple(triple)

    def neighbors(self, entity: Union[Entity, str]) -> List[WikiEntity]:
        return super().neighbors(entity)
