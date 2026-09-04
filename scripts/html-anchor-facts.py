"""Extract actual HTML attributes, not similarly named data-* attributes."""
import json
import sys
from html.parser import HTMLParser


class Facts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = {}
        self.language = None
        self.math = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "math":
            self.math += 1
        if "id" in attrs:
            value = attrs["id"]
            self.ids[value] = self.ids.get(value, 0) + 1

    handle_startendtag = handle_starttag


parser = Facts()
parser.feed(sys.stdin.buffer.read().decode("utf-8"))
parser.close()
print(json.dumps({"language": parser.language, "anchor_counts": parser.ids,
                  "mathml_elements": parser.math}, ensure_ascii=False))
