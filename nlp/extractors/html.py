# -*- coding: utf-8 -*-

import re

from base import BaseExtractor, BaseRegexExtractor
from nlp.utils.html2txt import html2markdown

class LinkExtractor(BaseRegexExtractor):
    regex = '<\s*[Aa]{1}\s+[^>]*?[Hh][Rr][Ee][Ff]\s*=\s*[\"\']?([/:_;=\w\&\?\%\+\-\.\(\)]+)[\"\']?\s*.*?>(.*?)</[Aa]{1}>'

    def extract(self, html):
        r=super(LinkExtractor, self).extract(html)
        return r

class MarkdownExtractor(BaseExtractor):
    errors=[]

    def extract(self, html, baseurl=None):
        return html2markdown(html, baseurl=baseurl)
