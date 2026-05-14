"""Parse Vivek's ai-fluency-assessment.html and extract the per-skill,
per-level proficiency descriptions. Writes JSON for ontology merge.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "luda_vivek_may10" / "aa7c1888_3_ai-fluency-assessment.html"
OUT = ROOT / "docs" / "vivek_proficiency_descriptions.json"

html = SRC.read_text(encoding="utf-8", errors="replace")

# Find the JS object literal containing SK.PRM.003 (and all others)
anchor = html.find("'SK.PRM.003':[")
if anchor < 0:
    raise SystemExit("anchor not found")
open_brace = html.rfind("{", 0, anchor)
depth = 0
end = open_brace
for i in range(open_brace, len(html)):
    if html[i] == "{":
        depth += 1
    elif html[i] == "}":
        depth -= 1
    if depth == 0:
        end = i
        break
obj_text = html[open_brace : end + 1]


def parse_quoted_list(arr_text: str) -> list[str]:
    """Pull out single-quoted strings from a JS array literal body."""
    out = []
    i = 0
    n = len(arr_text)
    while i < n:
        if arr_text[i] == "'":
            j = i + 1
            buf = []
            while j < n:
                if arr_text[j] == "\\" and j + 1 < n:
                    buf.append(arr_text[j + 1])
                    j += 2
                    continue
                if arr_text[j] == "'":
                    break
                buf.append(arr_text[j])
                j += 1
            out.append("".join(buf))
            i = j + 1
        else:
            i += 1
    return out


# Walk the object: find each "'SK.XXX.NNN':[...]" entry
skills: dict[str, list[str]] = {}
pos = 0
key_re = re.compile(r"'(SK\.[A-Z]+\.\d+)'\s*:\s*\[")
while True:
    m = key_re.search(obj_text, pos)
    if not m:
        break
    sid = m.group(1)
    # Walk until matching ]
    start = m.end()
    depth_b = 1
    j = start
    while j < len(obj_text) and depth_b > 0:
        ch = obj_text[j]
        if ch == "[":
            depth_b += 1
        elif ch == "]":
            depth_b -= 1
        elif ch == "'":  # skip quoted string body
            j += 1
            while j < len(obj_text):
                if obj_text[j] == "\\":
                    j += 2
                    continue
                if obj_text[j] == "'":
                    break
                j += 1
        j += 1
    arr_body = obj_text[start : j - 1]
    levels = parse_quoted_list(arr_body)
    if levels:
        skills[sid] = levels
    pos = j

with_six = sum(1 for v in skills.values() if len(v) == 6)
other = {k: len(v) for k, v in skills.items() if len(v) != 6}
print(f"Total skills extracted: {len(skills)}")
print(f"With exactly 6 levels:  {with_six}")
if other:
    print(f"Non-6-level entries (need review): {other}")
print()

print("Sample SK.PRM.003:")
for i, d in enumerate(skills.get("SK.PRM.003", [])):
    print(f"  L{i}: {d}")

OUT.write_text(json.dumps(skills, indent=2), encoding="utf-8")
print(f"\nSaved {len(skills)} skills to {OUT.relative_to(ROOT)}")
