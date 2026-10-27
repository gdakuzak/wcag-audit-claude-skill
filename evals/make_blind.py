#!/usr/bin/env python3
"""
Make blind copies of the test pages for auditing: strips every HTML/CSS/JS comment (where the
ground truth lives), replaces <title> with the page's <h1> text (pages 11-12 keep theirs: their
titles are part of the test) and names files page-NN.html so the topic isn't given away.

usage: python3 evals/make_blind.py <out-dir>
Audit each page-NN.html with the skill, save page-NN-audit-report.html and page-NN-findings.json,
copy them to evals/reports/<page-name>-*, then run grade_all.py.
"""
import glob
import os
import re
import sys

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(here, "test-pages", "*.html"))):
    n = os.path.basename(f)[:2]
    s = open(f).read()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"(?m)^\s*//.*\n", "", s)
    if n not in ("11", "12"):
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else "Home"
        s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, flags=re.S)
    open(os.path.join(out, f"page-{n}.html"), "w").write(s)
    print(os.path.join(out, f"page-{n}.html"))
