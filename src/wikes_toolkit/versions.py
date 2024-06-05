from __future__ import annotations

import os
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum


@dataclass
class DatasetVersion:
    base_url: str


class DatasetName(Enum):
    def get_dataset_path(self, base_path: str | os.PathLike) -> str:
        return os.path.join(base_path, self.value + ".pkl")

    @abstractmethod
    def get_dataset_url(self) -> str:
        pass


class V1(DatasetVersion):
    base_url = 'https://github.com/msorkhpar/wiki-entity-summarization/releases/download/1.0.4/'

    @staticmethod
    def get_dataset_url(dataset: DatasetName) -> str:
        return V1.base_url + dataset.value + ".pkl"

    class First(DatasetName):
        SMALL_FULL = '1_small_full'
        SMALL_TRAIN = '1_small_train'
        SMALL_VALIDATION = '1_small_val'
        SMALL_TEST = '1_small_test'
        MEDIUM_FULL = '1_medium_full'
        MEDIUM_TRAIN = '1_medium_train'
        MEDIUM_VALIDATION = '1_medium_val'
        MEDIUM_TEST = '1_medium_test'
        LARGE_FULL = '1_large_full'
        LARGE_TRAIN = '1_large_train'
        LARGE_VALIDATION = '1_large_val'
        LARGE_TEST = '1_large_test'

        def get_dataset_url(self):
            return V1.get_dataset_url(self)

    class Second(DatasetName):
        SMALL_FULL = '2_small_full'
        SMALL_TRAIN = '2_small_train'
        SMALL_VALIDATION = '2_small_val'
        SMALL_TEST = '2_small_test'
        MEDIUM_FULL = '2_medium_full'
        MEDIUM_TRAIN = '2_medium_train'
        MEDIUM_VALIDATION = '2_medium_val'
        MEDIUM_TEST = '2_medium_test'
        LARGE_FULL = '2_large_full'
        LARGE_TRAIN = '2_large_train'
        LARGE_VALIDATION = '2_large_val'
        LARGE_TEST = '2_large_test'

        def get_dataset_url(self):
            return V1.get_dataset_url(self)

    class Third(DatasetName):
        SMALL_FULL = '3_small_full'
        SMALL_TRAIN = '3_small_train'
        SMALL_VALIDATION = '3_small_val'
        SMALL_TEST = '3_small_test'
        MEDIUM_FULL = '3_medium_full'
        MEDIUM_TRAIN = '3_medium_train'
        MEDIUM_VALIDATION = '3_medium_val'
        MEDIUM_TEST = '3_medium_test'
        LARGE_FULL = '3_large_full'
        LARGE_TRAIN = '3_large_train'
        LARGE_VALIDATION = '3_large_val'
        LARGE_TEST = '3_large_test'

        def get_dataset_url(self):
            return V1.get_dataset_url(self)

    class Fourth(DatasetName):
        SMALL_FULL = '4_small_full'
        SMALL_TRAIN = '4_small_train'
        SMALL_VALIDATION = '4_small_val'
        SMALL_TEST = '4_small_test'
        MEDIUM_FULL = '4_medium_full'
        MEDIUM_TRAIN = '4_medium_train'
        MEDIUM_VALIDATION = '4_medium_val'
        MEDIUM_TEST = '4_medium_test'
        LARGE_FULL = '4_large_full'
        LARGE_TRAIN = '4_large_train'
        LARGE_VALIDATION = '4_large_val'
        LARGE_TEST = '4_large_test'

        def get_dataset_url(self):
            return V1.get_dataset_url(self)
