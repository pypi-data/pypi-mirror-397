import networkx as nx
import dpath

from pathlib import Path
from loguru import logger

from .loaders.loader import BaseLoader
from .matchers.matcher import BaseMatcher
from .formatters.formatter import BaseFormatter
from .processors.processor import BaseProcessor


class CitationGraph:

    def __init__(self, path: str, loader: BaseLoader):
        self.path = Path(path)
        self.loader = loader
        if not self.path.exists():
            raise FileNotFoundError(
                f"'{path}' does not exist! Please check if you've provided the correct path."
            )
        items, links = loader.load(self.path)
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from([(item["id"], item) for item in items])

        missing = []
        for link in links:
            if link["source"] not in self.graph or link["target"] not in self.graph:
                missing.append((link["source"], link["target"]))
                continue
            self.graph.add_edge(link["source"], link["target"])

        logger.success(
            f"Loaded {self.graph.number_of_nodes()} items and {self.graph.number_of_edges()} links from '{self.path}'."
        )

        if len(missing) > 0:
            logger.warning("The following links have item IDs that doesn't exist:")
            for source, target in missing:
                logger.warning(f"  - {source} -> {target}")
            logger.warning("They have been skipped.")

    def merge(
        self,
        path: str,
        loader: BaseLoader,
        # matcher: BaseMatcher | None = None,
        # item_matcher: BaseMatcher | None = None,
        source_matcher: BaseMatcher | None = None,
        target_matcher: BaseMatcher | None = None,
    ):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(
                f"'{path}' does not exist! Please check if you've provided the correct path."
            )
        items, links = loader.load(self.path)

        logger.success(
            f"Loaded {len(items)} items and {len(links)} links from '{self.path}'."
        )

        statistics = {
            "items": {"added": 0, "updated": 0},
            "links": {"added": 0},
        }
        for item in items:
            if item["id"] in self.graph:
                out = dpath.merge(item, self.graph.nodes[item["id"]])
                self.graph.nodes[item["id"]].update(out)
                statistics["items"]["updated"] += 1
            else:
                self.graph.add_nodes_from([(item["id"], dict(item))])
                statistics["items"]["added"] += 1

        unmatched = set()
        if source_matcher is not None:
            matches = source_matcher.match(
                list(set([link["source"] for link in links])),
                [data for _, data in self.graph.nodes.data()],
            )
            for link in links:
                if link["source"] not in matches:
                    unmatched.add((link["source"], link["target"]))
                    continue
                source_id, source_value, cost = matches[link["source"]]
                link["source"] = source_id

        if target_matcher is not None:
            matches = target_matcher.match(
                list(set([link["target"] for link in links])),
                [data for _, data in self.graph.nodes.data()],
            )
            for link in links:
                if link["target"] not in matches:
                    unmatched.add((link["source"], link["target"]))
                    continue
                target_id, target_value, cost = matches[link["target"]]
                link["target"] = target_id

        if len(unmatched) > 0:
            logger.warning(
                "The following links did not have a good match and will be skipped:"
            )
            for source, target in unmatched:
                logger.warning(f" - {source} -> {target}")

        for link in links:
            if (link["source"], link["target"]) in unmatched:
                continue
            if link["source"] not in self.graph.nodes:
                logger.warning(
                    f"Item '{link['source']}' does not exist! Skipping adding edge {link['source']} -> {link['target']}"
                )
                continue
            if link["target"] not in self.graph.nodes:
                logger.error(
                    f"Item '{link['target']}' does not exist! Skipping adding edge {link['source']} -> {link['target']}"
                )
                continue
            self.graph.add_edge(link["source"], link["target"])
            statistics["links"]["added"] += 1

        logger.success(
            f"Added {statistics['items']['added']} items and {statistics['links']['added']} links. Updated {statistics['items']['updated']} existing items."
        )

        return self

    def write(self, path: str, formatter: BaseFormatter):
        formatted = formatter.format(self.graph)
        with open(path, "wb") as f:
            f.write(formatted)
        logger.success(f"Written to {path}.")
        return self

    def run(self, processor: BaseProcessor):
        processor.run(self.graph)
        return self
