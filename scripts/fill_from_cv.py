#!/usr/bin/env python3
"""用途：把 career-ops 的 cv.md 填進 academicpages 模板（鼠大哥 2026-11-26 選 A）。2026-11-26 鼠管家。
在 academicpages 的 checkout 根目錄執行：python3 scripts/fill_from_cv.py
會：改 _config.yml 個人資料；重寫 about、cv、media 頁；清掉模板範例，產生 _publications、_talks；改導覽列。
不公開：電話、推薦人聯絡方式、TOEFL。照片放 images/profile.jpg（有才用）。"""
import os, re, glob, shutil

CV = os.path.expanduser("~/Projects/career-ops/cv.md")
ROOT = os.getcwd()
SCHOLAR = os.environ.get("SCHOLAR_URL", "")


def secs(raw):
    out = {}
    for ch in re.split(r"\n## ", raw)[1:]:
        t, _, b = ch.partition("\n"); out[t.strip()] = b.strip("\n")
    return out


def bullets(b):
    items = []
    for ln in b.splitlines():
        if re.match(r"^\s*- ", ln): items.append(re.sub(r"^\s*- ", "", ln).strip())
        elif items and ln.startswith("  ") and ln.strip(): items[-1] += " " + ln.strip()
    return items


def slug(s, n=50):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n].strip("-")


def yq(s):  # YAML 單引號字串
    return "'" + s.replace("'", "''") + "'"


def strip_md(s):
    return re.sub(r"\*+", "", s).strip()


raw = open(CV, encoding="utf-8").read()
S = secs(raw)
head = raw.split("\n## ")[0]
name = re.search(r"^# (.+)$", head, re.M).group(1).strip()
tagline = (re.search(r"^\*\*(.+?)\*\*\s*$", head, re.M) or [None, ""])[1]

# ---- _config.yml
cfg = open("_config.yml", encoding="utf-8").read()
def setk(key, val, indent=""):
    global cfg
    cfg = re.sub(rf"(?m)^{indent}{re.escape(key)}(\s*):.*$", lambda m: f"{indent}{key}{m.group(1)}: {val}", cfg, count=1)
setk("title", f'"{name}"'); setk("name", f'&name "{name}"')
setk("description", f'&description "{tagline}"'); setk("url", "https://hltiunn.github.io"); setk("repository", '"hltiunn/hltiunn.github.io"')
for k, v in [("avatar", '"profile.jpg"' if os.path.exists("images/profile.jpg") else '""'), ("name", f'"{name}"'),
             ("bio", '"Health workforce and national security policy researcher"'), ("location", '"Washington, DC & Taipei"'),
             ("employer", '"George Washington University; DSET"'), ("email", '"hltiunnn@gmail.com"'),
             ("googlescholar", f'"{SCHOLAR}"' if SCHOLAR else ""), ("orcid", ""), ("pubmed", ""), ("github", '"hltiunn"'),
             ("linkedin", '"hltiunn"'), ("bluesky", "")]:
    setk(k, v, "  ")
open("_config.yml", "w", encoding="utf-8").write(cfg)

# ---- 清掉範例
for d in ("_posts", "_portfolio", "_teaching", "_publications", "_talks", "_drafts"):
    for f in glob.glob(f"{d}/*"):
        os.remove(f) if os.path.isfile(f) else shutil.rmtree(f)
for f in ("_pages/markdown.md", "_pages/non-menu-page.md", "_pages/archive-layout-with-content.md", "_pages/terms.md"):
    if os.path.exists(f): os.remove(f)
for f in glob.glob("files/*"):
    if os.path.isfile(f): os.remove(f)

# ---- publications
def add_pub(item, category):
    y = (re.search(r"\((\d{4})[^)]*\)", item) or [None, "2000"])[1]
    title = (re.search(r"\(\d{4}[^)]*\)\.\s*(.+?)[.?](\s|\*)", item) or [None, strip_md(item)[:90]])[1]
    venue = (re.search(r"\*([^*]+?)\*", item.split(title, 1)[-1]) or [None, ""])[1].rstrip(".")
    first = "(first author)" in item or item.startswith("Tiunn")
    cit = re.sub(r"\*\(first author\)\*", "", item).strip()
    cit = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", cit)
    cit = re.sub(r"\b(Tiunn, H-L\.|Chang, H\. L\.)", r"<b>\1</b>", cit)
    fn = f"_publications/{y}-01-01-{slug(title)}.md"
    open(fn, "w", encoding="utf-8").write(f"""---
title: {yq(strip_md(title))}
collection: publications
category: {category}
permalink: /publication/{y}-{slug(title)}
date: {y}-01-01
venue: {yq(venue)}
citation: {yq(cit)}
---
{"First-authored." if first else ""}
""")

for it in bullets(S.get("Peer-Reviewed Articles", "")): add_pub(it, "manuscripts")
for it in bullets(S.get("Book Chapters", "")): add_pub(it, "books")
for it in bullets(S.get("Policy Reports & Briefings", "")) + bullets(S.get("Op-Eds & Commentary", "")): add_pub(it, "reports")

# ---- talks
for it in bullets(S.get("Conference Presentations", "")):
    y = (re.search(r"\((\d{4})\)", it) or [None, "2000"])[1]
    title = (re.search(r"\(\d{4}\)\.\s*(.+?)\.\s*\*", it) or [None, strip_md(it)[:90]])[1]
    venue = (re.search(r"\*([^*]+?)\.?\*", it.split(title, 1)[-1]) or [None, ""])[1]
    loc = it.split("*")[-1].strip(" ,.") if it.count("*") >= 2 else ""
    open(f"_talks/{y}-01-01-{slug(title)}.md", "w", encoding="utf-8").write(f"""---
title: {yq(strip_md(title))}
collection: talks
type: "Conference presentation"
permalink: /talks/{y}-{slug(title)}
venue: {yq(venue)}
date: {y}-01-01
location: {yq(loc)}
---
""")
for it in bullets(S.get("Invited Talks & Briefings", "")):
    org, _, what = it.partition(" — ")
    open(f"_talks/2025-06-01-{slug(org + ' ' + what)}.md", "w", encoding="utf-8").write(f"""---
title: {yq(strip_md(what) or strip_md(org))}
collection: talks
type: "Invited talk"
permalink: /talks/invited-{slug(org + ' ' + what)}
venue: {yq(strip_md(org))}
date: 2025-06-01
location: ""
---
""")

# ---- about
prof = S.get("Profile", "").strip()
interests = S.get("Research Interests", "").strip()
cross = S.get("Cross-Domain Integration", "").strip()
media = bullets(S.get("Selected Media Coverage", ""))
open("_pages/about.md", "w", encoding="utf-8").write(f"""---
permalink: /
title: "About"
author_profile: true
redirect_from:
  - /about/
  - /about.html
---

{prof}

Research interests
------
{interests}

One method, two critical systems
------
{cross}

Highlights
------
- Lead author of *Drones for Democracy* (DSET, 2025), cited by Bloomberg, The Economist, Deutsche Welle, Al Jazeera and Nikkei Asia.
- First-authored work in *Health Affairs Scholar* on the enhanced Nurse Licensure Compact; co-author in *JAMA Network Open* (2025).
- Dissertation on nurse collective bargaining agreements, defended November 2026 at George Washington University.
- IVLP Fellow, U.S. Department of State; former Board of Directors member, AcademyHealth.
""")

# ---- media
rows = []
for m in media:
    mm = re.match(r"(.+?) \(([\d-]+)\)\. \"(.+?)\"", m)
    rows.append(f"| {mm.group(1)} | {mm.group(3)} | {mm.group(2)} |" if mm else f"| {strip_md(m)} | | |")
open("_pages/media.md", "w", encoding="utf-8").write("""---
layout: archive
title: "Media"
permalink: /media/
author_profile: true
---

| Outlet | Story | Date |
|---|---|---|
""" + "\n".join(rows) + "\n")

# ---- CV（全文，去掉不公開項）
keep = [t for t in S if t not in ("References",)]
cvbody = []
for t in keep:
    b = re.sub(r"(?m)^TOEFL.*$", "", S[t]).strip()
    cvbody.append(f"{t}\n======\n{b}\n")
open("_pages/cv.md", "w", encoding="utf-8").write("""---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

""" + "\n".join(cvbody) + "\nReferences available on request.\n")

# ---- 導覽列
open("_data/navigation.yml", "w", encoding="utf-8").write("""main:
  - title: "Publications"
    url: /publications/
  - title: "Talks"
    url: /talks/
  - title: "Media"
    url: /media/
  - title: "CV"
    url: /cv/
""")
print("filled from", CV)
