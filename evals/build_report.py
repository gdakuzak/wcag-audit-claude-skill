#!/usr/bin/env python3
"""
Build the evaluation dashboard (docs/eval-report.html and docs/eval-report.pt-BR.html)
from evals/grading_results.json and evals/manual_review.json.

manual_review.json classifies each "unmatched fail finding" the grader printed:
  {"<page>": [{"sc": "1.4.11", "element": "<as in findings>", "verdict": "genuine|false_positive",
               "note_en": "...", "note_pt": "..."}]}

usage: python3 evals/build_report.py
"""
import html
import json
import os

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(EVAL_DIR, "..", "docs")
DATE = "2026-10-27"

PAGES = {
    "01-subtle-contrast": ("Subtle contrast", "Contraste sutil",
                           "Borderline ratios, rgba overlays, non-text contrast",
                           "Razões no limite, sobreposições rgba, contraste não textual"),
    "02-semantic-structure": ("Semantic structure", "Estrutura semântica",
                              "Fake headings, div navigation, tables, lang, link text",
                              "Títulos falsos, navegação em div, tabelas, lang, texto de link"),
    "03-keyboard-focus": ("Keyboard & focus", "Teclado e foco",
                          "Keyboard traps, focus visibility, tabindex, sticky header",
                          "Armadilhas de teclado, foco visível, tabindex, cabeçalho fixo"),
    "04-wcag22-specific": ("WCAG 2.2 targets & focus", "Alvos e foco da WCAG 2.2",
                           "Target size (2.5.8), focus not obscured (2.4.11)",
                           "Tamanho de alvo (2.5.8), foco não encoberto (2.4.11)"),
    "05-form-accessibility": ("Forms", "Formulários",
                              "Labels, radio groups, error association, custom select",
                              "Labels, grupos de radio, associação de erros, select customizado"),
    "06-media-failures": ("Media", "Mídia",
                          "Alt text, image of text, captions, transcripts",
                          "Texto alternativo, imagem de texto, legendas, transcrições"),
    "07-fully-compliant": ("Fully compliant", "Totalmente conforme",
                           "False-positive test: dark theme, custom focus, large targets",
                           "Teste de falso positivo: tema escuro, foco customizado, alvos grandes"),
    "08-dynamic-content": ("Dynamic content", "Conteúdo dinâmico",
                           "Widgets, ARIA states, status messages, reordering",
                           "Widgets, estados ARIA, mensagens de status, reordenação"),
    "09-color-only-info": ("Color-only information", "Informação só por cor",
                           "Links, required fields, status, charts, errors",
                           "Links, campos obrigatórios, status, gráficos, erros"),
    "10-responsive-reflow": ("Responsive & reflow", "Responsividade e reflow",
                             "Reflow, text resize, text spacing, fixed layouts",
                             "Reflow, redimensionar texto, espaçamento, layouts fixos"),
    "11-wcag22-new-criteria": ("New in WCAG 2.2", "Novos na WCAG 2.2",
                               "Dragging (2.5.7), redundant entry (3.3.7), accessible auth (3.3.8)",
                               "Arrastar (2.5.7), entrada redundante (3.3.7), autenticação (3.3.8)"),
    "12-operable-understandable": ("Operable & understandable", "Operável e compreensível",
                                   "Timing, bypass, title, shortcuts, on input, autocomplete, errors",
                                   "Tempo, pular blocos, título, atalhos, on input, autocomplete, erros"),
}

T = {
    "en": {
        "lang": "en", "title": "WCAG 2.2 Audit Skill — Evaluation Report", "other": "Português",
        "other_href": "eval-report.pt-BR.html", "label": "Evaluation report",
        "subtitle": "Blind evaluation of skill v{ver} across {pages} test pages with {known} documented "
                    "failures and {tn} should-pass items, graded strictly against the ground truth.",
        "date": "Date", "version": "Skill version", "pages": "Test pages", "known": "Known failures",
        "k_detect": "Detection rate", "k_detect_d": "{hit} of {known} known failures reported as fails",
        "k_missed": "Missed", "k_missed_d": "Known failures not reported",
        "k_fp": "False positives", "k_fp_d": "{tn_bad} should-pass items failed + {fp_extra} other",
        "k_cov": "Criteria rated", "k_cov_d": "Pages where all 55 criteria got a status",
        "m_label": "Methodology", "m_h": "How this evaluation was run",
        "m_items": [
            "<strong>Blind.</strong> Each page was audited from a copy with every HTML, CSS and JS comment "
            "removed, a neutral <code>&lt;title&gt;</code> and a neutral file name (<code>page-NN.html</code>). "
            "The previous evaluation shipped the answers inside the pages (<code>&lt;!-- FAIL: … --&gt;</code>).",
            "<strong>Independent auditors.</strong> Three fresh agents, four pages each, could read only the "
            "skill folder and their pages — never the ground truth or the grader.",
            "<strong>Strict grading.</strong> A known failure counts only if the audit filed a <em>fail</em> "
            "finding under an accepted success criterion that names the element. The old grader matched "
            "keywords anywhere in the report.",
            "<strong>Manual review.</strong> Every fail finding that matches no known failure was read and "
            "classified as a genuine issue the ground truth missed, or as a false positive.",
        ],
        "t_label": "Per-page results", "t_h": "Test page breakdown",
        "th": ["Test page", "Focus", "Known", "Detected", "Should-pass OK", "Extra genuine", "False pos.", "Result"],
        "pass": "Pass", "partial": "Partial", "note": "Note",
        "miss_label": "Misses", "miss_h": "Known failures the audit did not report", "miss_none": "None — every known failure was reported.",
        "fp_label": "False positives", "fp_h": "Reported failures that are not real", "fp_none": "None.",
        "ex_label": "Beyond the ground truth", "ex_h": "Genuine issues the test pages didn't document",
        "ex_none": "None.",
        "cov_label": "Coverage", "cov_h": "Success criteria exercised by known failures",
        "cov_p": "{n} of the 55 WCAG 2.2 A + AA criteria have at least one known failure in the suite. "
                 "The rest are only checked for a status (pass / fail / N/A) on every page.",
        "cov_missing": "Not exercised by any known failure:",
        "v1_label": "Compared with v1.0", "v1_h": "Why the numbers changed",
        "v1_p": "The v1.0 report claimed 100% (56/56), but the auditor could read the answers in the page comments, "
                "and the pages documented 59 failures, not 56. Graded blind, 8 of those 59 turned out to be wrong in "
                "the ground truth itself: e.g. .subtitle #757575 is 4.61:1, not 4.48:1; the rgba overlay is 7.09:1; "
                "the \"modal trap\" doesn't trap focus; the 900px table sits in a scroll container. v1.0 \"detected\" "
                "all of them, including a 4.48:1 ratio that only existed in the comment. They are now should-pass "
                "items. v1.1 adds 55-criteria coverage and two new pages (16 more known failures).",
        "lim": "<strong>Limitations:</strong> Single-page audits are static code analysis — no real keyboard, "
               "screen reader or JavaScript execution. Some class names in the older pages still hint at the issue "
               "(e.g. <code>.fake-h1</code>). The Storybook mode is not covered by this suite.",
        "footer": "WCAG 2.2 Audit Skill evaluation — generated {date} — {pages} pages, {known} known failures, {rate}% detection",
        "sc": "SC",
        "cols": ["Page", "SC", "Element", "Note"],
        "verdict_k": "{rate}% detected",
        "verdict_p": "{hit} of {known} known failures found, {tn_ok} of {tn} should-pass items left alone, "
                     "{fp} false positives and {gen} real issues beyond the ground truth. Audited blind, graded strictly.",
    },
    "pt": {
        "lang": "pt-BR", "title": "Skill de Auditoria WCAG 2.2 — Relatório de Avaliação", "other": "English",
        "other_href": "eval-report.html", "label": "Relatório de avaliação",
        "subtitle": "Avaliação às cegas da skill v{ver} em {pages} páginas de teste, com {known} falhas "
                    "documentadas e {tn} itens que devem passar, com correção rígida contra o gabarito.",
        "date": "Data", "version": "Versão da skill", "pages": "Páginas de teste", "known": "Falhas conhecidas",
        "k_detect": "Taxa de detecção", "k_detect_d": "{hit} de {known} falhas conhecidas reportadas como falha",
        "k_missed": "Não detectadas", "k_missed_d": "Falhas conhecidas que não foram reportadas",
        "k_fp": "Falsos positivos", "k_fp_d": "{tn_bad} itens que deviam passar + {fp_extra} outros",
        "k_cov": "Critérios avaliados", "k_cov_d": "Páginas em que os 55 critérios receberam status",
        "m_label": "Metodologia", "m_h": "Como a avaliação foi feita",
        "m_items": [
            "<strong>Às cegas.</strong> Cada página foi auditada a partir de uma cópia sem nenhum comentário de "
            "HTML, CSS ou JS, com <code>&lt;title&gt;</code> e nome de arquivo neutros (<code>page-NN.html</code>). "
            "A avaliação anterior trazia as respostas dentro das páginas (<code>&lt;!-- FAIL: … --&gt;</code>).",
            "<strong>Auditores independentes.</strong> Três agentes novos, com quatro páginas cada, só podiam ler "
            "a pasta da skill e as próprias páginas, nunca o gabarito nem o avaliador.",
            "<strong>Correção rígida.</strong> Uma falha conhecida só conta se a auditoria registrou um achado "
            "<em>fail</em> num critério aceito e citando o elemento. O avaliador antigo procurava palavras-chave "
            "em qualquer parte do relatório.",
            "<strong>Revisão manual.</strong> Todo achado de falha que não corresponde a uma falha conhecida foi "
            "lido e classificado como problema real que o gabarito não tinha, ou como falso positivo.",
        ],
        "t_label": "Resultados por página", "t_h": "Detalhamento por página de teste",
        "th": ["Página", "Foco", "Conhecidas", "Detectadas", "Passa OK", "Extras reais", "Falsos pos.", "Resultado"],
        "pass": "Passou", "partial": "Parcial", "note": "Nota",
        "miss_label": "Não detectadas", "miss_h": "Falhas conhecidas que a auditoria não reportou",
        "miss_none": "Nenhuma: todas as falhas conhecidas foram reportadas.",
        "fp_label": "Falsos positivos", "fp_h": "Falhas reportadas que não são reais", "fp_none": "Nenhum.",
        "ex_label": "Além do gabarito", "ex_h": "Problemas reais que as páginas de teste não documentavam",
        "ex_none": "Nenhum.",
        "cov_label": "Cobertura", "cov_h": "Critérios exercitados por falhas conhecidas",
        "cov_p": "{n} dos 55 critérios WCAG 2.2 A + AA têm pelo menos uma falha conhecida na suíte. "
                 "Os demais são verificados apenas quanto ao status (passa / falha / N/A) em cada página.",
        "cov_missing": "Sem nenhuma falha conhecida:",
        "v1_label": "Comparação com a v1.0", "v1_h": "Por que os números mudaram",
        "v1_p": "O relatório da v1.0 dizia 100% (56/56), mas o auditor podia ler as respostas nos comentários das "
                "páginas, e elas documentavam 59 falhas, não 56. Na avaliação às cegas, 8 dessas 59 se mostraram erros "
                "do próprio gabarito: por exemplo, .subtitle #757575 tem 4,61:1, e não 4,48:1; o overlay rgba tem 7,09:1; "
                "o \"modal trap\" não prende o foco; a tabela de 900px está num contêiner com rolagem. A v1.0 "
                "\"detectou\" todas, inclusive uma razão de 4,48:1 que só existia no comentário. Agora elas são itens "
                "que devem passar. A v1.1 cobre os 55 critérios e tem duas páginas novas (mais 16 falhas conhecidas).",
        "lim": "<strong>Limitações:</strong> a auditoria de página única é análise estática do código, sem teclado "
               "real, leitor de tela nem execução de JavaScript. Alguns nomes de classe das páginas antigas ainda "
               "dão pista do problema (por exemplo <code>.fake-h1</code>). O modo Storybook não é coberto por esta suíte.",
        "footer": "Avaliação da Skill de Auditoria WCAG 2.2 — gerado em {date} — {pages} páginas, {known} falhas conhecidas, {rate}% de detecção",
        "sc": "SC",
        "cols": ["Página", "SC", "Elemento", "Nota"],
        "verdict_k": "{rate}% detectado",
        "verdict_p": "{hit} de {known} falhas conhecidas encontradas, {tn_ok} de {tn} itens que devem passar "
                     "preservados, {fp} falsos positivos e {gen} problemas reais além do gabarito. Auditoria às cegas, "
                     "correção rígida.",
    },
}

ALL_SC = (
    "1.1.1 1.2.1 1.2.2 1.2.3 1.2.4 1.2.5 1.3.1 1.3.2 1.3.3 1.3.4 1.3.5 1.4.1 1.4.2 1.4.3 1.4.4 "
    "1.4.5 1.4.10 1.4.11 1.4.12 1.4.13 2.1.1 2.1.2 2.1.4 2.2.1 2.2.2 2.3.1 2.4.1 2.4.2 2.4.3 "
    "2.4.4 2.4.5 2.4.6 2.4.7 2.4.11 2.5.1 2.5.2 2.5.3 2.5.4 2.5.7 2.5.8 3.1.1 3.1.2 3.2.1 3.2.2 "
    "3.2.3 3.2.4 3.2.6 3.3.1 3.3.2 3.3.3 3.3.4 3.3.7 3.3.8 4.1.2 4.1.3"
).split()


def esc(s):
    return html.escape(str(s))


def build(lang, res, review):
    t = T[lang]
    pp = res["per_page"]
    known, hit, tn = res["known_failures"], res["detected"], res["should_pass_items"]
    tn_bad = tn - res["should_pass_correct"]
    verdicts = {p: review.get(p, []) for p in pp}
    fp_extra = sum(1 for v in verdicts.values() for r in v if r["verdict"] == "false_positive")
    gen_total = sum(1 for v in verdicts.values() for r in v if r["verdict"] == "genuine")
    full_cov = sum(1 for r in pp.values() if r["meta"]["all_55_criteria_rated"])
    rate = res["detection_rate"] if lang == "en" else str(res["detection_rate"]).replace(".", ",")
    fmt = dict(ver=res["skill_version"], pages=res["test_pages"], known=known, tn=tn, hit=hit,
               tn_bad=tn_bad, fp_extra=fp_extra, date=DATE, rate=rate, tn_ok=res["should_pass_correct"],
               fp=tn_bad + fp_extra, gen=gen_total)

    rows, misses, fps, extras = [], [], [], []
    for page, r in pp.items():
        n = page[:2]
        name = PAGES[page][0 if lang == "en" else 1]
        focus = PAGES[page][2 if lang == "en" else 3]
        tps = [a for a in r["assertions"] if a["type"] == "tp"]
        tns = [a for a in r["assertions"] if a["type"] == "tn"]
        d = sum(a["passed"] for a in tps)
        ok_tn = sum(a["passed"] for a in tns)
        gen = [x for x in verdicts[page] if x["verdict"] == "genuine"]
        fpx = [x for x in verdicts[page] if x["verdict"] == "false_positive"]
        clean = d == len(tps) and ok_tn == len(tns) and not fpx
        badge = (f'<span class="badge b-pass">{t["pass"]}</span>' if clean
                 else f'<span class="badge b-warn">{t["partial"]}</span>')
        rows.append(f"<tr{'' if clean else ' class=r-warn'}><td><strong>{n}</strong> {esc(name)}</td>"
                    f"<td class='note'>{esc(focus)}</td><td class='c mono'>{len(tps)}</td><td class='c mono'>{d}</td>"
                    f"<td class='c mono'>{ok_tn}/{len(tns)}</td><td class='c mono'>{len(gen)}</td>"
                    f"<td class='c mono'>{len(fpx) + len(tns) - ok_tn}</td><td>{badge}</td></tr>")
        note = "note_en" if lang == "en" else "note_pt"
        misses += [(n, a["sc"], "", esc(a["text"])) for a in tps if not a["passed"]]
        fps += [(n, a["sc"], "", esc(a["text"])) for a in tns if not a["passed"]]
        fps += [(n, x["sc"], esc(x["element"]), esc(x[note])) for x in fpx]
        extras += [(n, x["sc"], esc(x["element"]), esc(x[note])) for x in gen]

    def table(items, empty):
        if not items:
            return f"<p class='empty'>{empty}</p>"
        head = "".join(f"<th>{c}</th>" for c in t["cols"])
        body = "".join(f"<tr><td class='mono'>{n}</td><td class='mono'>{sc}</td>"
                       f"<td>{f'<code>{el}</code>' if el else ''}</td><td class='note'>{txt}</td></tr>"
                       for n, sc, el, txt in items)
        return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"

    tested = sorted({a["sc"] for r in pp.values() for a in r["assertions"] if a["type"] == "tp"}, key=ALL_SC.index)
    untested = [s for s in ALL_SC if s not in tested]
    ok = hit == known and not (tn_bad + fp_extra)
    css = open(os.path.join(EVAL_DIR, "report.css")).read()
    th = "".join(f"<th{' class=c' if 1 < i < 7 else ''}>{h}</th>" for i, h in enumerate(t["th"]))
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(t['title'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
{css}
</style>
</head>
<body>
<main class="wrap">
  <header>
    <div class="top">
      <div class="eyebrow">{t['label']} · WCAG 2.2 A + AA · {DATE}</div>
      <a href="{t['other_href']}" hreflang="{'pt-BR' if lang == 'en' else 'en'}">{t['other']}</a>
    </div>
    <h1>WCAG 2.2 Audit Skill v{res['skill_version']}</h1>
    <p class="sub">{t['subtitle'].format(**fmt)}</p>
  </header>

  <div class="verdict{' ok' if ok else ''}" style="{'' if ok else 'border-color:var(--warn);background:var(--warn-bg)'}">
    <strong style="{'' if ok else 'color:var(--warn)'}">{t['verdict_k'].format(**fmt).upper()}</strong>
    <p>{t['verdict_p'].format(**fmt)}</p>
  </div>

  <div class="kpis">
    <div class="kpi p"><b>{hit}/{known}</b><span>{t['k_detect']}</span></div>
    <div class="kpi {'p' if hit == known else 'f'}"><b>{known - hit}</b><span>{t['k_missed']}</span></div>
    <div class="kpi {'p' if not fmt['fp'] else 'w'}"><b>{fmt['fp']}</b><span>{t['k_fp']}</span></div>
    <div class="kpi p"><b>{fmt['tn_ok']}/{tn}</b><span>{t['th'][4]}</span></div>
    <div class="kpi a"><b>{gen_total}</b><span>{t['ex_label']}</span></div>
    <div class="kpi a"><b>{full_cov}/{res['test_pages']}</b><span>{t['k_cov_d']}</span></div>
  </div>

  <section>
    <h2>{t['m_h']}</h2>
    <ol class="prio">{''.join(f'<li><p>{i}</p></li>' for i in t['m_items'])}</ol>
  </section>

  <section>
    <h2>{t['t_h']}</h2>
    <div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
  </section>

  <section>
    <h2>{t['miss_h']}</h2>
    {table(misses, t['miss_none'])}
  </section>

  <section>
    <h2>{t['fp_h']}</h2>
    {table(fps, t['fp_none'])}
  </section>

  <section>
    <h2>{t['ex_h']} <span class="badge b-na">{gen_total}</span></h2>
    <details><summary>{t['ex_label']}</summary>{table(extras, t['ex_none'])}</details>
  </section>

  <section>
    <h2>{t['cov_h']}</h2>
    <p class="sub">{t['cov_p'].format(n=len(tested))}</p>
    <div class="tags">{''.join(f'<code>{s}</code>' for s in tested)}</div>
    <p class="sub">{t['cov_missing']} {', '.join(untested)}</p>
  </section>

  <section>
    <h2>{t['v1_h']}</h2>
    <p class="sub">{t['v1_p']}</p>
  </section>

  <footer><p>{t['lim']}</p><p>{t['footer'].format(**fmt)}</p></footer>
</main>
</body>
</html>
"""


def main():
    res = json.load(open(os.path.join(EVAL_DIR, "grading_results.json")))
    rp = os.path.join(EVAL_DIR, "manual_review.json")
    review = json.load(open(rp)) if os.path.isfile(rp) else {}
    for lang, name in (("en", "eval-report.html"), ("pt", "eval-report.pt-BR.html")):
        with open(os.path.join(DOCS, name), "w") as f:
            f.write(build(lang, res, review))
        print("wrote", os.path.normpath(os.path.join(DOCS, name)))


if __name__ == "__main__":
    main()
