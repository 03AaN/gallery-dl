# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://hitomi.la/"""

from .common import GalleryExtractor
from .. import text, util
import string


class HitomiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from hitomi.la"""
    category = "hitomi"
    pattern = r"(?:https?://)?hitomi\.la/(?:galleries|reader)/(\d+)"
    test = (
        ("https://hitomi.la/galleries/867789.html", {
            "url": "cb759868d090fe0e2655c3e29ebf146054322b6d",
            "keyword": "52951edb50163180eb669a78aef0bab0522d32b7",
        }),
        ("https://hitomi.la/galleries/1036181.html", {
            # "aa" subdomain for gallery-id ending in 1 (#142)
            "pattern": r"https://aa\.hitomi\.la/",
        }),
        ("https://hitomi.la/reader/867789.html"),
    )

    def __init__(self, match):
        self.gid = text.parse_int(match.group(1))
        url = "https://hitomi.la/galleries/{}.html".format(self.gid)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        pos = page.index('<h1><a href="/reader/')
        extr = text.extract
        title , pos = extr(page, '.html">', '<', pos)
        artist, pos = extr(page, '<h2>', '</h2>', pos)
        group , pos = extr(page, '<td>Group</td><td>', '</td>', pos)
        gtype , pos = extr(page, '<td>Type</td><td>', '</td>', pos)
        lang  , pos = extr(page, '<td>Language</td><td>', '</td>', pos)
        series, pos = extr(page, '<td>Series</td><td>', '</td>', pos)
        chars , pos = extr(page, '<td>Characters</td><td>', '</td>', pos)
        tags  , pos = extr(page, '<td>Tags</td><td>', '</td>', pos)
        date  , pos = extr(page, '<span class="date">', '</span>', pos)
        lang = None if lang == "N/A" else text.remove_html(lang)

        return {
            "gallery_id": self.gid,
            "title": text.unescape(" ".join(title.split())),
            "artist": self._prepare(artist),
            "group": self._prepare(group),
            "type": text.remove_html(gtype).capitalize(),
            "lang": util.language_to_code(lang),
            "language": lang,
            "date": date,
            "series": self._prepare(series),
            "characters": self._prepare(chars),
            "tags": self._prepare(tags),
        }

    def images(self, page):
        # see https://ltn.hitomi.la/common.js
        frontends = 2
        offset = self.gid % frontends if self.gid % 10 != 1 else 0
        subdomain = chr(97 + offset) + "a"
        base = "https://" + subdomain + ".hitomi.la/galleries/"

        return [
            (base + urlpart, None)
            for urlpart in text.extract_iter(
                page, "'//tn.hitomi.la/smalltn/", ".jpg',"
            )
        ]

    @staticmethod
    def _prepare(value):
        if not value or "<ul " not in value:
            return ""
        value = ", ".join(text.extract_iter(
            value, '.html">', '<'))
        return string.capwords(
            text.unescape(value)
        )
