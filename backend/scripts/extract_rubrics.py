"""Extract rubric_by_level from Vivek's ontology HTML and merge into ontology.json."""
import re
import json

# Read HTML
with open('../docs/vivek_response/AI Fluency Assessment — GenAI Skills Ontology v2.0 (1).html', 'r', encoding='utf-8') as f:
    html = f.read()

# Get script block
scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
script = scripts[0]

# Find the R={...} object containing rubrics
# It starts with "const R={" and each entry is 'SK.XXX.XXX':['l0','l1',...,'l5'],
r_start = script.find("const R={")
if r_start < 0:
    r_start = script.find("const R= {")
if r_start < 0:
    print("ERROR: Could not find R object")
    exit(1)

# Find the closing };
r_end = script.find("};", r_start)
r_block = script[r_start:r_end+2]
print(f"Found R object: {len(r_block)} chars")

# Parse each skill entry
# Use a simpler approach - split by skill ID pattern
rubrics = {}
entries = re.split(r"(?='SK\.)", r_block)

for entry in entries:
    # Match: 'SK.XXX.XXX':['text0','text1','text2','text3','text4','text5']
    m = re.match(r"'(SK\.[A-Z]+\.\d+)':\s*\[", entry)
    if not m:
        continue
    skill_id = m.group(1)

    # Extract the array content between [ and ]
    bracket_start = entry.index('[')
    bracket_end = entry.rindex(']')
    array_content = entry[bracket_start+1:bracket_end]

    # Parse quoted strings - handle escaped quotes
    levels = []
    in_quote = False
    current = []
    i = 0
    while i < len(array_content):
        c = array_content[i]
        if c == "'" and not in_quote:
            in_quote = True
            current = []
        elif c == "'" and in_quote:
            # Check for escaped quote
            if i + 1 < len(array_content) and array_content[i+1] == "'":
                current.append("'")
                i += 1
            else:
                levels.append(''.join(current))
                in_quote = False
        elif in_quote:
            current.append(c)
        i += 1

    if len(levels) == 6:
        rubrics[skill_id] = levels
    elif len(levels) > 0:
        print(f"  WARNING: {skill_id} has {len(levels)} levels")

print(f"\nExtracted rubrics for {len(rubrics)} skills")

# Show examples
for sid in ['SK.PRM.003', 'SK.FND.002', 'SK.GOV.022', 'SK.EVL.001', 'SK.CTIC.006']:
    if sid in rubrics:
        print(f"\n{sid}:")
        for i, desc in enumerate(rubrics[sid]):
            print(f"  L{i}: {desc[:80]}")

# Merge into ontology.json
with open('../backend/app/data/ontology.json', 'r', encoding='utf-8') as f:
    ontology = json.load(f)

updated = 0
missing = []
for skill in ontology.get('skills', []):
    sid = skill.get('id', '')
    if sid in rubrics:
        skill['rubric_by_level'] = rubrics[sid]
        updated += 1
    else:
        missing.append(sid)

print(f"\nUpdated {updated}/{len(ontology.get('skills',[]))} skills")
if missing:
    print(f"Missing rubrics for {len(missing)} skills: {missing[:5]}...")

with open('../backend/app/data/ontology.json', 'w', encoding='utf-8') as f:
    json.dump(ontology, f, indent=2, ensure_ascii=False)
print("Saved ontology.json")
