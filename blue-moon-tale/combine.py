#!/usr/bin/env python3
"""Join drafts/day-1.md … day-5.md into 06-full-draft.md and print word counts."""
import re, pathlib

here = pathlib.Path(__file__).parent
days = sorted(here.glob("drafts/day-*.md"), key=lambda p: int(re.search(r"\d+", p.stem).group()))

def body(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)           # drop instructions
    text = re.sub(r"^#.*$", "", text, flags=re.M)                 # drop headings
    return text.strip()

def words(text):
    return len(re.findall(r"\b[\w'’-]+\b", text))

parts, total = [], 0
for p in days:
    t = body(p)
    n = words(t)
    total += n
    parts.append(t)
    print(f"{p.name:12} {n:5} words   running total {total:5}")
print(f"{'TOTAL':12} {total:5} words   (target 5,000)")

out = here / "06-full-draft.md"
out.write_text("# Blue Moon Tale — full draft\n\n" + "\n\n* * *\n\n".join(parts) + "\n", encoding="utf-8")
print(f"written {out.name}")
