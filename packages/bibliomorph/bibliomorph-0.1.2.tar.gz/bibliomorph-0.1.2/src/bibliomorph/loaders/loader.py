from abc import ABC, abstractmethod
from pathlib import Path


class BaseLoader(ABC):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def load(self, path: Path):
        raise NotImplementedError(
            "Please use a concrete implementation of BaseLoader to load a file."
        )
