import re

from cleantext import clean

from bibliomorph.formatters.mapping import MappingJSONFormatter
from bibliomorph.graph import CitationGraph
from bibliomorph.loaders.snowball import SnowballLoader
from bibliomorph.loaders.bibtex import BibTexLoader
from bibliomorph.loaders.excel_links import ExcelLinksLoader
from bibliomorph.matchers.text import TextSimilarityMatcher
from bibliomorph.processors.openalex import OpenAlexEnricher
from bibliomorph.utils.string import count_strings
from bibliomorph.utils.formatting import venue_abbreviation


def format_source(strings: list[str]) -> list[str]:
    titles = []
    for string in strings:
        found = re.findall(r"\d\d\d\d\s*-\s*(.+)\.pdf", string)
        if len(found) > 0:
            titles.append(clean(found[0]).strip())
    return titles


def format_target(strings: list[str]) -> list[str]:
    titles = []
    for string in strings:
        found = re.findall(r"\d\d\d\d\s*\.\s*([^.]+)\.", string)
        if len(found) > 0:
            titles.append(clean(found[0]).strip())
    counts = count_strings(titles)
    title = counts[0][0]
    return [title] * len(strings)


def format_venue(venue, item):
    if "csl" not in item:
        print(item)
    if "snowball" in item and item["snowball"]["venue"] is not None:
        return venue_abbreviation(str(venue))
    elif "type" in item["csl"] and item["csl"]["type"] == "paper-conference":
        return venue_abbreviation(str(venue))
    return None


graph = (
    CitationGraph(
        path="snowball-data.json",
        loader=SnowballLoader(),
    )
    .merge(
        path="additional-bibtex.bib",
        loader=BibTexLoader(),
    )
    .merge(
        path="excel-citation-list.xlsx",
        loader=ExcelLinksLoader(
            source="Paper",  # Source column name
            target="Reference",  # Target column name
            source_formatter=format_source,
            target_formatter=format_target,
            skip_sheets=["Info"],
        ),
        source_matcher=TextSimilarityMatcher(
            threshold=18,
            domain_id=lambda x: x,
            domain_value=lambda x: x,
            range_id=lambda node: node["id"],
            range_value=lambda node: clean(node["csl"]["title"]),
        ),
        target_matcher=TextSimilarityMatcher(
            threshold=37,
            domain_id=lambda x: x,
            domain_value=lambda x: x,
            range_id=lambda node: node["id"],
            range_value=lambda node: clean(node["csl"]["title"]),
        ),
    )
    .run(processor=OpenAlexEnricher())
    .write(
        path="output.json",
        formatter=MappingJSONFormatter(
            items_field="nodes",
            links_field="links",
            mapping={
                "id": ["id"],
                "domain": ["snowball/domain"],
                "title": ["snowball/title", "csl/title"],
                "abstract": ["snowball/abstract", "csl/abstract"],
                "authors": ["snowball/authors", "csl/author"],
                "year": ["snowball/year", "csl/issued/year"],
                "venue": [
                    "snowball/venue",
                    "csl/collection_title",
                    "csl/container_title",
                ],
                "framing": ["snowball/framing"],
                "codes": ["snowball/codes"],
                "globalCitations": [
                    "snowball/globalCitations",
                    "csl/is-referenced-by-count",
                    "openalex/cited_by_count",
                ],
                "localCitations": lambda graph, item_id: len(graph.in_edges(item_id)),
                "seed": ["snowball/seed"],
            },
            defaults={
                "id": "",
                "domain": "",
                "title": "",
                "abstract": "",
                "authors": [],
                "year": -1,
                "localCitations": -1,
                "seed": False,
            },
            postprocess={
                "title": lambda title, _: str(title),
                "venue": format_venue,
            },
        ),
    )
)
