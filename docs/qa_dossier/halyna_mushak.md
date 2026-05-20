# QA Dossier - halyna_mushak

**Verdict: YELLOW**

READY WITH CAVEATS: Path Coherence Auditor=GREEN, Skill Curator=YELLOW, Customer Voice Reasoner=YELLOW, Chapter Reviewer=YELLOW

## Per-agent verdicts

### Path Coherence Auditor - GREEN

_all invariants pass across 5 modules and 5 cached lessons_

**Reasoning:** Checked: chapter skill_id resolves in ontology; Module title equals ontology canonical name; cached Lesson content meta.skill_id matches parent Module.skill_id; chapter_number contiguous.

### Skill Curator - YELLOW

_top5 ok (1/2 expected, 0 forbidden)_

**Reasoning:** Customer quote: "the tool pulled our rather rudimentary set of skills for her level. I ran this set by Claude. It recommended a set of skills that was more in depth." Engine returned top5 ['SK.DOM.MKT.001', 'SK.FND.002', 'SK.LRN.001', 'SK.PRD.001', 'SK.COM.001']; expected_top5 was ['SK.DOM.MKT.001', 'SK.COM.005']; forbidden_in_top5 was ['SK.PRM.020', 'SK.PRM.003']. Some expected skills missing. No forbidden hits.

**Findings:**
  - [WARN] expected top5 skill 'SK.COM.005' missing - at rank #7
    > customer: "the tool pulled our rather rudimentary set of skills for her level. I ran this set by Claude. It recommended a set of skills that was more in depth."
    > proposed fix: raise 'SK.COM.005''s rubric score (boost importance, connectivity, or career_signal) so it lands in top 5
  - [INFO] expected top10 skill 'SK.PRM.000' not present in top 10
  - [INFO] expected top10 skill 'SK.PRM.001' not present in top 10
  - [INFO] expected top10 skill 'SK.COM.004' not present in top 10
  - [INFO] expected top10 skill 'SK.RSN.003' not present in top 10
  - [INFO] expected top10 skill 'SK.GOV.010' not present in top 10

### Customer Voice Reasoner - YELLOW

_The engine output does not fully meet the customer's expectations for a more in-depth skill set._

**Reasoning:** The customer's feedback indicates a desire for a more comprehensive and in-depth skill set. The engine output partially meets this by including 'SK.DOM.MKT.001' in the top position, but it fails to include 'SK.COM.005' in the top 5, which is a critical expectation. Additionally, the presence of 'SK.PRM.003' in the top 10, although not in the top 5, suggests a misalignment with the customer's intent for a more advanced skill set. Therefore, the output does not fully address the customer's needs, resulting in an error-level finding.

**Findings:**
  - [WARN] The expected skill 'SK.COM.005' is missing from the top 5.
    > customer: "the tool pulled our rather rudimentary set of skills for her level. I ran this set by Claude. It recommended a set of skills that was more in depth."
    > The customer expected a more in-depth set of skills, including 'SK.COM.005', which is not present in the top 5 positions.
    > proposed fix: Ensure 'SK.COM.005' is included in the top 5 skills.
  - [WARN] A forbidden skill 'SK.PRM.003' appears in the top 10.
    > customer: "the tool pulled our rather rudimentary set of skills for her level. I ran this set by Claude. It recommended a set of skills that was more in depth."
    > The skill 'SK.PRM.003' is listed at position #10, which is not in the top 5 but still indicates a potential misalignment with customer expectations.
    > proposed fix: Remove 'SK.PRM.003' from the top 10 to better align with customer expectations.

### Chapter Reviewer - YELLOW

_audited 5 cached chapter(s); 5 finding(s)_

**Reasoning:** Ran deterministic identity + sections checks across 5 cached chapters. LLM prose-fit check also ran.

**Findings:**
  - [WARN] ch#1 missing sections: ['meta', 'scenario', 'concepts', 'agent_build']
  - [WARN] ch#2 missing sections: ['meta', 'scenario', 'concepts', 'agent_build']
  - [WARN] ch#3 missing sections: ['meta', 'scenario', 'concepts', 'agent_build']
  - [WARN] ch#4 missing sections: ['meta', 'scenario', 'concepts', 'agent_build']
  - [WARN] ch#5 missing sections: ['meta', 'scenario', 'concepts', 'agent_build']

### Demo-Readiness Gate - YELLOW

_READY WITH CAVEATS: Path Coherence Auditor=GREEN, Skill Curator=YELLOW, Customer Voice Reasoner=YELLOW, Chapter Reviewer=YELLOW_

**Reasoning:** Aggregated 4 upstream verdicts. READY WITH CAVEATS. 0 RED, 3 YELLOW, 1 GREEN.
