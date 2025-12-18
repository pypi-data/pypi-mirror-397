from abc import ABC, abstractmethod
from networkx import DiGraph


class BaseProcessor(ABC):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def run(self, graph: DiGraph):
        raise NotImplementedError(
            "Please use a concrete implementation of BaseProcessor to process the CitationGraph."
        )
