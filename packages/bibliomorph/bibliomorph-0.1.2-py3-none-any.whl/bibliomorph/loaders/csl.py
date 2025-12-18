import json

from pathlib import Path
from citeproc.source.json import CiteProcJSON

from .loader import BaseLoader


class CSLLoader(BaseLoader):

    def load(self, path: Path):
        try:
            data = json.load(open(path))
            bibliography = CiteProcJSON(data)
        except Exception as e:
            raise e

        raise NotImplementedError("CSLLoader have not been fully implemented yet!")
        return bibliography, []
