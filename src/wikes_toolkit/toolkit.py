from __future__ import annotations

import logging
import pickle
import inspect
import types
from pathlib import Path
from typing import Type, Union, Dict, Tuple, Optional, TypeVar, Callable, Set

import networkx as nx
import requests
from tqdm import tqdm

from wikes_toolkit.oo_graph import WikESGraph
from wikes_toolkit.pandas_graph import PandasWikESGraph
from wikes_toolkit.versions import DatasetName, DatasetVersion
from wikes_toolkit.wikies_graph_components import BaseWikESGraph, RootEntity, Triple

logger = logging.getLogger(__name__)


class WikESToolkit:
    T = TypeVar('T', bound=BaseWikESGraph)

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
        dataset_path = self.save_path / f"{dataset.value}.pkl"

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
            G: BaseWikESGraph,
            predictions: Dict[Union[RootEntity, str], Set[Union[Triple, Tuple[str, str, str]]]]
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
            entity_formatter: Optional[Callable] = None,
            predicate_formatter: Optional[Callable] = None,
            triple_formatter: Optional[Callable] = None) -> T:
        if not issubclass(implementation_class, BaseWikESGraph):
            raise ValueError("Please use a valid WikESGraph class.")

        if issubclass(implementation_class, WikESGraph):
            if not isinstance(dataset, DatasetName):
                raise ValueError("Please use a valid dataset version class.")
            if entity_formatter is not None and not isinstance(entity_formatter, types.FunctionType):
                raise ValueError("Please provide a valid entity formatter functon.")
            if predicate_formatter is not None and not isinstance(predicate_formatter, types.FunctionType):
                raise ValueError("Please provide a valid predicate formatter functon.")
            if triple_formatter is not None and not isinstance(triple_formatter, types.FunctionType):
                raise ValueError("Please provide a valid triple formatter functon.")
        elif issubclass(implementation_class, PandasWikESGraph) and (
                entity_formatter or predicate_formatter or triple_formatter):
            logger.warning("PandasWikESGraph does not support custom formatters. Ignoring formater functions.")

        dataset_path = self.save_path / f"{dataset.value}.pkl"
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
            return WikESGraph(G, entity_formatter, predicate_formatter, triple_formatter)
        elif issubclass(implementation_class, PandasWikESGraph):
            return PandasWikESGraph(G)

    def load_all_graphs(self,
                        implementation_class: Type[T],
                        dataset_version: Type[DatasetVersion],
                        entity_formatter: Optional[callable] = None,
                        predicate_formatter: Optional[callable] = None,
                        triple_formatter: Optional[callable] = None
                        ) -> Dict[DatasetName, T]:
        if not issubclass(dataset_version, DatasetVersion):
            raise ValueError("Please use one of the provided version classes.")

        datasets = {}
        for name, obj in inspect.getmembers(dataset_version):
            if inspect.isclass(obj) and issubclass(obj, DatasetName):
                for enum_member in obj:
                    datasets[enum_member] = self.load_graph(
                        implementation_class, enum_member, entity_formatter,
                        predicate_formatter, triple_formatter
                    )
        return datasets

    @staticmethod
    def F1_score(
            G: BaseWikESGraph,
            predictions: Dict[Union[RootEntity, str], Set[Union[Triple, Tuple[str, str, str]]]] = None
    )-> float:
        WikESToolkit.__apply_predictions(G, predictions)

        n = len(G.predications())
        if n == 0:
            logger.error("No predictions found or provided.")
            return 0
        logger.debug(f"Calculating F1 score for {n} predictions...")

        raise NotImplementedError

    @staticmethod
    def MAP(
            G: BaseWikESGraph,
            predictions: Dict[Union[RootEntity, str], Set[Union[Triple, Tuple[str, str, str]]]] = None
    ) -> float:
        WikESToolkit.__apply_predictions(G, predictions)
        if len(G.predications()) == 0:
            logger.error("No predictions found or provided.")
            return 0

        root_entity_ids = list(G.root_entity_ids())
        n = len(root_entity_ids)
        if n == 0:
            logger.error("No root entities found.")
            return 0

        logger.debug(f"Calculating MAP for {n} predictions...")
        total_avg_prec = 0

        for root_entity_id in G.root_entity_ids():
            logger.debug(f"Calculating MAP for root entity: {root_entity_id}")
            ground_truth_triples: Set[Tuple[str, str, str]] = G.ground_truth_triple_ids(root_entity_id)
            logger.debug(f"Ground truth triples for {root_entity_id}: {ground_truth_triples}")
            if len(ground_truth_triples) == 0:
                logger.debug(f"No ground truth triples for root entity {root_entity_id}")
                continue

            prec_sum = 0
            num_hits = 0

            for i, triple in enumerate(G.predication_for_root(root_entity_id), start=1):
                logger.debug(f"Evaluating prediction {i}: {triple}")
                if triple in ground_truth_triples:
                    num_hits += 1
                    prec_sum += num_hits / i
                    logger.debug(f"Hit found: {triple}, num_hits: {num_hits}, prec_sum: {prec_sum}")

            avg_prec = prec_sum / len(ground_truth_triples) if num_hits > 0 else 0
            logger.debug(f"Average precision for {root_entity_id}: {avg_prec}")
            total_avg_prec += avg_prec

        final_map = total_avg_prec / n
        logger.debug(f"Final MAP: {final_map}")
        return final_map
