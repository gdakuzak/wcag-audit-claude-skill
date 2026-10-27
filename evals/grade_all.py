#!/usr/bin/env python3
"""
Grade the wcag-audit eval runs against the ground truth documented in each test page.

Each run produces, in evals/reports/:
  <page>-audit-report.html   the skill's normal HTML report
  <page>-findings.json       machine-readable results, schema:
    {"criteria": [{"sc": "1.4.3", "status": "pass|fail|warning|na"}, ...],
     "findings": [{"sc": "1.4.3", "status": "fail|warning", "element": "...", "description": "..."}]}

Grading is strict: a known failure counts as detected only if a finding with status "fail",
filed under one of the accepted success criteria, mentions the element (any keyword).
A should-pass item is a false positive if any "fail" finding under its criteria mentions it.
Fail findings that match no ground-truth failure are listed for manual review.

usage: python3 evals/grade_all.py
"""
import json
import os
import re

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.join(EVAL_DIR, "reports")

ALL_SC = (
    "1.1.1 1.2.1 1.2.2 1.2.3 1.2.4 1.2.5 1.3.1 1.3.2 1.3.3 1.3.4 1.3.5 1.4.1 1.4.2 1.4.3 1.4.4 "
    "1.4.5 1.4.10 1.4.11 1.4.12 1.4.13 2.1.1 2.1.2 2.1.4 2.2.1 2.2.2 2.3.1 2.4.1 2.4.2 2.4.3 "
    "2.4.4 2.4.5 2.4.6 2.4.7 2.4.11 2.5.1 2.5.2 2.5.3 2.5.4 2.5.7 2.5.8 3.1.1 3.1.2 3.2.1 3.2.2 "
    "3.2.3 3.2.4 3.2.6 3.3.1 3.3.2 3.3.3 3.3.4 3.3.7 3.3.8 4.1.2 4.1.3"
).split()
assert len(ALL_SC) == 55

# (type, accepted SCs, keywords, description) — "tp" = known failure, "tn" = must not be failed.
# Accepted SCs include the defensible alternatives an expert auditor might file it under.
TESTS = {
    "01-subtle-contrast": [
        ("tn", ["1.4.3"], ["757575", "subtitle"], ".subtitle #757575 on #fff is 4.61:1 (v1.0 ground truth wrongly said 4.48)"),
        ("tp", ["1.4.3"], ["959595", "card-meta", "card meta"], ".card-meta #959595 on #f5f5f5"),
        ("tp", ["1.4.3"], ["74b9ff", "tag"], ".tag #fff on #74b9ff"),
        ("tn", ["1.4.3"], ["overlay", "rgba"], ".overlay-text rgba(255,255,255,.7) on #333 = #c2c2c2, 7.09:1 (v1.0 said ~3.4)"),
        ("tp", ["1.4.11"], ["cccccc", "btn-outline", "outline button", "button border"], ".btn-outline border #ccc"),
        ("tn", ["1.4.3"], ["2d6a4f", "accent-text"], ".accent-text #2d6a4f passes 7.08:1"),
        ("tn", ["1.4.3"], ["e0e0e0", "dark-section"], ".dark-section #e0e0e0 on #1a1a1a passes"),
    ],
    "02-semantic-structure": [
        ("tp", ["1.3.1"], ["fake-h", "heading"], "Headings are styled divs"),
        ("tp", ["1.3.1", "2.4.1"], ["fake-nav", "navigation", "<nav>"], "Navigation built from divs"),
        ("tp", ["1.3.1"], ["table", "<th>", "scope"], "Data table without th/scope"),
        ("tp", ["1.3.1", "3.3.2", "4.1.2"], ["placeholder", "label"], "Form inputs with placeholder-only labels"),
        ("tp", ["1.3.2"], ["reordered", "order"], "CSS order breaks reading sequence"),
        ("tn", ["2.4.6", "2.4.4"], ["click here", "read more", "generic", "link text"], "\"click here\"/\"Read more\" have purpose from the sentence (2.4.4 AA passes)"),
        ("tp", ["3.1.2"], ["french", "lang=\"fr\"", "lang=fr", "fr"], "French quote without lang"),
        ("tp", ["1.3.1"], ["breadcrumb"], "Breadcrumb not in nav"),
        ("tp", ["4.1.2"], ["toggle", "switch"], "Custom toggle without role/state"),
    ],
    "03-keyboard-focus": [
        ("tp", ["2.1.1"], ["card-link", "card", "onclick"], ".card-link div with onclick"),
        ("tn", ["2.1.2"], ["modal", "trap"], "Modal is not a keyboard trap: no JS traps focus, Tab leaves it"),
        ("tp", ["2.4.7"], ["outline: none", "outline:none", "outline none", "outline"], "Global outline:none"),
        ("tp", ["2.4.3"], ["tabindex"], "tabindex=5 on search input"),
        ("tp", ["2.4.7", "2.1.1", "4.1.2"], ["custom-dropdown", "dropdown"], ".custom-dropdown has no focus indicator"),
        ("tp", ["2.4.11"], ["sticky", "header"], "Sticky header obscures focus"),
        ("tp", ["2.1.1", "1.4.13"], ["expand-btn", "mouseover", "hover", "expand"], "Mouse-only expand"),
        ("tp", ["1.4.11", "2.4.7"], ["subtle-focus", "e0e0e0", "focus ring"], "1px #e0e0e0 focus ring"),
    ],
    "04-wcag22-specific": [
        ("tp", ["2.5.8"], ["pagination", "dot"], "8px pagination dots"),
        ("tp", ["2.5.8"], ["icon-action", "icon button", "18"], "18px icon buttons"),
        ("tp", ["2.5.8"], ["star"], "14px star rating"),
        ("tp", ["2.4.11"], ["bottom-bar", "bottom bar", "fixed bar", "fixed"], "Fixed bottom bar obscures focus"),
        ("tn", ["2.5.8"], ["nav-link", "inline link"], "Inline link exempt from target size"),
        ("tn", ["2.5.8"], ["big-btn", "48"], "48px button"),
    ],
    "05-form-accessibility": [
        ("tp", ["1.3.1", "3.3.2", "4.1.2", "2.5.3"], ["email"], "Email input without label"),
        ("tp", ["1.3.1"], ["radio", "fieldset", "legend", "account type"], "Radio group without fieldset"),
        ("tp", ["3.3.2", "1.3.1", "4.1.2"], ["phone", "tel"], "Phone input without label/format"),
        ("tp", ["3.3.1", "1.3.1"], ["error"], "Errors not associated with inputs"),
        ("tp", ["1.3.1", "1.4.1", "3.3.2"], ["required", "asterisk", "required-star"], "Required shown only by color"),
        ("tp", ["4.1.2", "2.1.1"], ["custom-select", "custom select", "dropdown"], "Div-based select without ARIA"),
        ("tp", ["1.4.3"], ["bbbbbb", "placeholder"], "Placeholder #bbb contrast"),
    ],
    "06-media-failures": [
        ("tp", ["1.1.1"], ["hero"], "Meaningful hero with alt=\"\""),
        ("tp", ["1.1.1"], ["product", "no alt", "missing alt"], "Product photo without alt"),
        ("tp", ["1.1.1"], ["infographic", "alt=\"image\"", "non-descriptive", "generic alt"], "alt=\"image\""),
        ("tp", ["1.4.5"], ["text-image", "image of text", "text as image", "heading"], "Image of text heading"),
        ("tp", ["1.1.1", "2.4.4", "4.1.2"], ["icon-link", "icon link", "social"], "Icon link without name"),
        ("tp", ["1.2.1"], ["audio", "podcast", "transcript"], "Audio without transcript"),
        ("tp", ["1.2.2"], ["video", "caption"], "Video without captions"),
        ("tn", ["1.1.1"], ["divider"], "Decorative divider with alt=\"\""),
    ],
    "07-fully-compliant": [
        ("tn", ["1.4.3"], [""], "No text contrast failures"),
        ("tn", ["2.4.7"], [""], "Custom focus styles are visible"),
        ("tn", ["2.5.8"], [""], "44px targets / inline links"),
        ("tn", ["1.1.1"], [""], "Decorative alt and aria-labels are correct"),
        ("tn", ["2.4.1"], [""], "Skip link present"),
    ],
    "08-dynamic-content": [
        ("tp", ["4.1.2"], ["toggle", "switch", "role"], "Toggle without role"),
        ("tp", ["4.1.2"], ["aria-checked", "checked", "state"], "Toggle without aria-checked"),
        ("tp", ["4.1.3"], ["status", "settings saved", "aria-live", "live"], "Status message not announced"),
        ("tp", ["1.3.1", "4.1.2"], ["tab"], "Tabs without tablist/tab/tabpanel"),
        ("tp", ["2.1.1"], ["accordion"], "Accordion not keyboard operable"),
        ("tp", ["4.1.2"], ["accordion", "aria-expanded"], "Accordion without aria-expanded"),
        ("tp", ["1.3.2"], ["step", "order"], "Steps visually reordered"),
    ],
    "09-color-only-info": [
        ("tp", ["1.4.1"], ["link", "underline"], "Links only distinguished by color"),
        ("tp", ["1.4.1", "1.3.1", "3.3.2"], ["required"], "Required only by red color"),
        ("tn", ["1.4.1"], ["status-dot", "status dot", "dot", "status"], "Status dots have text labels (Online/Away/Offline)"),
        ("tn", ["1.4.1"], ["chart", "legend"], "Legend swatches have text labels"),
        ("tp", ["1.4.1", "3.3.1"], ["error", "deadline", "red border"], "Error only by red border"),
        ("tp", ["1.4.3"], ["4caf50", "success"], ".success-text #4caf50"),
        ("tn", ["1.4.1"], ["badge"], "Badges use color and text"),
    ],
    "10-responsive-reflow": [
        ("tn", ["1.4.10"], ["fixed-width-table", "table", "900"], "Data table in overflow-x:auto wrapper (tables are exempt)"),
        ("tp", ["1.4.10", "1.4.12", "1.4.4"], ["code-block", "code", "nowrap"], "nowrap code block clips"),
        ("tn", ["1.4.4"], ["fixed-text", "!important"], "14px !important still scales with browser zoom"),
        ("tp", ["1.4.10", "1.4.4", "1.4.12"], ["hero"], "Fixed-height hero clips"),
        ("tp", ["1.4.12"], ["tight-paragraph", "line-height", "letter-spacing"], "Tight text spacing"),
        ("tp", ["1.4.3"], ["watermark", "e8e8e8"], "Watermark #e8e8e8"),
        ("tn", ["1.4.10"], ["responsive-card", "responsive card"], "Responsive card reflows"),
    ],
    "11-wcag22-new-criteria": [
        ("tp", ["2.5.7"], ["wishlist", "sortable", "reorder"], "Drag-only sortable list"),
        ("tp", ["2.5.7"], ["price-range", "slider", "price"], "Drag-only slider"),
        ("tp", ["3.3.7"], ["billing", "same as shipping", "re-enter", "redundant"], "Billing re-asks shipping address"),
        ("tp", ["3.3.8", "1.3.5"], ["paste", "password", "autocomplete"], "Password blocks paste / password managers"),
        ("tp", ["3.3.8"], ["captcha"], "Transcription CAPTCHA without alternative"),
        ("tp", ["2.1.1"], ["wishlist", "price-range", "slider", "sortable", "reorder"], "Wishlist/slider not keyboard operable"),
        ("tp", ["4.1.2"], ["price-range", "slider", "handle"], "Slider without role/value"),
        ("tn", ["2.5.7"], ["receipt", "drop zone", "dropzone", "upload"], "Drop zone has Browse button"),
    ],
    "12-operable-understandable": [
        ("tp", ["2.4.2"], ["title"], "Empty <title>"),
        ("tp", ["2.4.1"], ["skip", "landmark", "bypass", "menu", "navigation"], "No skip link or landmarks"),
        ("tp", ["2.2.1"], ["timeout", "session", "logout", "settimeout", "2 minutes"], "Hard session timeout"),
        ("tp", ["2.2.2"], ["carousel", "auto-advanc", "promo", "slide"], "Auto-advancing carousel"),
        ("tp", ["2.1.4"], ["shortcut", "keydown", "\"s\"", "'s'"], "Single-character shortcuts"),
        ("tp", ["3.2.2"], ["lang", "language", "select", "onchange"], "Select navigates on change"),
        ("tp", ["1.3.5"], ["autocomplete", "name", "email", "phone"], "Personal-data inputs without autocomplete"),
        ("tp", ["2.5.2"], ["mousedown", "delete", "down-event", "down event"], "Delete on mousedown"),
        ("tp", ["3.3.3"], ["invalid input", "date", "dob", "suggest"], "Error message without suggestion"),
        ("tn", ["2.4.4"], ["annual report", "annual-report"], "Descriptive annual report link"),
    ],
}


def load(page):
    report = os.path.join(REPORTS, f"{page}-audit-report.html")
    findings_path = os.path.join(REPORTS, f"{page}-findings.json")
    html = open(report, errors="ignore").read() if os.path.isfile(report) else ""
    data = None
    if os.path.isfile(findings_path):
        try:
            data = json.load(open(findings_path))
        except json.JSONDecodeError:
            pass
    return html, data


def text_of(f):
    return f"{f.get('element', '')} {f.get('description', '')}".lower()


def grade(page, assertions):
    html, data = load(page)
    findings = (data or {}).get("findings", [])
    fails = [f for f in findings if f.get("status") == "fail"]
    criteria = {c.get("sc") for c in (data or {}).get("criteria", [])}

    rows, matched = [], set()
    for kind, scs, kws, desc in assertions:
        hits = [i for i, f in enumerate(fails) if f.get("sc") in scs and any(k in text_of(f) for k in kws)]
        if kind == "tp":
            matched.update(hits)
        rows.append({"type": kind, "sc": scs[0], "text": desc, "passed": bool(hits) if kind == "tp" else not hits})

    meta = {
        "report_exists": bool(html),
        "findings_json_valid": data is not None,
        "all_55_criteria_rated": set(ALL_SC) <= criteria,
        "contrast_ratios_present": len(re.findall(r"\d+(?:\.\d+)?\s*:\s*1", html)) >= 3,
    }
    extra = [{"sc": f.get("sc"), "element": f.get("element", ""), "description": f.get("description", "")[:200]}
             for i, f in enumerate(fails) if i not in matched]
    return {"assertions": rows, "meta": meta, "unmatched_fail_findings": extra,
            "criteria_rated": len(criteria & set(ALL_SC))}


def main():
    per_page, tp, tp_hit, tn, tn_ok = {}, 0, 0, 0, 0
    for page, assertions in TESTS.items():
        r = grade(page, assertions)
        per_page[page] = r
        p_tp = [a for a in r["assertions"] if a["type"] == "tp"]
        p_tn = [a for a in r["assertions"] if a["type"] == "tn"]
        tp += len(p_tp); tp_hit += sum(a["passed"] for a in p_tp)
        tn += len(p_tn); tn_ok += sum(a["passed"] for a in p_tn)
        ok = all(a["passed"] for a in r["assertions"])
        print(f"{'✅' if ok else '⚠️ '} {page}: {sum(a['passed'] for a in p_tp)}/{len(p_tp)} detected, "
              f"{sum(a['passed'] for a in p_tn)}/{len(p_tn)} should-pass correct, "
              f"{r['criteria_rated']}/55 criteria rated, meta {sum(r['meta'].values())}/{len(r['meta'])}")
        for a in r["assertions"]:
            if not a["passed"]:
                label = "MISSED" if a["type"] == "tp" else "FALSE POSITIVE"
                print(f"     ❌ {label} [SC {a['sc']}] {a['text']}")
        for m, v in r["meta"].items():
            if not v:
                print(f"     ❌ meta: {m}")
        for e in r["unmatched_fail_findings"]:
            print(f"     ?  unmatched fail [SC {e['sc']}] {e['element'][:60]} — {e['description'][:90]}")

    print()
    print(f"Detection: {tp_hit}/{tp} ({tp_hit / tp * 100:.1f}%) · should-pass correct: {tn_ok}/{tn} "
          f"({tn_ok / tn * 100:.1f}%) · unmatched fail findings (review manually): "
          f"{sum(len(r['unmatched_fail_findings']) for r in per_page.values())}")

    out = {
        "skill_version": "1.1.0",
        "test_pages": len(TESTS),
        "known_failures": tp,
        "detected": tp_hit,
        "detection_rate": round(tp_hit / tp * 100, 1),
        "should_pass_items": tn,
        "should_pass_correct": tn_ok,
        "per_page": per_page,
    }
    with open(os.path.join(EVAL_DIR, "grading_results.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Saved {os.path.join(EVAL_DIR, 'grading_results.json')}")


if __name__ == "__main__":
    main()
