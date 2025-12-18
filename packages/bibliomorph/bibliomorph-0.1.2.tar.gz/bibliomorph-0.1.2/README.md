# Bibliomorph

A Python library for building bibliographic data processing pipelines, to merge, enrich, and export citation data from multiple heterogeneous sources.

Currently, Bibliomorph can help with the following:

-   Load bibliographic data from multiple formats ([Snowball](https://github.com/shaunabanana/snowball), BibTeX, Excel (citation links))
-   Use string similarity matching to resolve textual mentions of papers (e.g. formatted citations) to structured paper records in a best-effort manner.
-   Enrich records with external metadata (OpenAlex)
-   Construct a unified citation graph
-   Export the result into a clean, analysis-ready JSON structure

> [!NOTE]
> This library is a work-in-progress. API changes may occur in future versions.

## Overview

Bibliomorph operates around a **citation graph** abstraction:

-   **Items** represent bibliographic items (papers, books, reports, etc.)
-   **Links** represent citation relationships

A typical pipeline consists of:

1. Creating a `CitationGraph` with a data source
2. Merging other sources with optional matching logic
3. Running processors to enrich or transform the graph
4. Define an output format and saving the graph as a JSON file.

This pipeline is fully declarative and composable. Merging data from multiple sources is non-destructive. Each loader will typically add its own field to the item, identified by some string. Then, appropirate data is merged into the "csl" field, in the format of CSL-JSON. During merging, only empty fields are filled, in the order defined by the order of `merge()` operations.

```
item = {
    "id": "10.some/identifer.such.as.doi",  # A unique string used by the library to identify the item, not guaranteed to be a specific format. You may want to use data in the "identifiers" field.
    "identifiers": {  # Identifiers of the item.
        "doi": [...],
        "isbn": [...],
        ...
    },
    "csl": {...}  # CSL-JSON format data
    "ris": {...}  # Other loader-defined fields
    "excel-attributes": {...}  # Other loader-defined fields
    "snowball": {...}  # Other loader-defined fields
}
```

## Usage

### Installation

```bash
pip install bibliomorph
```

### Loading and merging data

The following example combines three data sources:

1. **Snowball JSON**: Produced by the Snowball app and containing curated metadata and citation relationships.
2. **BibTeX/RIS**: Standard reference formats, but may not contain citation data.
3. **Excel citation list**: An Excel spreadsheet encoding citer/cited relations using columns. The column content can be any identifying info (DOIs, filenames, titles or formatted references), as you can supply your own method to match them to actual records.

```python
from bibliomorph.graph import CitationGraph
from bibliomorph.loaders.snowball import SnowballLoader
from bibliomorph.loaders.bibtex import BibTexLoader
from bibliomorph.loaders.excel_links import ExcelLinksLoader

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
        loader=ExcelLinksLoader(...),
        ... # See below
    )
)
```

The Excel loader accepts custom formatter functions to extract identifying information from free-form strings.

When merging the Excel data, the pipeline supplies basic similarity-based text matching (`TextSimilarityMatcher`) to match text to existing nodes in the graph.

```python
from bibliomorph.matchers.text import TextSimilarityMatcher
from bibliomorph.utils.string import count_strings

# Extracts titles from filenames like: 2021 - Paper Title.pdf
def format_source(strings: list[str]) -> list[str]:
    titles = []
    for string in strings:
        found = re.findall(r"\d\d\d\d\s*-\s*(.+)\.pdf", string)
        if len(found) > 0:
            titles.append(clean(found[0]).strip())
    return titles

# Extracts the most frequent used form of title from reference strings
def format_target(strings: list[str]) -> list[str]:
    titles = []
    for string in strings:
        found = re.findall(r"\d\d\d\d\s*\.\s*([^.]+)\.", string)
        if len(found) > 0:
            titles.append(clean(found[0]).strip())
    counts = count_strings(titles)
    title = counts[0][0]
    return [title] * len(strings)

graph = (
    CitationGraph(...)
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
)
```

### Processing data

After loading, the data can be processed by one or more processors to transform or enrich them. Currently, `OpenAlexEnricher` can load metadata from [OpenAlex](https://openalex.org) for items with DOIs or ISBNs.

```python
from bibliomorph.processors.openalex import OpenAlexEnricher

graph = (
    CitationGraph(...)
    .run(processor=OpenAlexEnricher())
)
```

### Saving to a specific format

Finally, the `.write()` method writes the data to the specified format. The library supplies a `MappingJSONFormatter`, which allows you to define which values (and priority) to map to a output JSON field:

```python
from bibliomorph.formatters.mapping import MappingJSONFormatter

graph = (
    CitationGraph(...)
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
```

## Acknowledgement

This project builds upon others such as:

-   [`citeproc-py`](https://github.com/citeproc-py/citeproc-py) for BibTeX, RIS, CSL-JSON processing and formatting.
-   [`pandas`](https://github.com/pandas-dev/pandas) and [`openpyxl`](https://foss.heptapod.net/openpyxl/openpyxl) for Excel data processing.
-   [`rapidfuzz`](https://github.com/rapidfuzz/RapidFuzz), [`clean-text`](https://github.com/jfilter/clean-text), and [`scipy`](https://github.com/scipy/scipy) for text similarity matching.
-   [`pyalex`](https://github.com/J535D165/pyalex), [`crossrefapi`](https://github.com/fabiobatalha/crossrefapi) (WIP), and [`more_itertools`](https://github.com/more-itertools/more-itertools) for metadata queries.
-   [`dpath`](https://github.com/dpath-maintainers/dpath-python), [`networkx`](https://github.com/networkx/networkx) for citation graph data structure.
