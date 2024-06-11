import logging
from typing import Union, Tuple

import networkx as nx
import pandas as pd

from wikes_toolkit.base.versions import DatasetName
from wikes_toolkit.wikes import wikes_csv_exporter
from wikes_toolkit.wikes.wikies_graph_components import WikiBaseWikESGraph

logger = logging.getLogger(__name__)


class PandasWikESGraph(WikiBaseWikESGraph):

    def __init__(self, G: nx.MultiDiGraph, dataset_name: DatasetName):
        super().__init__(G, dataset_name)

    def _initialize(self):
        logger.debug("Initializing PandasWikESGraph...")

        nodes_data = [
            {
                'identifier': node,
                'wikidata_label': data.get('wikidata_label'),
                'wikidata_description': data.get('wikidata_desc'),
                'wikipedia_id': int(data.get('wikipedia_id')) if data.get('wikipedia_id') else None,
                'wikipedia_title': data.get('wikipedia_title'),
                'category': data.get('category', None)
            }
            for node, data in self._G.nodes(data=True) if data.get('is_root', False)
        ]
        self._root_entities = pd.DataFrame(nodes_data, columns=[
            'identifier', 'wikidata_label', 'wikidata_description', 'wikipedia_id', 'wikipedia_title', 'category'
        ]).set_index('identifier')
        logger.debug(f"Root entities: {self._root_entities.shape[0]} initialized.")
        del nodes_data

        nodes_data = [
            {
                'identifier': node,
                'wikidata_label': data.get('wikidata_label'),
                'wikidata_description': data.get('wikidata_desc'),
                'wikipedia_id': int(data.get('wikipedia_id')) if data.get('wikipedia_id') else None,
                'wikipedia_title': data.get('wikipedia_title')
            }
            for node, data in self._G.nodes(data=True)
        ]
        self._entities = pd.DataFrame(nodes_data, columns=[
            'identifier', 'wikidata_label', 'wikidata_description', 'wikipedia_id', 'wikipedia_title'
        ]).set_index('identifier')
        logger.debug(f"Entities: {self._entities.shape[0]} initialized.")

        del nodes_data

        logger.debug("Initializing triples...")
        edges_data = []
        ground_truths_data = []
        predicates_data = dict()

        for u, v, data in self._G.edges(data=True):
            predicate_id = data['predicate']
            edges_data.append({'subject': u, 'predicate': predicate_id, 'object': v})

            if predicate_id not in predicates_data:
                predicates_data[predicate_id] = (data.get('predicate_label'), data.get('predicate_desc'))

            if 'summary_for' in data:
                ground_truths_data.append({
                    'identifier': data['summary_for'],
                    'subject': u,
                    'predicate': predicate_id,
                    'object': v
                })
        predicate_flat = [
            {
                'identifier': k,
                'predicate_label': v[0],
                'predicate_desc': v[1]
            } for k, v in predicates_data.items()
        ]
        self._predicates = pd.DataFrame(
            predicate_flat,
            columns=['identifier', 'predicate_label', 'predicate_desc']
        ).set_index('identifier')
        del predicate_flat, predicates_data

        self._triples = pd.DataFrame(edges_data, columns=['subject', 'predicate', 'object'])
        del edges_data

        self._ground_truths = pd.DataFrame(
            ground_truths_data,
            columns=['identifier', 'subject', 'predicate', 'object']
        ).set_index('identifier')
        del ground_truths_data

        logger.debug(f"Triples: {self._triples.shape[0]} initialized.")

    def root_entities(self) -> pd.DataFrame:
        return super().root_entities()

    def entities(self) -> pd.DataFrame:
        return super().entities()

    def triples(self) -> pd.DataFrame:
        return super().triples()

    def predicates(self) -> pd.DataFrame:
        return super().predicates()

    def fetch_entity(self, entity: [str, pd.Series]) -> pd.Series:
        return super().fetch_entity(entity)

    def fetch_root_entity(self, entity: [str, pd.Series]) -> pd.Series:
        return super().fetch_root_entity(entity)

    def fetch_predicate(self, predicate: [str, pd.Series]) -> pd.Series:
        return super().fetch_predicate(predicate)

    def fetch_triple(self, triple: Union[Tuple[str, str, str], pd.Series]) -> pd.Series:
        return super().fetch_triple(triple)

    def neighbors(self, entity: [str, pd.Series]) -> pd.DataFrame:
        return super().neighbors(entity)

    def export_as_csv(self, path: str):
        wikes_csv_exporter.export(
            path,
            self._dataset_name.value,
            self._G,
            self._entities,
            self._root_entities,
            self._triples,
            self._predicates,
            self._ground_truths
        )
