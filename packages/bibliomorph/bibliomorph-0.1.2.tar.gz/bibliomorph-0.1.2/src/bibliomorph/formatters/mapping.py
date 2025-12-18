import dpath

from json import dumps
from typing import Any, Callable, Iterable, Mapping
from networkx import DiGraph

from .formatter import BaseFormatter


class MappingJSONFormatter(BaseFormatter):

    items_field: str = "items"
    links_field: str = "links"

    mapping: Mapping[str, Iterable[str] | Callable[[DiGraph, str], Any]] = {}
    defaults: Mapping[str, Any] = {}
    postprocess: Mapping[str, Callable] = {}

    def format(self, graph: DiGraph) -> bytes:
        output = {}
        output[self.items_field] = []
        output[self.links_field] = []
        for item_id, item in graph.nodes.data():
            formatted = {}
            for key, mapping in self.mapping.items():
                if callable(mapping):
                    value = mapping(graph, item_id)
                else:
                    value = self.defaults[key] if key in self.defaults else None
                    for path in mapping:
                        try:
                            retrieved = dpath.get(item, path)
                            if retrieved is not None:
                                value = retrieved
                                break
                        except KeyError:
                            continue

                if key in self.postprocess:
                    value = self.postprocess[key](value, item)

                formatted[key] = value
            output[self.items_field].append(formatted)

        for source, target in graph.edges:
            output[self.links_field].append({"source": source, "target": target})

        return dumps(output, indent=4, ensure_ascii=False).encode("utf-8")
