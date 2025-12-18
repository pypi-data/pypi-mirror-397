import json
import re
from pathlib import Path
from loguru import logger

from .loader import BaseLoader


CSL_MAPPING = {
    "title": "title",
    "id": "id",
    "abstract": "abstract",
    "author": "authors",
}

doi_regex = re.compile(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)


def is_doi(s: str) -> bool:
    return bool(doi_regex.match(s))


class SnowballLoader(BaseLoader):

    def load(self, path: Path):
        logger.debug(f"Loading Snowball JSON from {path}.")
        data = json.load(open(path))
        items = []
        for item in data["nodes"]:
            csl = {}
            for key in CSL_MAPPING:
                csl[key] = item[CSL_MAPPING[key]]
            identifiers = {}
            if is_doi(item["id"]):
                identifiers["doi"] = [item["id"]]
            items.append(
                {
                    "id": item["id"].lower(),
                    "identifiers": identifiers,
                    "csl": csl,
                    "snowball": item,
                }
            )
        return items, data["links"]
