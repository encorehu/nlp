import re

class BaseExtractor(object):
    regex = None

    def _extract(self, html, regex=None):
        result =[]
        if regex == None:
            regex = self.regex

        if regex == None:
            return result

        p = re.compile(regex)

        result = p.findall(html)
        return result

    def extract(self, html, regex=None):
        return self._extract(html, regex=regex)
