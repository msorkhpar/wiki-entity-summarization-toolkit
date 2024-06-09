import logging
from typing import Union, Tuple

import networkx as nx
import pandas as pd

from wikes_toolkit.base.graph_components import Entity, Triple, Predicate, RootEntity
from wikes_toolkit.wikes.wikies_graph_components import WikiBaseWikESGraph

logger = logging.getLogger(__name__)


class PandasWikESGraph(WikiBaseWikESGraph):

    def __init__(self, G: nx.MultiDiGraph):
        super().__init__(G)

    def _initialize(self):
        logger.debug("Initializing PandasWikESGraph...")

        self._entities = pd.DataFrame(columns=[
            'identifier', 'wikidata_label', 'wikidata_description', 'wikipedia_id',
            'wikipedia_title'
        ])

        self._root_entities = pd.DataFrame(columns=[
            'identifier', 'wikidata_label', 'wikidata_description', 'wikipedia_id',
            'wikipedia_title', 'category'
        ])

        nodes_data = [
            {
                'identifier': node,
                'wikidata_label': data.get('wikidata_label'),
                'wikidata_description': data.get('wikidata_desc'),
                'wikipedia_id': data.get('wikipedia_id'),
                'wikipedia_title': data.get('wikipedia_title')
            }
            for node, data in self._G.nodes(data=True)
        ]
        self._entities = pd.DataFrame(nodes_data).set_index('identifier')
        logger.debug(f"Entities: {self._entities.shape[0]} initialized.")

        nodes_data = [
            {
                'identifier': node,
                'wikidata_label': data.get('wikidata_label'),
                'wikidata_description': data.get('wikidata_desc'),
                'wikipedia_id': data.get('wikipedia_id'),
                'wikipedia_title': data.get('wikipedia_title'),
                'category': data.get('category', None)
            }
            for node, data in self._G.nodes(data=True) if data.get('is_root', False)
        ]
        self._root_entities = pd.DataFrame(nodes_data).set_index('id')
        logger.debug(f"Root entities: {self._root_entities.shape[0]} initialized.")
        del nodes_data

        self._triples = pd.DataFrame(columns=['subject', 'predicate', 'object'])
        self._ground_truths = pd.DataFrame(columns=['root_entity', 'subject', 'predicate', 'object'])
        self._predicates = pd.DataFrame(columns=['predicate', 'predicate_label', 'predicate_desc'])

        logger.debug("Initializing triples...")
        edges_data = []
        ground_truths_data = []
        predicates_data = []

        for u, v, data in self._G.edges(data=True):
            predicate_id = data['predicate']
            edges_data.append({'subject': u, 'predicate': predicate_id, 'object': v})

            if predicate_id not in self._predicates.index:
                predicates_data.append({
                    'predicate': predicate_id,
                    'predicate_label': data.get('predicate_label'),
                    'predicate_desc': data.get('predicate_desc')
                })

            if 'summary_for' in data:
                ground_truths_data.append({
                    'root_entity': data['summary_for'],
                    'subject': u,
                    'predicate': predicate_id,
                    'object': v
                })

        self._triples = pd.DataFrame(edges_data)
        self._predicates = pd.DataFrame(predicates_data).set_index('predicate')
        self._ground_truths = pd.DataFrame(ground_truths_data).set_index('root_entity')
        del edges_data, predicates_data, ground_truths_data
        logger.debug(f"Triples: {self._triples.shape[0]} initialized.")

    def root_entities(self) -> pd.DataFrame:
        return super().root_entities()

    def entities(self) -> pd.DataFrame:
        return super().entities()

    def triples(self) -> pd.DataFrame:
        return super().triples()

    def predicates(self) -> pd.DataFrame:
        return super().predicates()

    def fetch_entity(self, entity: Union[Entity, str]) -> pd.Series:
        return super().fetch_entity(entity)

    def fetch_root_entity(self, entity: Union[RootEntity, str]) -> pd.Series:
        return super().fetch_root_entity(entity)

    def fetch_predicate(self, predicate: Union[Predicate, str]) -> pd.Series:
        return super().fetch_predicate(predicate)

    def fetch_triple(self, triple: Union[
        Triple, Tuple[
            Union[Entity, str],
            Union[Predicate, str],
            Union[Entity, str]
        ],

    ]) -> pd.Series:
        return super().fetch_triple(triple)

    def neighbors(self, entity: Union[Entity, str]) -> pd.DataFrame:
        return super().neighbors(entity)
