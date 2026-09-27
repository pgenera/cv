#!/usr/bin/env python3
"""Render cv.yaml into LaTeX, a single-file website, and Markdown.

Usage: build.py cv.yaml OUTDIR
Writes OUTDIR/phil_genera_cv.tex, OUTDIR/index.html, OUTDIR/phil_genera_cv.md.
"""

import html
import re
import sys
from datetime import date
from pathlib import Path

import yaml

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

    L += [r"\section*{Additional}"] + tex_bullets(cv["additional"])

    tpl = (TEMPLATES / "cv.tex").read_text()
    return tpl.replace("<<NAME>>", tex(cv["name"])).replace("<<BODY>>", "\n".join(L))


# ---------- Markdown ----------

def md(s):
    return s.replace(" ", " ")


def md_dates(x):
    return f"{x['start']} – {x['end']}" if "start" in x else x["dates"]


def render_md(cv):
    L = [f"# {cv['name']}", "", cv["headline"], ""]
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
    L += [f"- {md(b)}" for b in cv["additional"]] + [""]
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


def render_html(cv):
    contact = [f'<a class="chip" href="mailto:{cv["email"]}">{h(cv["email"])}</a>']
    if cv.get("phone"):
        contact.append(f'<a class="chip" href="{tel(cv["phone"])}">{h(cv["phone"])}</a>')
    contact += [f'<a class="chip" href="{l["url"]}">{h(l["label"])}</a>' for l in cv["links"]]

    exp = []
    for job in cv["experience"]:
        roles = []
        for r in job["roles"]:
            team = f'<span class="team">{h(r["team"])}</span>' if r.get("team") else ""
            roles.append(
                f'<li class="role reveal"><div class="role-head"><h4>{h(r["title"])}</h4>'
                f'{team}<time>{h_dates(r)}</time></div>{h_bullets(r["bullets"])}</li>')
        exp.append(
            f'<article class="employer"><header class="employer-head"><h3>{h(job["org"])}</h3>'
            f'<time>{h_dates(job)}</time></header><ol class="timeline">{"".join(roles)}</ol></article>')

    projects = []
    for p in cv["personal_projects"]:
        name = h(p["name"])
        if p.get("url"):
            name = f'<a href="{p["url"]}">{name}</a>'
        desc = f'<p class="desc">{h(p["description"])}</p>' if p.get("description") else ""
        projects.append(
            f'<article class="card reveal"><div class="card-head"><h3>{name}</h3>'
            f'<time>{h(p["dates"])}</time></div>{desc}{h_bullets(p["bullets"])}</article>')

    edu = "".join(
        f'<p><strong>{h(e["school"])}</strong> <time>{h_dates(e)}</time><br>{h(e["degree"])}</p>'
        for e in cv["education"])

    fills = {
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
        "ADDITIONAL": h_bullets(cv["additional"]),
        "BASENAME": BASENAME,
        "BUILT": date.today().isoformat(),
    }
    out = (TEMPLATES / "site.html").read_text()
    for k, v in fills.items():
        out = out.replace("{{" + k + "}}", v)
    leftover = re.findall(r"\{\{[A-Z]+\}\}", out)
    if leftover:
        sys.exit(f"unfilled placeholders in site.html: {leftover}")
    return out


def tel(phone):
    return "tel:" + re.sub(r"[^0-9+]", "", phone)


def main():
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    cv = yaml.safe_load(src.read_text())
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{BASENAME}.tex").write_text(render_tex(cv))
    (outdir / f"{BASENAME}.md").write_text(render_md(cv))
    (outdir / "index.html").write_text(render_html(cv))


if __name__ == "__main__":
    main()
