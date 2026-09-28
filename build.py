#!/usr/bin/env python3
"""Render cv.yaml into LaTeX, a single-file website, and Markdown.

Usage: build.py cv.yaml OUTDIR
Writes OUTDIR/phil_genera_cv.tex, OUTDIR/index.html, OUTDIR/phil_genera_cv.md.
"""

import base64
import hashlib
import os
import html
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

import boston_map


def content_date():
    """The content date: SOURCE_DATE_EPOCH (set by make from the last commit
    touching the CV's sources), else today."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    return datetime.fromtimestamp(int(epoch), timezone.utc).date() if epoch else date.today()


def fingerprint(path):
    """Short sha256 of the source file, embedded in the PDF metadata."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]

ROOT = Path(__file__).parent
TEMPLATES = ROOT / "templates"
BASENAME = "phil_genera_cv"

# [text](url) | `code` | **bold** | *em*
INLINE = re.compile(
    r"\[(?P<ltext>[^\]]+)\]\((?P<url>[^)]+)\)"
    r"|`(?P<code>[^`]+)`"
    r"|\*\*(?P<bold>.+?)\*\*"
    r"|\*(?P<em>.+?)\*"
)


def inline(text, esc, link, code, bold, em):
    """Convert the inline markup subset, escaping plain runs with esc."""
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        rec = lambda s: inline(s, esc, link, code, bold, em)
        if m["url"]:
            out.append(link(rec(m["ltext"]), m["url"]))
        elif m["code"]:
            out.append(code(esc(m["code"])))
        elif m["bold"]:
            out.append(bold(rec(m["bold"])))
        else:
            out.append(em(rec(m["em"])))
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def plain(text):
    """Strip inline markup."""
    return inline(text, lambda s: s.replace(" ", " "),
                  lambda t, u: t, lambda c: c, lambda b: b, lambda e: e)


# ---------- LaTeX ----------

TEX_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}", " ": "~",
}


def tex_esc(s):
    return "".join(TEX_ESCAPES.get(c, c) for c in s)


def tex(s):
    return inline(
        s, tex_esc,
        lambda t, u: r"\href{%s}{%s}" % (u.replace("%", r"\%").replace("#", r"\#"), t),
        lambda c: r"\texttt{%s}" % c,
        lambda b: r"\textbf{%s}" % b,
        lambda e: r"\emph{%s}" % e,
    )


def tex_dates(x):
    return f"{x['start']} -- {x['end']}" if "start" in x else tex(x["dates"])


def tex_bullets(items):
    lines = [r"\begin{itemize}"]
    lines += [r"  \item " + tex(b) for b in items]
    lines.append(r"\end{itemize}")
    return lines


def render_tex(cv):
    L = []
    contact = [tex(cv["location"]),
               r"\href{mailto:%s}{%s}" % (cv["email"], tex(cv["email"]))]
    if cv.get("phone"):
        contact.append(r"\href{%s}{%s}" % (tel(cv["phone"]), tex(cv["phone"])))
    contact += [r"\href{%s}{%s}" % (l["url"], tex(l["label"])) for l in cv["links"]]
    L += [
        "% ---------- HEADER ----------",
        r"\begin{center}",
        r"  {\Large \scshape %s}\\[3pt]" % tex(cv["name"]),
        r"  %s\\[2pt]" % tex(cv["headline"]),
        r"  \small " + " $\\vert$\n  ".join(contact),
        r"\end{center}",
        "",
        r"\section*{Summary}",
        tex(cv["summary"]),
        "",
        r"\section*{Technical}",
        tex(cv["technical"]),
        "",
        r"\section*{Experience}",
        "",
    ]
    for i, job in enumerate(cv["experience"]):
        multi = len(job["roles"]) > 1
        if multi:
            L += [r"\textbf{%s} \hfill \textit{%s}" % (tex(job["org"]), tex_dates(job)), ""]
        for j, r in enumerate(job["roles"]):
            L.append(r"\vspace{%s}" % ("2pt" if multi else "4pt"))
            label = tex(r["title"]) + r" $\cdot$ " + tex(r.get("team") or job["org"])
            L.append(r"\role{%s}{%s}" % (label, tex_dates(r)))
            L += tex_bullets(r["bullets"])
            L.append("")

    L += [r"\section*{Personal Projects}", ""]
    for i, p in enumerate(cv["personal_projects"]):
        L.append(r"\vspace{%s}" % ("1pt" if i == 0 else "2pt"))
        name = tex(p["name"])
        if p.get("url"):
            name = r"\href{%s}{%s}" % (p["url"], name)
        if p.get("description"):
            name += r" $\cdot$ " + tex(p["description"])
        L.append(r"\role{%s}{%s}" % (name, tex(p["dates"])))
        L += tex_bullets(p["bullets"])
        L.append("")

    L += [r"\section*{Patents \& Publications}"] + tex_bullets(cv["publications"]) + [""]

    L.append(r"\section*{Education}")
    for e in cv["education"]:
        L += [r"\textbf{%s} \hfill \textit{%s}\\" % (tex(e["school"]), tex_dates(e)),
              r"\textit{\small %s}" % tex(e["degree"])]
    L.append("")

    L += [r"\section*{Additional}", r"\begin{itemize}"]
    for a in cv["additional"]:
        if isinstance(a, dict):
            # Same layout as \role: text wraps in the left 79%, date top-right.
            L.append(r"  \item \begin{tabular*}{\linewidth}[t]{@{}p{0.79\linewidth}@{\extracolsep{\fill}}r@{}}"
                     + tex(a["text"]) + r" & \textit{%s}\end{tabular*}" % tex_dates(a))
        else:
            L.append(r"  \item " + tex(a))
    L.append(r"\end{itemize}")

    tpl = (TEMPLATES / "cv.tex").read_text()
    site = cv["site"]
    fills = {
        "<<NAME>>": tex(cv["name"]),
        "<<SITE>>": site,
        "<<SITELABEL>>": tex(site.split("://", 1)[-1].rstrip("/")),
        "<<UPDATED>>": content_date().strftime("%B %Y"),
        "<<PDFSUBJECT>>": tex(f"CV. Latest version: {site}"),
        "<<PDFKEYWORDS>>": tex(f"source {site}; cv.yaml sha256:{cv['_fingerprint']}"),
        "<<BODY>>": "\n".join(L),
    }
    for k, v in fills.items():
        tpl = tpl.replace(k, v)
    return tpl


# ---------- Markdown ----------

def md(s):
    return s.replace(" ", " ")


def md_dates(x):
    return f"{x['start']} – {x['end']}" if "start" in x else x["dates"]


def render_md(cv):
    L = [f"# {cv['name']}", "", cv["headline"], "",
         f"Latest version: <{cv['site']}>. Updated {content_date():%B %Y}.", ""]
    L += [f"- Location: {cv['location']}", f"- Email: <{cv['email']}>"]
    if cv.get("phone"):
        L.append(f"- Phone: {cv['phone']}")
    L += [f"- [{l['label']}]({l['url']})" for l in cv["links"]]
    L += ["", "## Summary", "", md(cv["summary"]), "",
          "## Technical", "", md(cv["technical"]), "", "## Experience", ""]
    for job in cv["experience"]:
        L += [f"### {job['org']} ({md_dates(job)})", ""]
        for r in job["roles"]:
            title = r["title"] + (f", {r['team']}" if r.get("team") else "")
            L += [f"#### {title} ({md_dates(r)})", ""]
            L += [f"- {md(b)}" for b in r["bullets"]] + [""]
    L += ["## Personal Projects", ""]
    for p in cv["personal_projects"]:
        name = f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]
        if p.get("description"):
            name += f": {p['description']}"
        L += [f"### {name} ({p['dates']})", ""]
        L += [f"- {md(b)}" for b in p["bullets"]] + [""]
    L += ["## Patents and Publications", ""]
    L += [f"- {md(b)}" for b in cv["publications"]] + [""]
    L += ["## Education", ""]
    L += [f"- {e['school']}, {e['degree']} ({md_dates(e)})" for e in cv["education"]] + [""]
    L += ["## Additional", ""]
    L += [f"- {md(a['text'])} ({md_dates(a)})" if isinstance(a, dict) else f"- {md(a)}"
          for a in cv["additional"]] + [""]
    return "\n".join(L)


# ---------- HTML ----------

def h(s):
    return inline(
        s, lambda t: html.escape(t, quote=False).replace(" ", "&nbsp;"),
        lambda t, u: f'<a href="{html.escape(u)}">{t}</a>',
        lambda c: f"<code>{c}</code>",
        lambda b: f"<strong>{b}</strong>",
        lambda e: f"<em>{e}</em>",
    )


def h_dates(x):
    return f"{html.escape(x['start'])}&ndash;{html.escape(x['end'])}" if "start" in x \
        else html.escape(x["dates"])


def h_bullets(items):
    return "<ul>" + "".join(f"<li>{h(b)}</li>" for b in items) + "</ul>"


def font_b64(name):
    return base64.b64encode((TEMPLATES / "fonts" / name).read_bytes()).decode()


def render_html(cv):
    contact = [f'<a href="mailto:{cv["email"]}">{h(cv["email"])}</a>']
    if cv.get("phone"):
        contact.append(f'<a href="{tel(cv["phone"])}">{h(cv["phone"])}</a>')
    contact += [f'<a href="{l["url"]}">{h(l["label"])}</a>' for l in cv["links"]]

    exp, here_done = [], False
    for job in cv["experience"]:
        single = len(job["roles"]) == 1
        exp.append(f'<div class="org"><time>{h_dates(job)}</time><h3>{h(job["org"])}</h3></div>')
        for r in job["roles"]:
            here = not here_done and r.get("end") == "Present"
            here_done = here_done or here
            team = f'<span class="team">{h(r["team"])}</span>' if r.get("team") else ""
            when = "" if single and h_dates(r) == h_dates(job) else f"<time>{h_dates(r)}</time>"
            exp.append(
                f'<div class="stop{" here" if here else ""}">{when}<div><h4>{h(r["title"])}</h4>'
                f'{team}{h_bullets(r["bullets"])}</div></div>')

    projects = []
    for p in cv["personal_projects"]:
        name = h(p["name"])
        if p.get("url"):
            name = f'<a href="{p["url"]}">{name}</a>'
        what = f'<p class="what">{h(p["description"])}</p>' if p.get("description") else ""
        projects.append(
            f'<article class="project"><h3>{name}<time>{h(p["dates"])}</time></h3>'
            f'{what}{h_bullets(p["bullets"])}</article>')

    edu = "".join(
        f'<p><strong>{h(e["school"])}</strong><time>{h_dates(e)}</time></p><p>{h(e["degree"])}</p>'
        for e in cv["education"])

    fills = {
        "FONT_ROMAN": font_b64("overpass-latin-wght-normal.woff2"),
        "FONT_ITALIC": font_b64("overpass-latin-wght-italic.woff2"),
        "MAP": boston_map.svg(h(cv["location"])),
        "MAP_ASPECT_VW": f'{boston_map.DATA["view"]["H"] / boston_map.DATA["view"]["W"] * 100:.2f}vw',
        "NAME": h(cv["name"]),
        "TITLE": html.escape(cv["name"]),
        "DESCRIPTION": html.escape(plain(cv["headline"]) + ". " + plain(cv["summary"]).split(". ")[0] + "."),
        "HEADLINE": h(cv["headline"]),
        "LOCATION": h(cv["location"]),
        "CONTACT": "".join(contact),
        "SUMMARY": h(cv["summary"]),
        "TECHNICAL": h(cv["technical"]),
        "EXPERIENCE": "".join(exp),
        "PROJECTS": "".join(projects),
        "PUBLICATIONS": h_bullets(cv["publications"]),
        "EDUCATION": edu,
        "ADDITIONAL": "<ul>" + "".join(
            f'<li>{h(a["text"])} <time class="when">{h_dates(a)}</time></li>' if isinstance(a, dict)
            else f"<li>{h(a)}</li>" for a in cv["additional"]) + "</ul>",
        "BASENAME": BASENAME,
        "BUILT": content_date().isoformat(),
        "SITE": html.escape(cv["site"]),
    }
    out = (TEMPLATES / "site.html").read_text()
    for k, v in fills.items():
        out = out.replace("{{" + k + "}}", v)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if leftover:
        sys.exit(f"unfilled placeholders in site.html: {leftover}")
    return out


def tel(phone):
    return "tel:" + re.sub(r"[^0-9+]", "", phone)


def main():
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    cv = yaml.safe_load(src.read_text())
    cv["_fingerprint"] = fingerprint(src)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{BASENAME}.tex").write_text(render_tex(cv))
    (outdir / f"{BASENAME}.md").write_text(render_md(cv))
    (outdir / "index.html").write_text(render_html(cv))


if __name__ == "__main__":
    main()
