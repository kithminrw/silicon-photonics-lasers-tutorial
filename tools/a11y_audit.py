"""Static accessibility audit of the built site (_site): images without alt text, buttons and links without an
accessible name, form inputs without a label, 3D viewers without alt, duplicate ids, and skipped heading levels.

Run from the repository root after a Jekyll build:  python3 -I tools/a11y_audit.py [_site]
It prints a summary per check and the first few offending pages. Static checks only: colour contrast and
keyboard behaviour still need a person (or a browser-based tool).
"""
import collections
import pathlib
import sys
from html.parser import HTMLParser


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.issues = collections.defaultdict(list)
        self.stack = []            # open buttons/links collecting text: [tag, attrs, text]
        self.ids = collections.Counter()
        self.labels_for = set()
        self.inputs = []
        self.last_h = 0
        self.in_label = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids[a["id"]] += 1
        if tag == "img" and "alt" not in a: self.issues["img without alt"].append(a.get("src", "?"))
        if tag == "model-viewer" and not a.get("alt"): self.issues["3D viewer without alt"].append(a.get("src", "?"))
        if tag in ("button", "a"): self.stack.append([tag, a, ""])
        if tag == "label":
            self.in_label += 1
            if "for" in a: self.labels_for.add(a["for"])
        if tag in ("input", "select", "textarea") and a.get("type") not in ("hidden",):
            self.inputs.append((a, self.in_label > 0))
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            lvl = int(tag[1])
            if self.last_h and lvl > self.last_h + 1: self.issues["heading level skipped"].append(f"h{self.last_h} -> h{lvl}")
            self.last_h = lvl

    def handle_endtag(self, tag):
        if tag == "label": self.in_label = max(0, self.in_label - 1)
        if tag in ("button", "a") and self.stack and self.stack[-1][0] == tag:
            t, a, text = self.stack.pop()
            name = text.strip() or a.get("aria-label") or a.get("title") or a.get("aria-labelledby")
            if not name:
                if t == "button": self.issues["button without a name"].append(a.get("class", "?"))
                elif "href" in a: self.issues["link without a name"].append(a.get("href", "?"))
            if self.stack: self.stack[-1][2] += " " + text

    def handle_data(self, data):
        if self.stack: self.stack[-1][2] += data

    def finish(self):
        for i, n in self.ids.items():
            if n > 1: self.issues["duplicate id"].append(i)
        for a, inside in self.inputs:
            if not (inside or a.get("aria-label") or a.get("aria-labelledby") or a.get("id") in self.labels_for or a.get("title")):
                self.issues["input without a label"].append(a.get("data-k") or a.get("name") or a.get("type", "?"))


def main(root="_site"):
    total = collections.Counter(); where = collections.defaultdict(list)
    pages = sorted(pathlib.Path(root).rglob("*.html"))
    for p in pages:
        au = Audit(); au.feed(p.read_text(encoding="utf-8", errors="replace")); au.finish()
        for k, v in au.issues.items():
            total[k] += len(v); where[k].append((str(p.relative_to(root)), v[:3]))
    print(f"{len(pages)} pages checked")
    for k in ("img without alt", "3D viewer without alt", "button without a name", "link without a name", "input without a label",
              "duplicate id", "heading level skipped"):
        print(f"  {k:24s} {total[k]:5d}")
        for page, ex in where[k][:4]:
            print(f"      {page}: {ex}")


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
