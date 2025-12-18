from loguru import logger
from networkx import DiGraph
from crossref.restful import Works

from .processor import BaseProcessor


class CrossRefEnricher(BaseProcessor):

    def run(self, graph: DiGraph):
        for item_id, item in graph.nodes.data():
            if "identifiers" not in item:
                continue
            if "doi" not in item["identifiers"]:
                continue
            doi = item["identifiers"]["doi"]
            print(doi)
        return
