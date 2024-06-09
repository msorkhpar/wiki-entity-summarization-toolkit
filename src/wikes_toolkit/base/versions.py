from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum


@dataclass
class DatasetVersion:
    base_url: str


class DatasetName(Enum):

    @abstractmethod
    def get_dataset_url(self) -> str:
        pass
