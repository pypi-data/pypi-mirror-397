from citeproc.source import Reference as CSLReference


class BibliographyData:
    items: list
    links: list


class Citation:
    id: str
    record: CSLReference
