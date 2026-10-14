#!/usr/bin/env python3
"""02_music 폴더의 md 문서들을 서로 연결해 index.html 한 장으로 만든다.

사용법:
    python build_site.py                  # index.html 생성
    python build_site.py --check-online   # 유튜브 watch 링크가 살아 있는지도 확인

- [[문서명]] / [[문서명|별칭]] / [[문서명\\|별칭]] (표 안) 위키링크를 사이트 내부 링크로 바꾼다.
- 플레이리스트(0927 문서의 '오늘 틀 곡 목록')를 기준으로 각 곡이 어느 문서·어느 절에서
  언급되는지 찾아 '연결 점검' 표를 만든다.
- 아티스트 이름(한글/영문 표기)은 절마다 첫 등장 시 해당 아티스트 노트로 자동 링크된다.
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from collections import defaultdict

from markdown_it import MarkdownIt

if hasattr(sys.stdout, "reconfigure"):  # Windows 콘솔(cp1252)에서도 한글 출력
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "index.html"

# ---------------------------------------------------------------- config
MAIN_DOCS = [
    # (slug, filename stem, short label, description)
    ("program", "0927-2026 - Bossa Nova.Samba.Tango", "감상회 프로그램",
     "실제로 들려줄 순서. 13곡 플레이리스트와 탱고·클래식 보충 리스트."),
    ("script", "0926-2026 -  60 minutes", "60분 해설 스크립트",
     "곡 사이에 할 이야기. 1부 뿌리부터 5부 정리, Q&A까지."),
    ("latin", "0926-2026 - Latin America", "남미 음악 심화",
     "군사독재의 노래, 부에나비스타 소셜 클럽과 쿠바 손, 리듬과 음계."),
    ("rhythm", "0925-2026 - Rhythm and Intro", "리듬 입문",
     "삼바·보사노바·쇼루·바이아움 리듬 정리와 초기 자료."),
]

# key, file name part, display name, years, region, one-liner, aliases (longest first is handled automatically)
ARTISTS = [
    ("jobim", "Tom Jobim", "톰 조빙", "1927–1994", "브라질",
     "보사노바의 작곡가. Chega de Saudade, Garota de Ipanema, Águas de Março.",
     ["안토니우 카를루스 조빙", "안토니오 카를로스 조빔", "톰 조빙", "톰 조빔", "조빙", "조빔",
      "Antônio Carlos Jobim", "Antonio Carlos Jobim", "Tom Jobim", "Jobim"]),
    ("getz", "Getz and Gilberto", "게츠 & 지우베르투", "1964",
     "브라질 · 미국",
     "스탠 게츠, 주앙·아스트루드 지우베르투. 보사노바를 세계로 보낸 Getz/Gilberto.",
     ["주앙 지우베르투", "주앙 질베르토", "아스트루드 지우베르투", "아스트루드 질베르토", "스탠 게츠",
      "Getz/Gilberto", "João Gilberto", "Astrud Gilberto", "Stan Getz"]),
    ("vinicius", "Vinicius de Moraes", "비니시우스 지 모라이스", "1913–1980", "브라질",
     "시인이자 외교관. 보사노바의 가사를 쓴 'O Poetinha'.",
     ["비니시우스 지 모라이스", "비니시우스 드 모라이스", "비니시우스", "Vinícius de Moraes", "Vinicius de Moraes"]),
    ("bonfa", "Luiz Bonfa", "루이스 본파", "1922–2001", "브라질",
     "흑인 오르페의 Manhã de Carnaval. 선율을 앞세운 솔로 기타.",
     ["루이스 본파", "루이스 봉파", "Luiz Bonfá", "Luiz Bonfa"]),
    ("valle", "Marcos Valle", "마르코스 발리", "1943–", "브라질",
     "보사노바 2세대. Samba de Verão(So Nice)와 Estrelar.",
     ["마르코스 발리", "Marcos Valle"]),
    ("baden", "Baden Powell", "바덴 파웰", "1937–2000", "브라질",
     "비니시우스와 만든 Os Afro-Sambas. 타악기 같은 기타.",
     ["바덴 파웰", "바든 파울", "Baden Powell"]),
    ("mendes", "Sergio Mendez", "세르지우 멘지스", "1941–2024", "브라질 · 미국",
     "Brasil '66으로 Mas que Nada를 세계 히트로. 보사노바를 팝과 힙합까지 넓혔다.",
     ["세르지우 멘지스", "세르지오 멘데스", "세르지오 멘지스", "멘지스",
      "Sérgio Mendes", "Sergio Mendes", "Sergio Mendez", "Brasil '66", "Brasil 66"]),
    ("lisa", "Lisa Ono", "오노 리사", "1962–", "브라질 · 일본",
     "상파울루 출생. 스탠더드를 보사노바로 부른 Tea for Two.",
     ["오노 리사", "Lisa Ono"]),
    ("tania", "Tania Maria", "타니아 마리아", "1948–", "브라질 · 프랑스",
     "피아노와 스캣을 겹치는 아프로-브라질리언 재즈. Dona Flor.",
     ["타니아 마리아", "Tânia Maria", "Tania Maria"]),
    ("piazzolla", "Astor Piazzolla", "아스토르 피아졸라", "1921–1992", "아르헨티나",
     "누에보 탱고. Libertango, Oblivion, Adiós Nonino.",
     ["아스토르 피아졸라", "피아졸라", "Astor Piazzolla", "Piazzolla"]),
    ("gardel", "Carlos Gardel", "카를로스 가르델", "1890–1935", "아르헨티나",
     "탱고에 노래를 입힌 '탱고의 황제'. Por una Cabeza.",
     ["카를로스 가르델", "가르델", "Carlos Gardel", "Gardel"]),
    ("matos", "Gerardo Matos Rodriguez", "헤라르도 마토스 로드리게스", "1897–1948", "우루과이",
     "세상에서 가장 유명한 탱고 La Cumparsita의 작곡가.",
     ["헤라르도 마토스 로드리게스", "마토스 로드리게스", "Matos Rodríguez", "Matos Rodriguez"]),
    ("albeniz", "Isaac Albeniz", "이사크 알베니스", "1860–1909", "스페인",
     "이름은 탱고, 반주는 하바네라. Tango in D(1890).",
     ["이사크 알베니스", "알베니스", "Albéniz", "Albeniz"]),
]

# 플레이리스트 곡 제목 → 본문에서 찾을 별칭
TRACK_ALIASES = {
    "pelo telefone": ["Pelo Telefone"],
    "aquarela do brasil": ["Aquarela do Brasil", "Aquarela do Brazil", "브라질의 수채화"],
    "chega de saudade": ["Chega de Saudade"],
    "desafinado": ["Desafinado"],
    "the girl from ipanema": ["Girl from Ipanema", "Garota de Ipanema"],
    "samba de verao": ["Samba de Verão", "Summer Samba", "So Nice"],
    "mas que nada": ["Mas Que Nada"],
    # '카르멘'만 쓰면 '카르멘 미란다'까지 잡힌다
    "카르멘 \"하바네라\"": ["오페라 카르멘", "비제 카르멘", "카르멘 \"하바네라\"", "카르멘 하바네라",
                        "카르멘의 첼로", "Carmen Habanera", "L'amour est un oiseau"],
    "libertango": ["Libertango", "리베르탱고"],
    "oblivion": ["Oblivion"],
    "insensatez": ["Insensatez", "How Insensitive"],
    "tea for two": ["Tea for Two"],
    "aguas de marco": ["Águas de Março", "Waters of March"],
}

SUMMARY_SECTIONS = ("개요", "오늘의 프로그램", "전체 음악 리스트", "오늘 틀 곡 목록")

GENRE_CLASS = {"삼바": "samba", "보사노바": "bossa", "하바네라": "habanera", "탱고": "tango"}


# ---------------------------------------------------------------- helpers
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def name_key(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def esc(s: str) -> str:
    return html.escape(s, quote=True)


md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")


class Doc:
    def __init__(self, slug, stem, label, desc, kind, artist=None):
        self.slug, self.stem, self.label, self.desc, self.kind, self.artist = slug, stem, label, desc, kind, artist
        self.path = HERE / f"{stem}.md"
        self.src = self.path.read_text(encoding="utf-8")
        self.toc: list[tuple[int, str, str]] = []          # (level, id, text)
        self.sections: list[tuple[str, str, str]] = []     # (id, heading, plain text)
        self.links: list[tuple[str, str, str]] = []        # (section id, link text, href)
        self.wikilinks: list[str] = []                     # target slugs
        self.broken: list[str] = []
        self.html = ""


DOCS: list[Doc] = [Doc(s, f, l, d, "main") for s, f, l, d in MAIN_DOCS]
for a in ARTISTS:
    DOCS.append(Doc(f"artist-{a[0]}", f"Artist - {a[1]}", a[2], a[5], "artist", artist=a))
BY_NAME = {name_key(d.stem): d for d in DOCS}
BY_SLUG = {d.slug: d for d in DOCS}

missing = [p.name for p in HERE.glob("*.md") if name_key(p.stem) not in BY_NAME]
if missing:
    print("! config에 없는 md 파일 (사이트에 안 들어감):", ", ".join(missing))

WIKI = re.compile(r"\[\[([^\]\|\\#]+?)(?:#([^\]\|\\]+?))?(?:\\?\|([^\]]+?))?\]\]")


def preprocess(doc: Doc) -> str:
    def sub(m):
        target, _anchor, alias = m.group(1), m.group(2), m.group(3)
        d = BY_NAME.get(name_key(target))
        if not d:
            text = (alias or target).strip()
            doc.broken.append(target)
            return f'<span class="broken" title="문서를 찾을 수 없음">{esc(text)}</span>'
        text = (alias or (d.artist[2] if d.artist else d.label)).strip()
        doc.wikilinks.append(d.slug)
        return f"[{text}](#/doc/{d.slug})"

    s = WIKI.sub(sub, doc.src)
    s = re.sub(r"==([^=\n]+?)==", r"<mark>\1</mark>", s)
    return s


def render(doc: Doc):
    tokens = md.parse(preprocess(doc))
    n = 0
    cur_id, cur_head, cur_text = f"{doc.slug}--top", "", []
    pending_link = None
    for i, t in enumerate(tokens):
        if t.type == "heading_open":
            if cur_text or cur_head:
                doc.sections.append((cur_id, cur_head, " ".join(cur_text)))
            n += 1
            cur_id = f"{doc.slug}--h{n}"
            t.attrSet("id", cur_id)
            inline = tokens[i + 1]
            cur_head = "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline")).strip()
            cur_head = re.sub(r"<[^>]+>", "", cur_head)
            lvl = int(t.tag[1])
            if lvl in (2, 3, 4) and cur_head:
                doc.toc.append((lvl, cur_id, cur_head))
            cur_text = []
        elif t.type == "inline":
            for c in t.children or []:
                if c.type == "link_open":
                    pending_link = [c.attrGet("href") or "", []]
                elif c.type == "link_close" and pending_link:
                    doc.links.append((cur_id, "".join(pending_link[1]), pending_link[0]))
                    pending_link = None
                elif c.type in ("text", "code_inline"):
                    cur_text.append(c.content)
                    if pending_link:
                        pending_link[1].append(c.content)
        elif t.type in ("fence", "code_block"):
            cur_text.append(t.content)
    doc.sections.append((cur_id, cur_head, " ".join(cur_text)))
    out = md.renderer.render(tokens, md.options, {})
    out = postprocess(out, doc)
    doc.html = out


def postprocess(h: str, doc: Doc) -> str:
    # 첫 줄이 비어 있는 표: 첫 본문 행을 머리글로 올린다
    def fix_table(m):
        body_first = m.group(1)
        return "<thead>\n<tr>" + re.sub(r"<(/?)td", r"<\1th", body_first) + "</tr>\n</thead>\n<tbody>\n"
    h = re.sub(r"<thead>\s*<tr>\s*(?:<th[^>]*>\s*</th>\s*)+</tr>\s*</thead>\s*<tbody>\s*<tr>(.*?)</tr>\s*",
               fix_table, h, flags=re.S)
    h = h.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    # 외부 링크는 새 탭
    def ext(m):
        href = html.unescape(m.group(1))
        cls = "yt" if ("youtube.com" in href or "youtu.be" in href) else "ext"
        if "spotify.com" in href:
            cls = "sp"
        return f'<a class="{cls}" target="_blank" rel="noopener" href="{m.group(1)}"'
    h = re.sub(r'<a href="(https?://[^"]+)"', ext, h)
    h = re.sub(r'<a href="(#/doc/[^"]+)"', r'<a class="wl" href="\1"', h)
    return autolink(h, doc)


def autolink(h: str, doc: Doc) -> str:
    alias_map = []
    for a in ARTISTS:
        if doc.artist and doc.artist[0] == a[0]:
            continue
        for al in a[6]:
            alias_map.append((al, a[0]))
    alias_map.sort(key=lambda x: -len(x[0]))
    rx = re.compile("|".join(re.escape(a) for a, _ in alias_map))
    who = {a: k for a, k in alias_map}
    parts = re.split(r"(<[^>]+>)", h)
    depth = {"a": 0, "h": 0, "code": 0, "pre": 0}
    linked: set[str] = set()
    for i, p in enumerate(parts):
        if p.startswith("<"):
            m = re.match(r"<(/?)(\w+)", p)
            if not m:
                continue
            closing, tag = m.group(1) == "/", m.group(2).lower()
            key = "h" if re.fullmatch(r"h[1-6]", tag) else tag
            if key in depth:
                depth[key] += -1 if closing else 1
            if not closing and tag in ("h2", "h3"):
                linked = set()
            continue
        if any(depth.values()) or not p.strip():
            continue

        def sub(m):
            k = who[m.group(0)]
            if k in linked:
                return m.group(0)
            linked.add(k)
            return f'<a class="xref" href="#/doc/artist-{k}" title="아티스트 노트">{m.group(0)}</a>'
        parts[i] = rx.sub(sub, p)
    return "".join(parts)


for d in DOCS:
    render(d)


# ---------------------------------------------------------------- playlist & program from 0927
def table_after(src: str, heading: str) -> list[list[str]]:
    i = src.index(heading)
    rows = []
    started = False
    for line in src[i:].splitlines()[1:]:
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if all(re.fullmatch(r":?-*:?", c) for c in cells) or all(not c for c in cells):
                continue
            rows.append(cells)
        elif started:
            break
    return rows[1:]  # 첫 행은 머리글


def inline(s: str, doc: Doc) -> str:
    fake = Doc.__new__(Doc)
    fake.src, fake.broken, fake.wikilinks, fake.artist, fake.slug = s, [], [], None, doc.slug
    out = md.renderInline(preprocess(fake))
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a target="_blank" rel="noopener" href="\1"', out)
    return out


prog = BY_SLUG["program"]
prog_src = prog.src
PROGRAM = [{"time": r[0], "title": r[1], "songs": inline(r[2], prog)} for r in table_after(prog_src, "## 오늘의 프로그램")]

LINK_MD = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
TRACKS = []
for r in table_after(prog_src, "## 오늘 틀 곡 목록"):
    num, title_md, artist_md, year, genre = r[:5]
    m = LINK_MD.search(title_md)
    title, url = (m.group(1), m.group(2)) if m else (title_md, "")
    TRACKS.append({"n": num, "title": title, "url": url, "artist_md": artist_md,
                   "year": year, "genre": genre})


def track_aliases(title: str) -> list[str]:
    k = norm(title)
    for key, al in TRACK_ALIASES.items():
        if norm(key) == k:
            return al
    return [title]


def mentions(text: str, aliases: list[str]) -> bool:
    t = norm(text)
    return any(norm(a) in t for a in aliases)


def artist_mentions(text: str, a) -> bool:
    return mentions(text, a[6])


ART = {a[0]: a for a in ARTISTS}
for t in TRACKS:
    al = track_aliases(t["title"])
    t["aliases"] = al
    t["hits"] = {}
    for d in DOCS:
        secs = [(sid, head) for sid, head, txt in d.sections if mentions(head + " " + txt, al)]
        if secs:
            t["hits"][d.slug] = secs
    # 아티스트 노트: 플레이리스트 아티스트 칸 + 곡을 언급한 아티스트 문서
    arts = []
    for a in ARTISTS:
        if artist_mentions(re.sub(r"\[\[[^\]]*\]\]", lambda m: m.group(0), t["artist_md"]), a) \
                or f"Artist - {a[1]}" in t["artist_md"]:
            arts.append(a[0])
    for a in ARTISTS:
        if f"artist-{a[0]}" in t["hits"] and a[0] not in arts:
            arts.append(a[0])
    t["artists"] = arts
    # 곡 제목으로 걸린 링크 모으기
    urls = defaultdict(list)
    for d in DOCS:
        for sid, text, href in d.links:
            if href.startswith("http") and mentions(text, al):
                urls[href].append(d.slug)
    t["urls"] = dict(urls)
    t["artist_html"] = inline(t["artist_md"], prog)

# 아티스트별: 언급된 문서·절, 연결된 플레이리스트 곡
for a in ARTISTS:
    pass
ART_MENTIONS = {}
for a in ARTISTS:
    hits = []
    for d in DOCS:
        if d.artist and d.artist[0] == a[0]:
            continue
        secs = [(sid, head) for sid, head, txt in d.sections if artist_mentions(head + " " + txt, a)]
        linked = f"artist-{a[0]}" in d.wikilinks
        if secs or linked:
            hits.append((d.slug, secs, linked))
    ART_MENTIONS[a[0]] = hits

# 백링크 (명시적 위키링크)
BACKLINKS = defaultdict(set)
for d in DOCS:
    for s in d.wikilinks:
        if s != d.slug:
            BACKLINKS[s].add(d.slug)

BROKEN = [(d.slug, b) for d in DOCS for b in d.broken]


# ---------------------------------------------------------------- online check
ONLINE = {}
if "--check-online" in sys.argv:
    watch = sorted({href for d in DOCS for _, _, href in d.links
                    if re.search(r"youtube\.com/watch\?v=|youtu\.be/", href)})
    for u in watch:
        api = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(u, safe="")
        try:
            with urllib.request.urlopen(api, timeout=10) as r:
                ONLINE[u] = ("ok", json.load(r).get("title", ""))
        except Exception as e:  # 404/401 = 삭제·비공개·임베드 불가
            ONLINE[u] = ("dead", str(getattr(e, "code", e)))
    dead = [u for u, (s, _) in ONLINE.items() if s != "ok"]
    print(f"유튜브 watch 링크 {len(watch)}개 확인, 문제 {len(dead)}개")
    for u in dead:
        print("  !", u, ONLINE[u][1])


# ---------------------------------------------------------------- HTML
def sec_label(slug: str, secs) -> str:
    return secs[0][1] if secs else BY_SLUG[slug].label


def best_section(secs):
    """개요표·전체 목록 말고 곡을 실제로 설명하는 절을 고른다."""
    return next((s for s in secs if s[1] and not any(k in s[1] for k in SUMMARY_SECTIONS)), secs[0])


def doc_link(slug, sid=None, text=None, cls="chip"):
    d = BY_SLUG[slug]
    href = f"#/doc/{slug}" + (f"/{sid}" if sid else "")
    return f'<a class="{cls}" href="{href}">{esc(text or d.label)}</a>'


def short(s, n=26):
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= n else s[: n - 1] + "…"


def genre_cls(g):
    for k, v in GENRE_CLASS.items():
        if k in g:
            return v
    return "other"


home = []
intro = prog_src.split("\n\n")
intro_p = next((p for p in intro if p.startswith("브라질 음악은")), "")
# 코파카바나 가을 해질녘: 색은 전부 CSS 변수(--sun, --loaf ...)라 밝게/어둡게 테마를 따라간다
SCENE = """<svg class="scene" viewBox="0 0 1200 360" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
  <defs>
    <radialGradient id="sc-glow"><stop offset="0" class="g0"/><stop offset="1" class="g1"/></radialGradient>
    <pattern id="sc-wave" width="80" height="18" patternUnits="userSpaceOnUse"><rect class="stone" width="80" height="18"/><path class="wv" d="M0 9 Q20 1 40 9 T80 9"/></pattern>
    <path id="sc-leaf" d="M0 0 C4 -6 12 -6 15 0 C12 6 4 6 0 0Z"/>
    <g id="sc-palm"><path class="trunk" d="M0 0 C-4 -40 -14 -80 -30 -116"/>
      <path class="fr" d="M-30 -116 q-40 -20 -74 6 M-30 -116 q-30 4 -50 38 M-30 -116 q30 -26 70 -12 M-30 -116 q38 2 56 36 M-30 -116 q-6 -30 -30 -44 M-30 -116 q16 -30 40 -38"/></g>
  </defs>
  <circle cx="760" cy="266" r="220" fill="url(#sc-glow)"/>
  <circle class="sun" cx="760" cy="262" r="46"/>
  <path class="bird" d="M560 92 q7 -6 14 0 q7 -6 14 0 M604 72 q5 -4 10 0 q5 -4 10 0 M980 118 q6 -5 12 0 q6 -5 12 0"/>
  <path class="far" d="M0 272 V214 C60 196 120 200 170 216 C230 196 300 206 340 228 L380 272Z M880 272 C940 248 1000 240 1060 246 C1120 236 1170 240 1200 248 V272Z"/>
  <path class="mid" d="M0 272 V196 C50 178 110 184 150 208 C190 232 220 254 236 272Z"/>
  <path class="loaf" d="M318 272 C330 222 342 168 372 140 C396 118 432 120 450 146 C468 174 474 224 488 272Z"/>
  <path class="urca" d="M452 272 C468 240 500 218 540 216 C580 216 606 238 628 272Z"/>
  <path class="cable" d="M540 216 L410 126"/><rect class="car" x="471" y="170" width="9" height="7" rx="1.5"/>
  <rect class="sea" x="0" y="270" width="1200" height="34"/>
  <path class="glint" d="M718 278 H802 M734 285 H786 M744 292 H776 M752 298 H768"/>
  <path class="sand" d="M0 300 Q600 288 1200 302 V328 H0Z"/>
  <rect x="0" y="326" width="1200" height="34" fill="url(#sc-wave)"/>
  <g class="palm"><use href="#sc-palm" transform="translate(902 334)"/><use href="#sc-palm" transform="translate(1062 336) scale(.8)"/><use href="#sc-palm" transform="translate(150 336) scale(-.7 .7)"/></g>
  <g transform="translate(612 120) rotate(-20)"><use class="leaf l1" href="#sc-leaf"/></g>
  <g transform="translate(986 70) rotate(30)"><use class="leaf l2" href="#sc-leaf"/></g>
  <g transform="translate(250 120) rotate(60) scale(1.2)"><use class="leaf l3" href="#sc-leaf"/></g>
  <g transform="translate(690 190) rotate(-50) scale(.9)"><use class="leaf l2" href="#sc-leaf"/></g>
  <g transform="translate(1120 140) rotate(10) scale(1.1)"><use class="leaf l1" href="#sc-leaf"/></g>
  <g transform="translate(520 60) rotate(80) scale(.8)"><use class="leaf l3" href="#sc-leaf"/></g>
</svg>"""

home.append(f"""
<header class="hero" id="top">
  <div class="postcard">
    <p class="stamp" aria-hidden="true"><b>Saudade</b><span>Rio · Outono 2026</span></p>
    <p class="eyebrow">Listening Session · Autumn 2026 · Copacabana</p>
    <h1><span class="nw">보사노바·삼바·탱고</span> 감상회</h1>
    <p class="lede">{md.renderInline(intro_p)}</p>
    <div class="hero-meta">
      <span>{len(TRACKS)}곡</span><span>60분</span><span>아티스트 노트 {len(ARTISTS)}편</span>
    </div>
    {SCENE}
  </div>
  <div class="gloss">
    <div><b>Saudade</b><span>사우다지 · 그리움. 멜랑콜리 속의 희망.</span></div>
    <div><b>Syncopation</b><span>싱코페이션 · 당김음. 슬픈데 몸이 흔들리는 이유.</span></div>
    <div><b>3+3+2</b><span>하바네라에서 삼바와 탱고로 갈라진 한 리듬.</span></div>
  </div>
</header>""")

# program
rows = "".join(
    f'<li><span class="t">{esc(p["time"])}</span><div><b>{esc(p["title"])}</b><p>{p["songs"]}</p></div></li>'
    for p in PROGRAM)
home.append(f"""
<section id="program" class="block">
  <div class="block-h"><span class="num">I</span><h2>오늘의 60분</h2>
  <p>곡은 대부분 60~90초 발췌, 곡 사이에 2~3분 해설. 해설 원고는 {doc_link('script', cls='inl')}.</p></div>
  <ol class="timeline">{rows}</ol>
</section>""")

# tracks
cards = []
for t in TRACKS:
    chips = []
    for slug in ("script", "program"):
        if slug in t["hits"]:
            secs = t["hits"][slug]
            target = best_section(secs)
            more = f" +{len(secs) - 1}" if len(secs) > 1 else ""
            chips.append(doc_link(slug, target[0], f'{"해설" if slug == "script" else "프로그램"} · {short(target[1] or BY_SLUG[slug].label, 22)}{more}', "chip doc"))
    for slug in ("latin", "rhythm"):
        if slug in t["hits"]:
            chips.append(doc_link(slug, t["hits"][slug][0][0], BY_SLUG[slug].label, "chip doc"))
    for k in t["artists"]:
        chips.append(doc_link(f"artist-{k}", text=ART[k][2], cls="chip art"))
    if "script" not in t["hits"]:
        chips.append('<span class="chip warn" title="60분 해설 스크립트에 이 곡 이야기가 없음">스크립트에 없음</span>')
    cards.append(f"""
<li class="track g-{genre_cls(t['genre'])}" id="track-{esc(t['n'])}">
  <span class="tn">{esc(t['n']).zfill(2)}</span>
  <div class="tb">
    <h3><a target="_blank" rel="noopener" href="{esc(t['url'])}">{esc(t['title'])}</a></h3>
    <p class="tm">{t['artist_html']} · {esc(t['year'])} · <span class="genre">{esc(t['genre'])}</span></p>
    <div class="chips">{''.join(chips)}</div>
  </div>
  <a class="play" target="_blank" rel="noopener" href="{esc(t['url'])}" aria-label="{esc(t['title'])} 듣기">▶</a>
</li>""")
home.append(f"""
<section id="tracks" class="block">
  <div class="block-h"><span class="num">II</span><h2>오늘 틀 곡</h2>
  <p>제목이나 ▶를 누르면 유튜브로 갑니다. 아래 칩은 이 곡을 다루는 해설 절과 아티스트 노트입니다.</p></div>
  <ol class="tracks">{''.join(cards)}</ol>
</section>""")

# artists
acards = []
for a in ARTISTS:
    k = a[0]
    in_pl = [t for t in TRACKS if k in t["artists"]]
    tags = "".join(f'<a class="mini" href="#/tracks" data-track="{esc(t["n"])}">{esc(t["title"])}</a>' for t in in_pl)
    acards.append(f"""
<li><a class="acard" href="#/doc/artist-{k}">
  <span class="region">{esc(a[4])}</span>
  <b>{esc(a[2])}</b><span class="yrs">{esc(a[3])}</span>
  <p>{esc(a[5])}</p></a>
  <div class="minis">{tags or '<span class="mini none">플레이리스트 밖 · 번외</span>'}</div>
</li>""")
home.append(f"""
<section id="artists" class="block">
  <div class="block-h"><span class="num">III</span><h2>아티스트 노트</h2>
  <p>본문에 이름이 나오면 자동으로 이 노트로 연결됩니다.</p></div>
  <ul class="artists">{''.join(acards)}</ul>
</section>""")

# docs
dcards = "".join(
    f'<li><a class="dcard" href="#/doc/{d.slug}"><b>{esc(d.label)}</b><span class="fn">{esc(d.stem)}.md</span><p>{esc(d.desc)}</p></a></li>'
    for d in DOCS if d.kind == "main")
home.append(f"""
<section id="docs" class="block">
  <div class="block-h"><span class="num">IV</span><h2>문서</h2></div>
  <ul class="docs">{dcards}</ul>
</section>""")

# cross-reference check
cols = [d for d in DOCS if d.kind == "main"]
head = "".join(f"<th>{esc(d.label)}</th>" for d in cols) + "<th>아티스트 노트</th><th>링크</th>"
trs = []
for t in TRACKS:
    tds = []
    for d in cols:
        secs = t["hits"].get(d.slug)
        best = best_section(secs) if secs else None
        tds.append(f'<td class="ok">{doc_link(d.slug, best[0], "✓ " + short(best[1] or "본문", 16), "cell")}'
                   f'{" <small>+" + str(len(secs) - 1) + "</small>" if len(secs) > 1 else ""}</td>' if secs
                   else '<td class="no">—</td>')
    arts = [k for k in t["artists"] if f"artist-{k}" in t["hits"]]
    tds.append("<td>" + (" ".join(doc_link(f"artist-{k}", text=ART[k][2], cls="cell") for k in arts)
                         or '<span class="no">노트에 언급 없음</span>') + "</td>")
    n_urls = len(t["urls"])
    flag = ' class="warn"' if n_urls > 1 else ""
    url_list = "".join(f'<li><a target="_blank" rel="noopener" href="{esc(u)}">{esc(short(urllib.parse.unquote(u.split("//",1)[-1]), 52))}</a> '
                       f'<small>{esc(", ".join(BY_SLUG[s].label for s in sorted(set(ss))))}</small></li>'
                       for u, ss in t["urls"].items())
    tds.append(f'<td{flag}><details><summary>{n_urls}개</summary><ul class="urls">{url_list}</ul></details></td>')
    trs.append(f'<tr><th scope="row">{esc(t["n"])}. {esc(t["title"])}</th>{"".join(tds)}</tr>')

orphan_artists = [a for a in ARTISTS if not any(a[0] in t["artists"] for t in TRACKS)]
dead_html = ""
if ONLINE:
    dead = [(u, v) for u, v in ONLINE.items() if v[0] != "ok"]
    dead_html = (f"<p>유튜브 영상 링크 {len(ONLINE)}개 확인 · 문제 {len(dead)}개</p>"
                 + ("<ul>" + "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a> ({esc(v[1])})</li>' for u, v in dead) + "</ul>" if dead else ""))
broken_html = ("<ul>" + "".join(f"<li>{esc(BY_SLUG[s].label)}: [[{esc(b)}]]</li>" for s, b in BROKEN) + "</ul>") if BROKEN else "<p>깨진 위키링크 없음.</p>"

home.append(f"""
<section id="check" class="block">
  <div class="block-h"><span class="num">V</span><h2>연결 점검</h2>
  <p>플레이리스트 각 곡이 어느 문서의 어느 절에서 다뤄지는지 빌드할 때 자동으로 찾은 결과입니다. —는 그 문서에 곡 이름이 없다는 뜻이고,
  '링크'가 2개 이상이면 문서마다 다른 유튜브 주소를 쓰고 있다는 뜻입니다.</p></div>
  <div class="tw"><table class="xtab"><thead><tr><th>곡</th>{head}</tr></thead><tbody>{''.join(trs)}</tbody></table></div>
  <div class="notes">
    <div><h3>플레이리스트에 곡이 없는 아티스트 노트</h3><p>{' · '.join(doc_link('artist-' + a[0], text=a[2], cls='inl') for a in orphan_artists) or '없음'}</p>
    <p class="muted">해설 스크립트나 보충 리스트에서만 쓰이는 노트입니다.</p></div>
    <div><h3>위키링크</h3>{broken_html}{dead_html}</div>
  </div>
</section>""")

# doc views
views = []
for d in DOCS:
    toc = "".join(f'<li class="l{lvl}"><a href="#/doc/{d.slug}/{sid}">{esc(short(text, 40))}</a></li>'
                  for lvl, sid, text in d.toc if lvl <= 3)
    side = []
    if d.kind == "artist":
        k = d.artist[0]
        pl = [t for t in TRACKS if k in t["artists"]]
        if pl:
            side.append("<h4>플레이리스트 속 곡</h4><ul>" + "".join(
                f'<li><a target="_blank" rel="noopener" href="{esc(t["url"])}">{esc(t["n"])}. {esc(t["title"])}</a></li>' for t in pl) + "</ul>")
        ment = ART_MENTIONS[k]
        if ment:
            items = []
            for slug, secs, _ in ment:
                if secs:
                    items.extend(f"<li>{doc_link(slug, sid, BY_SLUG[slug].label + ' · ' + short(h or '본문', 24), 'plain')}</li>" for sid, h in secs[:4])
                else:
                    items.append(f"<li>{doc_link(slug, cls='plain')}</li>")
            side.append("<h4>이 아티스트가 나오는 곳</h4><ul>" + "".join(items) + "</ul>")
    bl = sorted(BACKLINKS.get(d.slug, []), key=lambda s: [x.slug for x in DOCS].index(s))
    if bl:
        side.append("<h4>이 문서를 링크한 문서</h4><ul>" + "".join(f"<li>{doc_link(s, cls='plain')}</li>" for s in bl) + "</ul>")
    kind = "아티스트 노트" if d.kind == "artist" else "문서"
    title = f"{d.artist[2]} <small>{esc(d.artist[3])}</small>" if d.kind == "artist" else esc(d.label)
    views.append(f"""
<article class="view docview" data-view="doc/{d.slug}" hidden>
  <div class="crumbs"><a href="#/">홈</a> / <a href="#/{'artists' if d.kind == 'artist' else 'docs'}">{kind}</a></div>
  <header class="doc-h"><h1>{title}</h1><p class="fn">{esc(d.stem)}.md</p></header>
  <div class="doc-grid">
    <aside class="toc">{'<details open><summary>목차</summary><ul>' + toc + '</ul></details>' if toc else ''}</aside>
    <div class="prose">{d.html}</div>
    <aside class="side">{''.join(side)}</aside>
  </div>
</article>""")

CSS = r"""
/* 레이아웃: 상단 고정 메뉴 + 한 열 홈(타임라인→곡→아티스트→문서→점검), 문서는 목차·본문·연결 3열
   색: 코파카바나의 가을 해질녘(모래색 바탕, 바다색 강조, 테라코타 보조). 기본은 밝은 테마,
   ◐ 버튼으로만 '해 진 뒤' 테마로 바뀐다(OS 다크모드를 따라가지 않음) */
:root{
  --bg:#f6efe3; --paper:#fffaf2; --ink:#2b211a; --muted:#6f6052; --line:#e5d7c2;
  --accent:#1d6766; --accent-2:#a14b1c; --accent-soft:#e0ebe5; --warm-soft:#f6e0c4;
  --samba:#a14b1c; --bossa:#1d6766; --habanera:#7a4a7e; --tango:#9b2f35; --other:#6f6052;
  --shadow:0 1px 0 rgba(60,35,15,.05),0 8px 24px -14px rgba(60,35,15,.4);
  --sky1:#fdf4e6; --sky2:#f9dcb9; --sky3:#f1b688; --sun:#fff3d6; --glow:#ffcf8f;
  --far:#e9c2a2; --mid:#c99682; --loaf:#7e5a50; --urca:#94695c; --sea:#4f8f8c; --sand:#ecd1a8;
  --stone:#f7efe3; --wave:#3a2b23; --palm:#3a2a21; --leaf1:#c45f24; --leaf2:#de9a36; --leaf3:#963c1c;
  --serif:"Noto Serif KR","Iowan Old Style",Georgia,serif;
  --sans:"Noto Sans KR",-apple-system,"Segoe UI","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  color-scheme:light;
}
:root[data-theme="dark"]{
  --bg:#241b19; --paper:#2f2421; --ink:#f3e7d8; --muted:#c3b09d; --line:#4a3a33;
  --accent:#79cbbf; --accent-2:#f0a463; --accent-soft:#273633; --warm-soft:#45301f;
  --samba:#f0a463; --bossa:#79cbbf; --habanera:#d4a6dc; --tango:#f08b8f; --other:#c3b09d;
  --shadow:0 1px 0 rgba(0,0,0,.25),0 8px 24px -14px rgba(0,0,0,.7);
  --sky1:#2b2135; --sky2:#583848; --sky3:#b4654a; --sun:#ffd79a; --glow:#f39a5c;
  --far:#6e4756; --mid:#553646; --loaf:#352232; --urca:#41293a; --sea:#36575d; --sand:#7d5d48;
  --stone:#5b4a40; --wave:#1c1411; --palm:#1b1216; --leaf1:#d9733a; --leaf2:#e8a94a; --leaf3:#b0502a;
  color-scheme:dark;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 var(--sans);-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:3px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:8px;z-index:99;background:var(--paper);padding:6px 10px}
nav.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav.top .in{max-width:1180px;margin:0 auto;padding:10px 16px;display:flex;gap:6px;align-items:center;overflow-x:auto;scrollbar-width:none}
nav.top .brand{font-family:var(--serif);font-weight:700;margin-right:10px;white-space:nowrap;color:var(--ink);text-decoration:none}
nav.top a.n{white-space:nowrap;color:var(--muted);text-decoration:none;font-size:14px;padding:4px 10px;border-radius:99px}
nav.top a.n:hover,nav.top a.n.on{background:var(--accent-soft);color:var(--accent)}
nav.top button{margin-left:auto;border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:99px;padding:3px 10px;cursor:pointer;font:inherit;font-size:13px}
main{max-width:1180px;margin:0 auto;padding:0 16px 80px}
.hero{padding:24px 0 8px}
.postcard{--scene-h:clamp(170px,30vw,320px);position:relative;isolation:isolate;overflow:hidden;border-radius:22px;padding:44px clamp(20px,5vw,56px) calc(var(--scene-h) + 8px);background:linear-gradient(180deg,var(--sky1),var(--sky2) 62%,var(--sky3));box-shadow:var(--shadow);margin-bottom:16px}
.postcard .scene{position:absolute;left:0;bottom:0;width:100%;height:var(--scene-h);z-index:-1}
.postcard .lede{max-width:720px}
.postcard .hero-meta span{background:color-mix(in srgb,var(--paper) 72%,transparent);border-color:color-mix(in srgb,var(--ink) 15%,transparent);color:var(--ink)}
.stamp{position:absolute;top:22px;right:24px;margin:0;transform:rotate(4deg);border:2px dashed color-mix(in srgb,var(--accent-2) 70%,transparent);border-radius:6px;padding:8px 14px;text-align:center;color:var(--accent-2);background:color-mix(in srgb,var(--paper) 45%,transparent)}
.stamp b{display:block;font-family:var(--serif);font-style:italic;font-size:22px;line-height:1.2}
.stamp span{font-size:11px;letter-spacing:.14em;text-transform:uppercase}
@media (max-width:1000px){.stamp{display:none}}
.scene .g0{stop-color:var(--glow);stop-opacity:.75}.scene .g1{stop-color:var(--glow);stop-opacity:0}
.scene .sun{fill:var(--sun)}.scene .far{fill:var(--far)}.scene .mid{fill:var(--mid)}
.scene .loaf{fill:var(--loaf)}.scene .urca{fill:var(--urca)}.scene .sea{fill:var(--sea)}.scene .sand{fill:var(--sand)}
.scene .cable{stroke:var(--loaf);stroke-width:1.2;fill:none}.scene .car{fill:var(--leaf1)}
.scene .glint{stroke:var(--sun);stroke-width:2.5;stroke-linecap:round;opacity:.8}
.scene .stone{fill:var(--stone)}.scene .wv{fill:none;stroke:var(--wave);stroke-width:5}
.scene .palm{fill:none;stroke:var(--palm);stroke-linecap:round}.scene .trunk{stroke-width:10}.scene .fr{stroke-width:6.5}
.scene .bird{fill:none;stroke:var(--palm);stroke-width:2;stroke-linecap:round;opacity:.7}
.scene .leaf{transform-box:fill-box;transform-origin:center;animation:sway 6s ease-in-out infinite alternate}
.scene .l1{fill:var(--leaf1)}.scene .l2{fill:var(--leaf2);animation-duration:7.5s}.scene .l3{fill:var(--leaf3);animation-duration:5s}
@keyframes sway{from{transform:translateY(-3px) rotate(-14deg)}to{transform:translateY(5px) rotate(16deg)}}
.calcadao{margin-top:56px;height:30px;background:var(--wave);opacity:.55;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='30'%3E%3Cpath d='M0 9 Q24 -3 48 9 T96 9 V21 Q72 33 48 21 T0 21Z'/%3E%3C/svg%3E") repeat-x 0 0/96px 30px;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='30'%3E%3Cpath d='M0 9 Q24 -3 48 9 T96 9 V21 Q72 33 48 21 T0 21Z'/%3E%3C/svg%3E") repeat-x 0 0/96px 30px}
.hero h1,.block-h h2,.doc-h h1{text-wrap:balance}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.scene .leaf{animation:none}}
.eyebrow{letter-spacing:.18em;text-transform:uppercase;font-size:12px;color:var(--accent-2);margin:0 0 8px}
.hero h1 .nw{white-space:nowrap}
.hero h1{word-break:keep-all;font-family:var(--serif);font-size:clamp(28px,6vw,58px);line-height:1.15;margin:0 0 16px;letter-spacing:-.01em}
.lede{max-width:760px;font-size:18px;color:var(--ink);margin:0 0 18px}
.hero-meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px}
.hero-meta span{border:1px solid var(--line);border-radius:99px;padding:2px 12px;font-size:13px;color:var(--muted);background:var(--paper)}
.gloss{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.gloss div{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:14px 16px;box-shadow:var(--shadow)}
.gloss b{display:block;font-family:var(--serif);font-size:20px;color:var(--accent)}
.gloss span{font-size:14px;color:var(--muted)}
.block{padding:48px 0 8px}
.block-h{display:grid;grid-template-columns:auto 1fr;column-gap:14px;align-items:baseline;margin-bottom:18px}
.block-h .num{font-family:var(--serif);color:var(--accent-2);font-size:18px}
.block-h h2{font-family:var(--serif);font-size:clamp(24px,3.4vw,32px);margin:0}
.block-h p{grid-column:2;margin:4px 0 0;color:var(--muted);max-width:760px}
.timeline{list-style:none;margin:0;padding:0;border-left:2px solid var(--line)}
.timeline li{display:grid;grid-template-columns:64px 1fr;gap:12px;padding:10px 0 10px 16px;position:relative}
.timeline li::before{content:"";position:absolute;left:-7px;top:19px;width:12px;height:12px;border-radius:50%;background:var(--paper);border:2px solid var(--accent)}
.timeline .t{font-variant-numeric:tabular-nums;color:var(--accent-2);font-weight:700}
.timeline b{font-family:var(--serif);font-size:18px}
.timeline p{margin:2px 0 0;color:var(--muted)}
.tracks{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.track{display:grid;grid-template-columns:48px 1fr 44px;gap:14px;align-items:start;background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--c,var(--other));border-radius:14px;padding:14px 16px;box-shadow:var(--shadow);transition:outline-color .3s}
.track.flash{outline:3px solid var(--accent-2);outline-offset:2px}
.g-samba{--c:var(--samba)}.g-bossa{--c:var(--bossa)}.g-habanera{--c:var(--habanera)}.g-tango{--c:var(--tango)}
.tb{min-width:0}
.tn{font-family:var(--serif);font-size:26px;color:var(--c);line-height:1.2}
.track h3{margin:0;font-family:var(--serif);font-size:20px;line-height:1.35}
.track h3 a{color:var(--ink);text-decoration:none}.track h3 a:hover{color:var(--accent)}
.tm{margin:2px 0 8px;color:var(--muted);font-size:14px}
.genre{color:var(--c);font-weight:600}
.play{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--c);color:var(--paper);text-decoration:none;font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12.5px;line-height:1.4;padding:3px 10px;border-radius:99px;text-decoration:none;border:1px solid var(--line);color:var(--ink);background:var(--bg)}
.chip.doc{background:var(--accent-soft);border-color:transparent;color:var(--accent)}
.chip.art{background:var(--warm-soft);border-color:transparent;color:var(--accent-2)}
.chip.warn{background:transparent;border-style:dashed;color:var(--muted)}
.chip:hover{filter:brightness(.96)}
.artists{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.artists li{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);display:flex;flex-direction:column}
.acard{display:block;min-width:0;overflow-wrap:anywhere;padding:16px 16px 8px;color:var(--ink);text-decoration:none;flex:1}
.acard:hover b{color:var(--accent)}
.acard .region{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent-2)}
.acard b{display:block;font-family:var(--serif);font-size:20px;margin-top:2px}
.acard .yrs{font-size:13px;color:var(--muted)}
.acard p{margin:6px 0 0;font-size:14px;color:var(--muted)}
.minis{display:flex;flex-wrap:wrap;gap:4px;padding:0 16px 14px}
.mini{font-size:12px;padding:1px 8px;border-radius:99px;background:var(--bg);border:1px solid var(--line);color:var(--ink);text-decoration:none}
.mini.none{color:var(--muted);border-style:dashed}
.docs{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.dcard{display:block;height:100%;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px;color:var(--ink);text-decoration:none;box-shadow:var(--shadow)}
.dcard b{font-family:var(--serif);font-size:19px}.dcard:hover b{color:var(--accent)}
.dcard .fn{display:block;font-size:12px;color:var(--muted);word-break:break-all}
.dcard p{margin:8px 0 0;font-size:14px;color:var(--muted)}
.tw{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:12px;background:var(--paper)}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{padding:8px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
thead th{background:var(--bg);font-weight:600;white-space:nowrap}
tbody tr:last-child>*{border-bottom:0}
.xtab th[scope=row]{font-family:var(--serif);font-weight:600;white-space:nowrap}
.xtab td.no,.no{color:var(--muted)}
.xtab td.warn summary{color:var(--accent-2);font-weight:600}
.cell{font-size:13px;text-decoration:none;white-space:nowrap}
.urls{margin:6px 0 0;padding-left:16px;font-size:12.5px;min-width:320px}
.notes{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:16px}
.notes>div{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.notes h3{margin:0 0 6px;font-size:16px}
.muted{color:var(--muted);font-size:14px}
.inl{font-weight:600}
/* doc view */
.crumbs{padding:20px 0 0;font-size:13px;color:var(--muted)}.crumbs a{color:var(--muted)}
.doc-h{padding:6px 0 18px;border-bottom:1px solid var(--line);margin-bottom:24px}
.doc-h h1{font-family:var(--serif);font-size:clamp(28px,4.6vw,44px);margin:0;line-height:1.2}
.doc-h h1 small{font-size:.5em;color:var(--muted);font-weight:400}
.doc-h .fn{margin:4px 0 0;font-size:12px;color:var(--muted)}
.doc-grid{display:grid;grid-template-columns:220px minmax(0,1fr) 230px;gap:36px;align-items:start}
.toc,.side{position:sticky;top:72px;max-height:calc(100vh - 90px);overflow:auto;font-size:13.5px}
.toc ul,.side ul{list-style:none;margin:0;padding:0}
.toc li{margin:2px 0}.toc li.l3{padding-left:12px}
.toc a,.side a{color:var(--muted);text-decoration:none;display:block;padding:2px 0;line-height:1.45}
.toc a:hover,.side a:hover{color:var(--accent)}
.toc summary{font-weight:600;cursor:pointer;margin-bottom:6px}
.side h4{margin:0 0 6px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-2)}
.side ul{margin-bottom:20px}
.prose{min-width:0;max-width:760px}
.prose h1{font-family:var(--serif);font-size:30px;margin:8px 0 12px}
.prose h2{font-family:var(--serif);font-size:25px;margin:40px 0 10px;padding-top:6px;border-top:1px solid var(--line)}
.prose h3{font-family:var(--serif);font-size:20px;margin:28px 0 8px}
.prose h4{font-size:17px;margin:22px 0 6px}
.prose blockquote{margin:14px 0;padding:10px 16px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 10px 10px 0}
.prose blockquote p{margin:0}
.prose pre{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px;overflow-x:auto;font-size:13.5px;line-height:1.6}
.prose code{font-family:ui-monospace,"D2Coding",Consolas,monospace}
.prose hr{border:0;border-top:1px dashed var(--line);margin:28px 0}
.prose li{margin:3px 0}
.prose mark{background:var(--warm-soft);color:inherit;padding:0 2px}
.prose a.yt::after{content:" ▶";font-size:.72em;color:var(--accent-2)}
.prose a.wl{font-weight:600;background:var(--accent-soft);padding:0 4px;border-radius:4px;text-decoration:none}
.prose a.xref{color:inherit;text-decoration:underline dotted var(--accent);text-decoration-thickness:1.5px}
.prose a.xref:hover{color:var(--accent)}
.broken{color:#b33;text-decoration:line-through}
section[id],h2[id],h3[id],h4[id]{scroll-margin-top:72px}
footer{padding:20px 16px;text-align:center;color:var(--muted);font-size:13px}
@media (max-width:1060px){.doc-grid{grid-template-columns:minmax(0,1fr) 220px}.toc{display:none}}
@media (max-width:760px){
  .doc-grid{grid-template-columns:1fr;gap:16px}.side{position:static;max-height:none;order:2;border-top:1px solid var(--line);padding-top:16px}
  .track{grid-template-columns:34px 1fr;padding:12px}.play{display:none}.tn{font-size:20px}
  .timeline li{grid-template-columns:52px 1fr}
  .block-h{grid-template-columns:1fr}.block-h p{grid-column:1}.block-h .num{display:none}
}
@media print{nav.top,.toc,.side,.play{display:none}.doc-grid{display:block}body{background:#fff}}
"""

JS = r"""
(function(){
  const views=[...document.querySelectorAll('.view')];
  const navs=[...document.querySelectorAll('nav.top a.n')];
  function show(name){views.forEach(v=>v.hidden=v.dataset.view!==name);}
  function route(){
    let h=decodeURIComponent(location.hash||'');
    if(h && !h.startsWith('#/')) h='#/'+h.slice(1);         // #tracks → #/tracks
    const p=h.replace(/^#\/?/,'').split('/').filter(Boolean);
    let target=null;
    if(p[0]==='doc' && document.querySelector('[data-view="doc/'+p[1]+'"]')){
      show('doc/'+p[1]); target=p[2]?document.getElementById(p[2]):null;
      document.title=(document.querySelector('[data-view="doc/'+p[1]+'"] h1')||{}).textContent+' · 보사노바·삼바·탱고';
      if(!target) window.scrollTo(0,0);
    }else{
      show('home'); document.title='보사노바·삼바·탱고 감상회';
      target=p[0]?document.getElementById(p[0]):null;
      if(!target) window.scrollTo(0,0);
    }
    navs.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#/'+(p[0]==='doc'?'docs':p[0]||'')));
    if(target) requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));
  }
  addEventListener('hashchange',route); route();
  // 아티스트 카드의 곡 태그 → 해당 곡 카드 강조
  document.addEventListener('click',e=>{
    const m=e.target.closest('.mini[data-track]'); if(!m) return;
    e.preventDefault(); const el=document.getElementById('track-'+m.dataset.track);
    if(location.hash!=='#/tracks') history.pushState(null,'','#/tracks');
    show('home'); el.scrollIntoView({block:'center'}); el.classList.add('flash'); setTimeout(()=>el.classList.remove('flash'),1400);
  });
  const btn=document.getElementById('theme');
  try{const t=localStorage.getItem('bn-theme'); if(t) document.documentElement.dataset.theme=t;}catch(e){}
  btn.addEventListener('click',()=>{
    const cur=document.documentElement.dataset.theme==='dark'?'dark':'light';
    const next=cur==='dark'?'light':'dark'; document.documentElement.dataset.theme=next;
    try{localStorage.setItem('bn-theme',next);}catch(e){}
  });
})();
"""

page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>보사노바·삼바·탱고 감상회</title>
<meta name="description" content="보사노바·삼바·탱고 60분 감상회: 플레이리스트, 해설 스크립트, 아티스트 노트를 서로 연결한 페이지">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&family=Noto+Serif+KR:wght@500;700&display=swap" rel="stylesheet">
<meta name="theme-color" content="#f6efe3">
<script>try{{var t=localStorage.getItem('bn-theme');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">본문으로 바로가기</a>
<nav class="top" aria-label="주 메뉴"><div class="in">
  <a class="brand" href="#/">Bossa · Samba · Tango</a>
  <a class="n" href="#/program">60분</a>
  <a class="n" href="#/tracks">오늘 틀 곡</a>
  <a class="n" href="#/artists">아티스트</a>
  <a class="n" href="#/docs">문서</a>
  <a class="n" href="#/check">연결 점검</a>
  <button id="theme" type="button" aria-label="밝게/어둡게 전환">◐</button>
</div></nav>
<main id="main">
<div class="view" data-view="home">{''.join(home)}</div>
{''.join(views)}
</main>
<div class="calcadao" aria-hidden="true" title="코파카바나 보도 물결무늬"></div>
<footer>02_music 폴더의 md 문서로 생성 · <code>python build_site.py</code>로 다시 만들 수 있습니다 · <a href="#top" onclick="scrollTo(0,0)">처음으로 ↑</a></footer>
<script>{JS}</script>
</body>
</html>
"""
OUT.write_text(page, encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- console report
print(f"→ {OUT.name} ({OUT.stat().st_size // 1024} KB), 문서 {len(DOCS)}개, 곡 {len(TRACKS)}개")
for t in TRACKS:
    where = ", ".join(BY_SLUG[s].label for s in t["hits"] if not s.startswith("artist-"))
    arts = ", ".join(ART[k][2] for k in t["artists"])
    print(f"  {t['n']:>2}. {t['title']:<24} 문서: {where or '-'} | 아티스트: {arts or '-'} | 링크 {len(t['urls'])}개")
if BROKEN:
    print("! 깨진 위키링크:", BROKEN)
print("플레이리스트 밖 아티스트 노트:", ", ".join(a[2] for a in orphan_artists) or "없음")
