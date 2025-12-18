from abc import ABC, abstractmethod
from networkx import DiGraph


class BaseFormatter(ABC):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def format(self, graph: DiGraph) -> bytes:
        raise NotImplementedError(
            "Please use a concrete implementation of BaseFormatter to format the CitationGraph."
        )
