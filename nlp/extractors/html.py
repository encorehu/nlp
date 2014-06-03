# -*- coding: utf-8 -*-

import re

from base import BaseRegexExtractor

class LinkExtractor(BaseRegexExtractor):
    regex = '<\s*[Aa]{1}\s+[^>]*?[Hh][Rr][Ee][Ff]\s*=\s*[\"\']?([/:_;=\w\&\?\%\+\-\.\(\)]+)[\"\']?\s*.*?>(.*?)</[Aa]{1}>'

    def extract(self, html):
        r=super(LinkExtractor, self).extract(html)
        return r
