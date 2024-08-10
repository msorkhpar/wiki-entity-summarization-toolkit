from __future__ import annotations

import logging
import os
import pickle
import inspect
import types
from pathlib import Path
from typing import Type, Union, Dict, Tuple, Optional, TypeVar, Callable, List

import networkx as nx
import requests
from tqdm import tqdm

from wikes_toolkit.esbm.esbm_eval import ESBMSummaryEvaluator
from wikes_toolkit.esbm.esbm_graph_components import ESBMBaseGraph
from wikes_toolkit.esbm.esbm_pandas_graph import PandasESBMGraph
from wikes_toolkit.wikes.wikes_eval import WikESSummaryEvaluator
from wikes_toolkit.wikes.wikes_versions import WikESVersions
from wikes_toolkit.esbm.esbm_versions import ESBMVersions

from wikes_toolkit.base.graph_components import BaseESGraph, RootEntity, Triple

from wikes_toolkit.esbm.esbm_graph import ESBMGraph
from wikes_toolkit.wikes.wikes_graph import WikESGraph
from wikes_toolkit.wikes.wikes_pandas_graph import PandasWikESGraph
from wikes_toolkit.base.versions import DatasetName, DatasetVersion
from wikes_toolkit.wikes.wikies_graph_components import WikESBaseGraph

logger = logging.getLogger(__name__)


class WikESToolkit:
    T = TypeVar('T', bound=BaseESGraph)
    WikES_datasets = WikESVersions.available_versions()
    ESBM_datasets = ESBMVersions.available_versions()

    def __init__(self, save_path: Union[str, Path] = None, log_level: int = logging.DEBUG):
        if save_path is None:
            save_path = Path.home() / '.wikes_data'
        self.save_path = Path(save_path)
        self.save_path.mkdir(parents=True, exist_ok=True)
        if not self.save_path.exists():
            raise Exception("WikES could not initialize the save path...")
        logging.basicConfig(level=log_level)

    def __download_graph(self, dataset: DatasetName) -> None:
        url = dataset.get_dataset_url()
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(
                f"Failed to download dataset [{dataset}] from {url}. HTTP Status Code: {response.status_code}")

        total_size = int(response.headers.get('content-length', 0))
        dataset_path = self.save_path / dataset.get_version() / f"{dataset.value}.pkl"
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dataset_path, 'wb') as file, tqdm(
                desc=str(dataset_path),
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(1024):
                file.write(data)
                bar.update(len(data))

    def __apply_predictions(
            G: BaseESGraph,
            predictions: Dict[
                Union[RootEntity, str],
                List[Union[Triple, Tuple[str, str, str]]]
            ]
    ):
        if predictions is None:
            return
        elif isinstance(predictions, dict):
            G.clear_summaries()
            for root_entity, triples in predictions.items():
                G.mark_triples_as_summaries(root_entity, triples)
        else:
            raise ValueError("Predictions should be a dictionary of root entities and their predicted triples.")

    def load_graph(
            self,
            implementation_class: Type[T],
            dataset: DatasetName,
            root_entity_formatter: Optional[callable] = None,
            entity_formatter: Optional[Callable] = None,
            predicate_formatter: Optional[Callable] = None,
            triple_formatter: Optional[Callable] = None) -> T:
        if not issubclass(implementation_class, BaseESGraph):
            raise ValueError("Please use a valid WikESGraph class.")

        if isinstance(dataset, self.WikES_datasets) and not issubclass(implementation_class, WikESBaseGraph):
            raise ValueError("To use a WikES dataset, use WikESGraph or PandasWikESGraph.")
        if isinstance(dataset, self.ESBM_datasets) and not issubclass(implementation_class, ESBMBaseGraph):
            raise ValueError("To use an ESBM dataset you need to use the ESBMGraph class.")

        if issubclass(implementation_class, WikESGraph):
            if not isinstance(dataset, DatasetName):
                raise ValueError("Please use a valid dataset version class.")
            if root_entity_formatter is not None and not isinstance(root_entity_formatter, types.FunctionType):
                raise ValueError("Please provide a valid root entity formatter functon.")
            if entity_formatter is not None and not isinstance(entity_formatter, types.FunctionType):
                raise ValueError("Please provide a valid entity formatter functon.")
            if predicate_formatter is not None and not isinstance(predicate_formatter, types.FunctionType):
                raise ValueError("Please provide a valid predicate formatter functon.")
            if triple_formatter is not None and not isinstance(triple_formatter, types.FunctionType):
                raise ValueError("Please provide a valid triple formatter functon.")
        elif issubclass(implementation_class, PandasWikESGraph) and (
                entity_formatter or predicate_formatter or triple_formatter):
            logger.warning("PandasWikESGraph does not support custom formatters. Ignoring formater functions.")

        dataset_path = self.save_path / dataset.get_version() / f"{dataset.value}.pkl"
        if not dataset_path.exists():
            self.__download_graph(dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset [{dataset}] could not be downloaded.")

        with open(dataset_path, 'rb') as f:
            G: nx.MultiDiGraph = pickle.load(f)
        if not G:
            raise ValueError("Could not load the graph from the dataset file.")
        else:
            logger.debug(f"Graph [{dataset}] file loaded successfully.")

        if issubclass(implementation_class, WikESGraph):
            return WikESGraph(
                G,
                dataset,
                root_entity_formatter, entity_formatter, predicate_formatter, triple_formatter
            )
        elif issubclass(implementation_class, PandasWikESGraph):
            return PandasWikESGraph(G, dataset)
        elif issubclass(implementation_class, ESBMGraph):
            return ESBMGraph(G, dataset, root_entity_formatter, entity_formatter, predicate_formatter, triple_formatter)
        elif issubclass(implementation_class, PandasESBMGraph):
            return PandasESBMGraph(G, dataset)
        else:
            raise ValueError("Please provide a valid Graph class.")

    def load_all_graphs(self,
                        implementation_class: Type[T],
                        dataset_version: Type[DatasetVersion],
                        entity_formatter: Optional[callable] = None,
                        predicate_formatter: Optional[callable] = None,
                        triple_formatter: Optional[callable] = None
                        ) -> Tuple[DatasetName, T]:
        if not issubclass(dataset_version, DatasetVersion):
            raise ValueError("Please use one of the provided version classes.")

        for name, obj in inspect.getmembers(dataset_version):
            if inspect.isclass(obj) and issubclass(obj, DatasetName):
                for enum_member in obj:
                    yield enum_member, self.load_graph(
                        implementation_class, enum_member, entity_formatter,
                        predicate_formatter, triple_formatter
                    )
