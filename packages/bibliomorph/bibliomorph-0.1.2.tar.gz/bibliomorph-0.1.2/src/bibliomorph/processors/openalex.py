from typing import Any, List
from math import floor
from loguru import logger
from networkx import DiGraph
from pyalex import OpenAlexResponseList, Works
from more_itertools import chunked

from .processor import BaseProcessor


class OpenAlexEnricher(BaseProcessor):

    def run(self, graph: DiGraph):
        dois = set()
        isbns = set()
        titles = set()
        skipped = set()

        for item_id, item in graph.nodes.data():
            if "identifiers" not in item:
                continue

            if "doi" in item["identifiers"]:
                doi = item["identifiers"]["doi"]
                for value in doi:
                    dois.add((item_id, str(value)))

            elif "isbn" in item["identifiers"]:
                isbn = item["identifiers"]["isbn"]
                for value in isbn:
                    isbns.add((item_id, str(value)))

            elif "title" in item["csl"]:
                title = item["csl"]["title"]
                titles.add((item_id, str(title)))

            else:
                skipped.add(item_id)

        logger.debug(
            f"Querying OpenAlex for {len(dois)} DOIs with a batch size of 100."
        )
        for batch in chunked(dois, 100):
            query_ids = [item_id for item_id, _ in batch]
            query_dois = [doi for _, doi in batch]
            response = Works().filter_or(doi=query_dois).get()
            if type(response) is tuple:
                data = response[0]
            elif type(response) is OpenAlexResponseList:
                data = response
            else:
                logger.warning(
                    f"The query did not return data correctly. The response is: {response}"
                )
                continue
            for index, work in enumerate(data):
                item_id = query_ids[index]
                graph.nodes[item_id]["openalex"] = work

            logger.debug(f"Updated {len(batch)} items.")


import datetime
from typing import Dict, Any, List, Optional


def openalex_work_to_csl(work: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a single OpenAlex Work (JSON dict) into a CSL-JSON dict.
    https://github.com/citation-style-language/schema
    """
    # --- Type mapping (very simple; extend as needed) ---
    oa_type = work.get("type") or ""
    type_map = {
        "journal-article": "article-journal",
        "book-chapter": "chapter",
        "book": "book",
        "proceedings-article": "paper-conference",
    }
    csl_type = type_map.get(oa_type, "article-journal")

    # --- Title ---
    title = work.get("title")

    # --- Container (journal / venue) ---
    host_venue = work.get("host_venue") or {}
    container_title = host_venue.get("display_name")

    # --- IDs ---
    ids = work.get("ids") or {}
    doi = ids.get("doi")
    url = host_venue.get("url") or work.get("primary_location", {}).get(
        "source", {}
    ).get("homepage_url")

    # --- Authors ---
    def person_from_authorship(a: Dict[str, Any]) -> Dict[str, str]:
        author = a.get("author", {})
        display_name = author.get("display_name") or ""
        # naive split; you may want a smarter name parser
        parts = display_name.split()
        if len(parts) == 1:
            return {"family": parts[0]}
        return {"given": " ".join(parts[:-1]), "family": parts[-1]}

    authorships = work.get("authorships") or []
    author_list: List[Dict[str, str]] = [person_from_authorship(a) for a in authorships]

    # --- Date ---
    # OpenAlex fields: publication_year, publication_date (YYYY-MM-DD)
    year = work.get("publication_year")
    month = None
    day = None

    pub_date = work.get("publication_date")
    if pub_date:
        try:
            dt = datetime.datetime.fromisoformat(pub_date)
            year = dt.year
            month = dt.month
            day = dt.day
        except ValueError:
            pass  # fall back to year only

    issued_parts: List[int] = []
    if year:
        issued_parts.append(year)
    if month:
        issued_parts.append(month)
    if day:
        issued_parts.append(day)

    issued = {"date-parts": [issued_parts]} if issued_parts else None

    # --- Volume, issue, pages (if present) ---
    biblio = work.get("biblio") or {}
    volume = biblio.get("volume")
    issue = biblio.get("issue")
    first_page = biblio.get("first_page")
    last_page = biblio.get("last_page")
    page = None
    if first_page and last_page:
        page = f"{first_page}-{last_page}"
    elif first_page:
        page = first_page

    # --- Build CSL dict ---
    csl: Dict[str, Any] = {
        "type": csl_type,
        "title": title,
        "container-title": container_title,
        "author": author_list or None,
    }

    if issued:
        csl["issued"] = issued
    if doi:
        csl["DOI"] = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    if url:
        csl["URL"] = url
    if volume:
        csl["volume"] = volume
    if issue:
        csl["issue"] = issue
    if page:
        csl["page"] = page

    # remove None values
    return {k: v for k, v in csl.items() if v not in (None, [], "", {})}
