from __future__ import annotations

import os
import pickle

import networkx as nx
import requests
from tqdm import tqdm

from .versions import DatasetName
from .graph import WikESGraph, RootEntity, Triple


class WikESToolkit:
    def __init__(self, save_path=None):
        if save_path is None:
            save_path = os.path.join(os.path.expanduser('~'), '.wikes_data')
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        if not os.path.exists(self.save_path):
            raise Exception("WikES could not initialize the save path...")

    def __download_graph(self, dataset: DatasetName) -> None:
        response = requests.get(dataset.get_dataset_url(), stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download dataset. HTTP Status Code: {response.status_code}")

        total_size = int(response.headers.get('content-length', 0))

        with open(dataset.get_dataset_path(self.save_path), 'wb') as file, tqdm(
                desc=dataset.get_dataset_path(self.save_path),
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
            raise ValueError("Please use dataset version class")
        dataset_path = dataset.get_dataset_path(self.save_path)
        if not os.path.exists(dataset_path):
            self.__download_graph(dataset)

        with open(dataset_path, 'rb') as f:
            G: nx.MultiDiGraph = pickle.load(f)
        return WikESGraph(G)

    @staticmethod
    def F1_score(G: WikESGraph, predications: dict[RootEntity | str, list[Triple | tuple[str, str, str]]]=None):
        raise NotImplemented

    @staticmethod
    def MAP_score(G: WikESGraph, predications: dict[RootEntity | str, list[Triple | tuple[str, str, str]]]=None):
        raise NotImplemented

