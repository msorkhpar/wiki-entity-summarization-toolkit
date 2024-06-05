import logging
from typing import List, Tuple, Set, Union

import networkx as nx
import pandas as pd

from wikes_toolkit.wikies_graph_components import BaseWikESGraph

logger = logging.getLogger(__name__)


class PandasWikESGraph(BaseWikESGraph):

    def __init__(self, G: nx.MultiDiGraph):
        super().__init__(G)

    def _initialize(self):
        logger.debug("Initializing PandasWikESGraph...")

        self._entities = pd.DataFrame(columns=[
            'wikidata_id', 'wikidata_label', 'wikidata_description', 'wikipedia_id',
            'wikipedia_title'
        ])

        self._root_entities = pd.DataFrame(columns=[
            'wikidata_id', 'wikidata_label', 'wikidata_description', 'wikipedia_id',
            'wikipedia_title', 'category'
        ])

        nodes_data = [
            {
                'wikidata_id': node,
                'wikidata_label': data.get('wikidata_label'),
                'wikidata_description': data.get('wikidata_desc'),
                'wikipedia_id': data.get('wikipedia_id'),
                'wikipedia_title': data.get('wikipedia_title')
            }
            for node, data in self._G.nodes(data=True)
        ]
        self._entities = pd.DataFrame(nodes_data).set_index('wikidata_id')
        logger.debug(f"Entities: {self._entities.shape[0]} initialized.")

        nodes_data = [
            {
                'wikidata_id': node,
                'wikidata_label': data.get('wikidata_label'),
                'wikidata_description': data.get('wikidata_desc'),
                'wikipedia_id': data.get('wikipedia_id'),
                'wikipedia_title': data.get('wikipedia_title'),
                'category': data.get('category', None)
            }
            for node, data in self._G.nodes(data=True) if data.get('is_root', False)
        ]
        self._root_entities = pd.DataFrame(nodes_data).set_index('wikidata_id')
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
        return self._root_entities

    def root_entity_ids(self) -> List[str]:
        return self._root_entities.index.tolist()

    def entities(self) -> pd.DataFrame:
        return self._entities

    def triples(self) -> pd.DataFrame:
        return self._triples

    def predicates(self) -> List:
        return self._predicates.index.tolist()

    def total_entities(self) -> int:
        return self._entities.shape[0]

    def total_triples(self) -> int:
        return self._triples.shape[0]

    def fetch_entity(self, wikidata_id: Union[str, pd.Series]) -> pd.Series:
        try:
            if isinstance(wikidata_id, pd.Series):
                wikidata_id = wikidata_id.name
            entity = self._entities.loc[wikidata_id]
        except KeyError:
            raise ValueError(f"Entity with wikidata_id: {wikidata_id} not found.")
        return entity

    def fetch_root_entity(self, wikidata_id: Union[str, pd.Series]) -> pd.Series:
        if isinstance(wikidata_id, pd.Series):
            wikidata_id = wikidata_id.name
        try:
            entity = self._root_entities.loc[wikidata_id]
        except KeyError:
            raise ValueError(f"Entity with wikidata_id: {wikidata_id} is not a root entity.")
        return entity

    def fetch_root_entity_id(self, wikidata_id: Union[str, pd.Series]) -> str:
        return str(self.fetch_root_entity(wikidata_id).name)

    def fetch_predicate(self, predicate: str) -> pd.Series:
        try:
            predicate = self._predicates.loc[predicate]
        except KeyError:
            raise ValueError(f"Predicate with predicate_id: {predicate} not found")
        return predicate

    def fetch_triple(self, triple: Tuple[str, str, str]) -> pd.Series:
        triple = self._triples[
            (self._triples['subject'] == triple[0]) &
            (self._triples['predicate'] == triple[1]) &
            (self._triples['object'] == triple[2])
            ]
        if triple.empty:
            raise ValueError(f"Triple ({triple[0]})-[{triple[1]}]->({triple[2]}) not found.")
        return triple.iloc[0]

    def fetch_triple_ids(self, triple: Tuple[str, str, str]) -> Tuple[str, str, str]:
        return self.fetch_triple(triple)[['subject', 'predicate', 'object']].apply(tuple, axis=1)

    def neighbors(self, wikidata_id: Union[str, pd.Series]) -> pd.DataFrame:
        entity = self.fetch_entity(wikidata_id)
        return self._triples[
            (self._triples['subject'] == entity.name) |
            (self._triples['object'] == entity.name)
            ]

    def degree(self, wikidata_id: str) -> int:
        return self.neighbors(wikidata_id).shape[0]

    def ground_truths(self, wikidata_id: Union[str, pd.Series]) -> pd.DataFrame:
        root_entity = self.fetch_root_entity(wikidata_id)
        return self._ground_truths[self._ground_truths.index == root_entity.name]

    def ground_truth_triple_ids(self, wikidata_id: str) -> Set[Tuple[str, str, str]]:
        return set(self.ground_truths(wikidata_id)[['subject', 'predicate', 'object']].apply(tuple, axis=1))

    def mark_triple_as_summary(self, root_entity: str, triple: Tuple[str, str, str]):
        if not isinstance(triple, Tuple):
            raise ValueError("Triple should be a Tuple of (subject, predicate, object).")
        wikidata_id = str(self.fetch_root_entity(root_entity).name)
        triple = self.fetch_triple(triple)

        if wikidata_id != triple['subject'] and root_entity != triple['object']:
            raise ValueError(f"Root entity: {root_entity} should be either a subject or an"
                             f" object of the triple in a summary.")

        self._predicted_summaries[wikidata_id].add(
            (triple['subject'], triple['predicate'], triple['object'])
        )
