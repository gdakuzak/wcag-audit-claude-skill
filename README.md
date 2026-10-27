# WCAG 2.2 Audit — Claude Cowork Skill

**English** · [Português](./README.pt-BR.md)

A Claude Cowork plugin that performs comprehensive WCAG 2.2 Level AA accessibility audits on web pages and HTML files, with programmatic contrast verification and professional audit reports.

## Results

Blind evaluation of v1.1.0 on 12 test pages (67 known failures, 22 should-pass items). Each page was audited from a copy with all comments removed and a neutral title, by agents that never saw the ground truth, and graded strictly (a known failure counts only as a *fail* finding under the right criterion naming the element).

| Metric | Result |
|--------|--------|
| Detection rate | **98.5%** (66/67 known failures) |
| Missed | **1** (links distinguished only by color, page 09) |
| False positives | **2** (missing landmarks filed under 1.3.1) · should-pass items: 22/22 correct |
| Criteria rated | **55/55** on every page |
| Extra genuine issues | **41** real failures the ground truth didn't document (reviewed manually) |

The blind run also showed that 8 of the 59 failures documented by v1.0 were wrong in the ground truth itself (e.g. `#757575` on white is 4.61:1, not 4.48:1). v1.0 had "detected" all of them by reading the answers in the page comments. They are now should-pass items.

[View the full evaluation report →](https://gdakuzak.github.io/wcag-audit-claude-skill/eval-report.html)

## Install

### Claude Code

```
/plugin marketplace add gdakuzak/wcag-audit-claude-skill
/plugin install wcag-audit@wcag-audit
```

Or locally from a clone: `/plugin marketplace add ./wcag-audit-claude-skill`.

Skill only (no plugin): `cp -r plugin/skills/wcag-audit ~/.claude/skills/`.

### Claude Desktop

Download [`wcag-audit.plugin`](./wcag-audit.plugin) and open it in Claude Desktop. The plugin will appear as an installable card — click Accept to install.

Alternatively, copy the `plugin/` directory into your Claude skills folder.

## Usage

Ask Claude to audit any web page or HTML file. Trigger phrases include:

- "Is this page WCAG compliant?"
- "Run an accessibility audit on this URL"
- "Check the contrast ratios on this page"
- "Does this HTML meet WCAG 2.2?"

The skill accepts URLs, local HTML files, or uploaded files as input.

## How It Works

The audit follows a 5-phase methodology:

1. **Source Acquisition** — Fetch the page via URL or read from the filesystem
2. **CSS Color Extraction** — Parse every color declaration from stylesheets
3. **Programmatic Contrast Verification** — Compute contrast ratios using the WCAG relative luminance formula via `contrast_checker.py`
4. **Manual Criteria Review** — Evaluate all 55 WCAG 2.2 A + AA success criteria through code analysis
5. **Report Generation** — Produce a professional styled HTML audit report

## Repository Structure

```
├── wcag-audit.plugin          # Installable plugin file
├── plugin/                    # Plugin source files
│   ├── .claude-plugin/        #   Plugin manifest
│   └── skills/wcag-audit/     #   Skill, scripts, and WCAG criteria reference
├── evals/                     # Evaluation suite
│   ├── test-pages/            #   10 test pages with ground truth (HTML comments)
│   ├── reports/               #   Audit reports generated during evaluation
│   ├── grade_all.py           #   Automated grading script
│   └── grading_results.json   #   Structured results
├── docs/                      # GitHub Pages
│   ├── eval-report.html       #   Evaluation dashboard (EN)
│   └── eval-report.pt-BR.html #   Evaluation dashboard (pt-BR)
└── original-work/             # Original OKLIS-2026 audit that inspired this skill
    ├── index.html             #   WCAG-fixed presentation
    └── audit-report.html      #   Audit report for the fixed version
```

## Evaluation Test Pages

| # | Focus Area | Known Failures | Detected | Should-pass OK | Extra genuine |
|---|-----------|---------------|----------|----------------|---------------|
| 01 | Subtle contrast (borderline ratios, rgba, non-text) | 3 | 3 | 4/4 | 0 |
| 02 | Semantic structure (headings, landmarks, lang) | 8 | 8 | 1/1 | 5 |
| 03 | Keyboard & focus (traps, visibility, tabindex) | 7 | 7 | 1/1 | 11 |
| 04 | WCAG 2.2 targets & focus obscured | 4 | 4 | 2/2 | 5 |
| 05 | Form accessibility (labels, fieldsets, ARIA) | 7 | 7 | 0/0 | 4 |
| 06 | Media (alt text, captions, transcripts) | 7 | 7 | 1/1 | 3 |
| 07 | Fully compliant (false positive test) | 0 | 0 | 5/5 | 3 |
| 08 | Dynamic content (widgets, ARIA states, live regions) | 7 | 7 | 0/0 | 4 |
| 09 | Color-only information (links, status, errors) | 4 | 3 | 3/3 | 3 |
| 10 | Responsive & reflow (viewport, text resize, spacing) | 4 | 4 | 3/3 | 0 |
| 11 | New in WCAG 2.2 (dragging, redundant entry, accessible auth) | 7 | 7 | 1/1 | 2 |
| 12 | Operable & understandable (timing, bypass, title, shortcuts, errors) | 9 | 9 | 1/1 | 1 |

Run it yourself: `python3 evals/grade_all.py` then `python3 evals/build_report.py`.

## Limitations

This skill performs static code analysis. It cannot test dynamic interactions in a live browser (e.g., actual keyboard navigation, screen reader behavior, or JavaScript-driven state changes). For full compliance verification, combine this audit with manual testing using assistive technologies.

## License

MIT
