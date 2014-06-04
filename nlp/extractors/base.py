import re

class BaseExtractor(object):

    def _extract(self, html):
        result =[]
        return result

    def find_between(self, text, s1, s2=None):
        if not s1:
            raise Exception('s1 is None!')

        pos1 = text.find(s1)
        if s2 and pos != -1:
            pos2 = text.find(s2, pos1)
        else:
            pos2 = -1

        if pos2 != -1 and pos2>pos1:
            return text[pos1+len(s1):pos2]
        else:
            return ''

    def extract(self, html):
        return self._extract(html)

class BaseRegexExtractor(object):
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
