from re import compile

conference_year = compile(r"\s*'\d\d$")
conference_abbr = compile(r"[A-Z]{2,}")


def venue_abbreviation(venue):
    if type(venue) is not str:
        return None
    venue = conference_year.sub("", venue).replace("&amp;", "").strip()
    if not venue.isupper():
        finds = conference_abbr.findall(venue)
        if len(finds) > 0:
            venue = finds[0].strip()
        else:
            venue = None
    return venue
