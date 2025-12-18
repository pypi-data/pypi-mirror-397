import warnings
from loguru import logger
from pathlib import Path
from citeproc.source.bibtex import BibTeX

from .loader import BaseLoader


class BibTexLoader(BaseLoader):

    def load(self, path: Path):
        logger.debug(f"Loading '{path}' as BibTeX...")
        with warnings.catch_warnings(record=True):
            bibliography = BibTeX(path)

            items = []
            for item in bibliography.values():
                identifier = item["key"]
                identifiers = {}
                if "DOI" in item:
                    identifier = str(item["DOI"])
                    identifiers["doi"] = [str(item["DOI"])]
                elif "ISBN" in item:
                    identifier = str(item["ISBN"])
                    identifiers["isbn"] = str(item["ISBN"]).replace("-", "").split(" ")
                formatted = {
                    "id": identifier.lower(),
                    "identifiers": identifiers,
                    "csl": dict(item),
                }
                formatted["csl"]["type"] = item.type
                items.append(formatted)
        return items, []
