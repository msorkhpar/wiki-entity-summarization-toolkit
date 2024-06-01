from __future__ import annotations

import os
import pickle
import inspect
from pathlib import Path
from typing import Type, Union, Dict, List, Tuple

import networkx as nx
import requests
from tqdm import tqdm

from .versions import DatasetName, V1, DatasetVersion
from .graph import WikESGraph, RootEntity, Triple


class WikESToolkit:
    def __init__(self, save_path: Union[str, Path] = None):
        if save_path is None:
            save_path = Path.home() / '.wikes_data'
        self.save_path = Path(save_path)
        self.save_path.mkdir(parents=True, exist_ok=True)
        if not self.save_path.exists():
            raise Exception("WikES could not initialize the save path...")

    def __download_graph(self, dataset: DatasetName) -> None:
        url = dataset.get_dataset_url()
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download dataset [{dataset}] from {url}. HTTP Status Code: {response.status_code}")

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

    def load_graph(self, dataset: DatasetName) -> WikESGraph:
        if not isinstance(dataset, DatasetName):
            raise ValueError("Please use a valid dataset version class.")

        dataset_path = self.save_path / f"{dataset.value}.pkl"
        if not dataset_path.exists():
            self.__download_graph(dataset)

        with open(dataset_path, 'rb') as f:
            G: nx.MultiDiGraph = pickle.load(f)
        return WikESGraph(G)

    def load_all_graphs(self, dataset_version: Type[DatasetVersion]) -> Dict[DatasetName, WikESGraph]:
        if not issubclass(dataset_version, DatasetVersion):
            raise ValueError("Please use one of the provided version classes.")

        datasets = {}
        for name, obj in inspect.getmembers(dataset_version):
            if inspect.isclass(obj) and issubclass(obj, DatasetName):
                for enum_member in obj:
                    datasets[enum_member] = self.load_graph(enum_member)
        return datasets

    @staticmethod
    def F1_score(
            G: WikESGraph, predictions: Dict[Union[RootEntity, str], List[Union[Triple, Tuple[str, str, str]]]] = None
    ):
        raise NotImplementedError

    @staticmethod
    def MAP_score(
            G: WikESGraph, predictions: Dict[Union[RootEntity, str], List[Union[Triple, Tuple[str, str, str]]]] = None
    ):
        raise NotImplementedError
