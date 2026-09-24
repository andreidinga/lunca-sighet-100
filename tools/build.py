#!/usr/bin/env python3
"""Transforma HTML-ul brut al artifactelor in pagini statice pentru GitHub Pages.

Foloseste fisierele index.html descarcate din fiecare artifact (cu Artifact
action="read_file") si le scrie ca pagini de sine statatoare in radacina repo-ului.

    python3 tools/build.py <dir_cu_html_brut>

unde <dir_cu_html_brut> contine: index/index.html, jurnal/index.html,
planse/index.html, instalatii/index.html, randari/index.html, poze/index.html
"""
import re
import sys
from pathlib import Path

# id de artifact -> pagina locala. Linkurile vin in doua forme:
#   https://claude.ai/code/artifact/<uuid>  -> cheia e prefixul de 8 caractere
#   https://claude.ai/artifact/<id scurt>   -> cheia e id-ul intreg
ARTIFACTS = {
    "c19277be": "index.html",       # Santier Lunca Sighet 100
    "295bdf4b": "index.html",       # varianta mai veche a paginii de santier
    "8b7c86f6": "jurnal.html",      # Jurnal de santier
    "30feb1be": "planse.html",      # Planse proiect
    "5eabaa01": "instalatii.html",  # Planse instalatii
    "JNY9ydoCZZKjirvHU8GDW6": "randari.html",  # Randari Lunca Sighet
    "Dj8kLEd6hurnXFohZkhFST": "poze.html",     # Poze de santier
}

SOURCES = {
    "index.html": "index",
    "jurnal.html": "jurnal",
    "planse.html": "planse",
    "instalatii.html": "instalatii",
    "randari.html": "randari",
    "poze.html": "poze",
}

HEAD = ('<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow"></head><body>')
TAIL = "</body></html>"

# https://claude.ai/artifact/<id> sau https://claude.ai/code/artifact/<id>,
# cu sufixe de cale optionale; fragmentul (#...) ramane neatins
LINK_RE = re.compile(
    r"https://claude\.ai/(?:code/)?artifact/"
    r"([A-Za-z0-9][A-Za-z0-9-]*)(?:/[A-Za-z0-9._~-]*)*"
)
# target="_blank" rel="noopener" in orice ordine / cu ghilimele simple sau duble
ATTR_RE = re.compile(
    r"""\s*(?:target=["']_blank["']|rel=["']noopener(?:\s+noreferrer)?["'])""")


def strip_shell(html: str) -> str:
    """Taie tot pana la primul <body> inclusiv si </body></html> de la final.

    Unele artifacte au continutul incheiat cu propriul </body></html>, peste care
    invelisul artifactului mai adauga unul; se taie toate cele de la final.
    """
    i = html.find("<body>")
    if i == -1:
        raise SystemExit("nu am gasit <body>")
    body = html[i + len("<body>"):].rstrip()
    if not body.endswith(TAIL):
        raise SystemExit("nu se termina cu </body></html>")
    while body.endswith(TAIL):
        body = body[: -len(TAIL)].rstrip()
    return body


def page_for(artifact_id: str) -> str | None:
    """Pagina locala pentru un id de artifact: id intreg, altfel prefix de uuid."""
    return ARTIFACTS.get(artifact_id) or ARTIFACTS.get(artifact_id[:8])


def rewrite_links(body: str) -> str:
    def sub(m):
        page = page_for(m.group(1))
        if page is None:
            raise SystemExit(f"id de artifact necunoscut in link: {m.group(0)}")
        return page
    return LINK_RE.sub(sub, body)


def build(raw_dir: Path, out_dir: Path) -> list[str]:
    written = []
    for page, src in SOURCES.items():
        raw = (raw_dir / src / "index.html").read_text(encoding="utf-8")
        body = strip_shell(raw)
        body = rewrite_links(body)
        body = ATTR_RE.sub("", body)
        (out_dir / page).write_text(HEAD + "\n" + body + "\n" + TAIL + "\n",
                                    encoding="utf-8")
        written.append(page)
    return written


def check(out_dir: Path) -> None:
    """Verificari: fara linkuri de artifact ramase, fara preturi in text vizibil."""
    price_re = re.compile(r"\u20ac|\bEUR\b|\blei\b|\bRON\b|[Bb]uget|[Pp]re\u021b", re.UNICODE)
    allow_re = re.compile(
        r"(?i)f\u0103r\u0103 pre\u021b|no prices|no budget|f\u0103r\u0103 buget|/\* budget \*/")
    problems = []
    for page in SOURCES:
        text = (out_dir / page).read_text(encoding="utf-8")
        if "claude.ai/artifact" in text or "claude.ai/code/artifact" in text:
            problems.append(f"{page}: a ramas un link claude.ai de artifact")
        if 'target="_blank"' in text or 'rel="noopener"' in text:
            problems.append(f"{page}: a ramas target=_blank / rel=noopener")
        # cauta preturi doar in textul vizibil: fara data URI, script, style
        visible = re.sub(r"data:[^\"')\s]+", "", text)
        visible = re.sub(r"(?is)<script[^>]*>.*?</script>", "", visible)
        visible = re.sub(r"(?is)<style[^>]*>.*?</style>", "", visible)
        for m in price_re.finditer(visible):
            ctx = visible[max(0, m.start() - 70): m.end() + 70].replace("\n", " ")
            if allow_re.search(ctx):
                continue  # disclaimerul "Fara preturi si fara buget", in RO sau EN
            problems.append(f"{page}: posibil pret -> ...{ctx}...")
    if problems:
        print("VERIFICARE - de analizat:")
        for p_ in problems:
            print("  " + p_)
    else:
        print("VERIFICARE OK: fara linkuri de artifact, fara target=_blank, fara preturi.")


if __name__ == "__main__":
    raw = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path.cwd()
    pages = build(raw, out)
    print("scrise:", ", ".join(pages))
    check(out)
