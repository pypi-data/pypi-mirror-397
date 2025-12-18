from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Mapping


class BaseMatcher(ABC):

    domain_id: Callable[[Any], str]
    domain_value: Callable[[Any], str]
    range_id: Callable[[Any], str]
    range_value: Callable[[Any], str]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def match(
        self,
        domains: Iterable[Any],
        ranges: Iterable[Any],
    ) -> Mapping[str, tuple[str, str, float]]:
        raise NotImplementedError(
            "Please use a concrete implementation of BaseMatcher to perform matching."
        )
