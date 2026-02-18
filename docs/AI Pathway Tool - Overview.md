**Confidential**

**Jan 21, 2026**

# AI Pathway Tool Overview

# Executive Summary

The AI Pathway Tool is a personalized learning platform that maps users from their current AI skill level (State A) to their target role or job requirements (State B). The system generates customized 5-chapter learning paths with domain-specific hands-on projects, leveraging AI-powered analysis and adaptive content generation.

**Core Value Proposition:** Unlike generic AI courses, this tool creates dynamic, personalized curricula based on actual skill gaps, integrating domain-specific AI applications (e.g., AI for Marketing Technology, AI for Finance).

# Product Overview

**Primary Goal**

Transform users from their current AI proficiency level to their target professional competency through personalized, structured learning paths.

**Key Outputs**

* 5 personalized learning chapters per path  
* Domain-specific hands-on projects and exercises  
* Adaptive skill assessments  
* Progress tracking with re-assessment capabilities

**Differentiation**

1. **Domain Integration**: AI skills contextualized to specific industries (martech, healthcare, finance, etc.)  
2. **True Personalization**: Dynamic paths based on actual skill gaps, not one-size-fits-all curriculum  
3. **Continuous Learning**: Built-in re-assessment and progressive deepening after completion

# System Architecture/Flow

The user provides these inputs:

1. Answers questions about their level of knowledge of AI  
2. PDF of their LinkedIn profile (the system derives current position, industry, etc.)  
3. User’s intent for learning AI, e.g. streamline processes.  
4. A position description(s) that the user is aspiring to get to with the new AI skills.

Inputs 1-3 define State A, a state from which this user is starting their AI journey. 

Input 4 defines State B, a state that the user is aspiring to get to.

The system runs State A inputs by the AI ontology to come up with top 5-10 skills that the user needs to learn to apply AI well in their current role. The system attaches a proficiency level to each skill (L0 to L4).

Similarly, the system runs State B by the AI ontology to come up with the top 5-10 skills that the user needs to learn to qualify for that role and attaches the level of proficiency needed for each skills (L0 to L4).

The system then compiles a GAP that shows the tops skills needed to get from State A to State B. The GAP becomes the base for generating the AI Pathway for the user. 

The pathway consists of 5 chapters. Each chapter is focused on the GAP skill. It has a definition of the skill/technique, hands-on exercises for the industry that the user is in and pointers to additional resources. The chapter progresses the user one level only even if the GAP requires the user to jump over several levels. 

At the end of 5 chapters, user is provided with a quiz to confirm that the knowledge was mastered.  

# [Claude Proposed System Architecture](https://claude.ai/public/artifacts/e2923976-cc44-4575-bb5f-60bf3d6ad58e)

# Output Quality Evaluation

See Phase 4 below for suggested frameworks for output quality evaluation. Initially we are planning to 

1. use experts to score 7-12 generated pathways of real users on the following criteria (1-5high):  
   1. Closeness to the user’s intent  
   2. Adherence to AI basic building blocks  
   3. Level of progression on the job If the user learns the pathway skills or ability to qualify for the targeted job  
   4. Correctness of the proficiency level assignment to skills  
   5. Clarity of the pathway modules  
   6. Usefulness of the hands-on exercises  
   7. Relevance of the industry use cases

2. Use experts to score Ai pathways for 5-10 simulated personas across various user archetypes, e.g.  
   1. Career transitioner (e.g., software engineer → ML engineer)  
   2. Domain professional upskilling (e.g., marketer learning AI tools) across 3-5 domains  
   3. Executive seeking AI literacy  
   4. Technical specialist deepening expertise

   Success Criteria (needs work), e.g.

* Path difficulty matches persona level  
* Content relevance to stated goals  
* Realistic time commitments  
* Appropriate prerequisite assumptions

These manual evaluations should give us a good rubric to evaluate AI pathways with LLM as a judge going forward.  
—-------------

# Development Phases

# Phase 1: Core Data Foundation

**1.1 AI Skills Ontology Development \- DONE**

**Purpose**: Create a comprehensive taxonomy of AI skills with hierarchical relationships.  
**Status:** Created. The .md file is in this [folder](https://drive.google.com/drive/folders/1tcCfDE1AI07nUCaZiXvzkBR2-FmSVObs?usp=drive_link). Vivek to add to the folder.

**Quality Evaluation**:

* Test: Map 10 different job descriptions to the ontology  
* Success Criteria: Can extract meaningful skill requirements from diverse JDs  
* Validation: Skills must be granular enough for proficiency scoring but broad enough to be reusable

**Technical Requirements**:

* Hierarchical skill structure (e.g., Machine Learning → Supervised Learning → Classification)  
* Skill categories covering: foundations, techniques, tools, domain applications  
* Metadata: prerequisites, related skills, typical learning duration

**1.2 Skill Proficiency Rubric**

**Purpose**: Define clear proficiency levels for objective skill assessment.

**Deliverable**: Scoring rubric document with L0-L4 levels

**Quality Evaluation**:

* Test: Apply rubric to 3 sample personas with varied backgrounds  
* Success Criteria: Can clearly differentiate skill levels; placements feel intuitive  
* Validation: Inter-rater reliability check on level assignments

**Proficiency Framework**:

* L0: No knowledge  
* L1: Awareness/Basic concepts  
* L2: Practical application with guidance  
* L3: Independent execution  
* L4: Expert/Teaching capability

---

# Phase 2: Input Processing & State Extraction

**2.1 User Intent Capture \- DONE**

**Purpose**: Gather sufficient context for personalization.

**Deliverable**: Form design \+ data model

**Quality Evaluation**:

* Test: Does collected data enable meaningful path differentiation?  
* Success Criteria: Can distinguish between a data scientist transitioning to ML engineering vs. a marketer learning AI tools

**Required Fields**:

* Current role and industry  
* Career intent (transition, upskilling, exploration)  
* Time commitment and learning preferences  
* Domain of interest

**2.2 State B JD Parser**

**Purpose**: Extract required skills from target job descriptions.

**Deliverable**: JD parsing service with structured output

**Quality Evaluation**:

* Test: Process 5 diverse job descriptions (varied roles, seniority, industries)  
* Success Criteria: Extract 80%+ of required skills with correct categorization  
* Edge Cases: Implicit skills, industry jargon, varying JD formats

**Technical Implementation**:

* LLM-powered extraction with structured output  
* Map extracted skills to ontology  
* Identify proficiency level expectations where stated  
* Flag domain-specific requirements

**2.3 LinkedIn Profile Parser**

**Purpose**: Extract professional context from user background.

**Deliverable**: PDF parsing service

**Quality Evaluation**:

* Test: Process 10 LinkedIn PDFs with varying formats  
* Success Criteria: 90%+ accuracy on key fields (role, industry, experience level)  
* Metrics: Title extraction, experience duration, education, skills mentioned

**Technical Considerations**:

* Handle multiple PDF export formats  
* Extract structured work history  
* Identify transferable skills  
* Privacy and data handling compliance

**2.4 State A Assessment Quiz Generator**

**Purpose**: Determine current skill levels through adaptive testing.

**Deliverable**: Quiz generation engine \+ question bank

**Quality Evaluation**:

* Test: Do quiz results correlate with actual skill levels?  
* Validation: Compare quiz scores against user self-assessments and project performance  
* Reliability: Test-retest consistency

**Features**:

* Adaptive questioning based on State B requirements  
* Multi-format questions (concept, application, scenario-based)  
* Time-bounded assessments  
* Immediate scoring with proficiency level mapping

---

# Phase 3: Gap Analysis & Path Generation

**3.1 Skill Gap Calculator**

**Purpose**: Identify and prioritize learning needs.

**Deliverable**: Gap analysis algorithm

**Quality Evaluation**:

* Test: Generate gap analyses for 3 test personas  
* Success Criteria: Prioritization feels intuitive; critical skills surface first  
* Validation: Domain experts review gap assessment logic

**Algorithm Components**:

* Delta calculation: State B requirements \- State A proficiency  
* Priority weighting: job criticality, prerequisite chains, user goals  
* Learning difficulty estimation  
* Time-to-competency projection

**3.2 Learning Path Generator**

**Purpose**: Create personalized 5-chapter curriculum.

**Deliverable**: Curriculum generation engine

**Quality Evaluation**: See Phase 4 (multi-layer validation system)

**Curriculum Design Principles**:

* Progressive skill building (prerequisites → foundations → applications)  
* Chapter structure: concept introduction, practical exercises, domain integration  
* Balanced theory and hands-on practice  
* Clear learning objectives per chapter

**Technical Approach**:

* LLM-generated chapter outlines based on gap analysis  
* Content sequencing algorithms  
* Prerequisite dependency resolution  
* Adaptive chapter sizing based on skill complexity

**3.3 Hands-on Project Designer**

**Purpose**: Generate relevant, achievable projects for skill application.

**Deliverable**: Project template generator

**Quality Evaluation**:

* Are projects clearly scoped?  
* Do they integrate domain context?  
* Are they achievable within chapter timeframe?  
* Do they require newly learned skills?

**Project Components**:

* Problem statement with business context  
* Required skills and tools  
* Step-by-step scaffolding for guidance  
* Success criteria and evaluation rubric  
* Domain-specific data/scenarios

---

# Phase 4: Quality Validation System

**4.1 Path Validation Framework**

**Purpose**: Ensure learning paths are high-quality, effective, and pedagogically sound.

**Deliverable**: Validation rubric \+ scoring system

**This is the most critical phase for product success.**

**Multi-Layer Validation Approach**

**A. Expert Review (First 7-20 Paths)**

**Process**:

* Submit generated paths to AI educators and domain experts  
* Structured review criteria: skill progression, content accuracy, time estimates, project relevance

**Metrics**:

* Pedagogical soundness score (1-5)  
* Content accuracy verification  
* Prerequisite chain validation  
* Estimated completion time reality check

**Deliverable**: Expert feedback incorporation system

**B. Simulated Persona Testing (10-15 Personas)**

**Process**:

* Create detailed test personas spanning user archetypes  
* Generate paths for each persona  
* Evaluate for appropriateness, difficulty calibration, relevance

**Test Personas**:

* Career transitioner (e.g., software engineer → ML engineer)  
* Domain professional upskilling (e.g., marketer learning AI tools)  
* Student/early career exploring AI  
* Executive seeking AI literacy  
* Technical specialist deepening expertise

**Success Criteria**:

* Path difficulty matches persona level  
* Content relevance to stated goals  
* Realistic time commitments  
* Appropriate prerequisite assumptions

**C. Learning Science Validation**

**Criteria**:

* Spaced repetition principles  
* Cognitive load management  
* Active learning integration  
* Retrieval practice opportunities  
* Progressive complexity

**Automated Checks**:

* Chapter length appropriateness (cognitive load)  
* Concept reinforcement frequency  
* Hands-on practice ratio (aim: 40-60%)  
* Knowledge gap detection between chapters

**D. A/B Comparison Testing**

**Method**:

* Generate 2-3 path variants for same user profile  
* Compare on quality dimensions  
* Identify optimal generation parameters

**Comparison Dimensions**:

* Skill coverage completeness  
* Learning efficiency (skills/time)  
* User preference (if user testing available)  
* Expert ratings

**E. Outcome Tracking (Post-Launch)**

**Metrics**:

* Chapter completion rates  
* Quiz score improvements  
* Project submission quality  
* User satisfaction ratings  
* Skill assessment pre/post deltas  
* Time-to-completion vs. estimates

**Feedback Loop**:

* Identify underperforming chapters/projects  
* Flag skill gaps in curriculum  
* Refine generation prompts and algorithms

---

# Phase 5: Course Content & Delivery

**5.1 Content Aggregation Engine**

**Purpose**: Map curriculum to high-quality learning resources.

**Deliverable**: Content library \+ matching algorithm

**Quality Evaluation**:

* Can you find quality resources for 90%+ of common AI skills?  
* Resource quality vetting process  
* Update frequency for outdated content

**Resource Types**:

* Video courses (YouTube, Coursera, Udemy)  
* Documentation and tutorials  
* Research papers and articles  
* Interactive coding environments  
* Open datasets for projects

**Content Matching**:

* Skill → Resource mapping  
* Difficulty level alignment  
* Format preferences (video, text, interactive)  
* Time duration estimates  
* Periodic content refresh (quarterly review)

**5.2 Progress Tracking & Adaptation**

**Purpose**: Monitor learning effectiveness and identify struggle points.

**Deliverable**: Progress tracking system

**Quality Evaluation**:

* Does tracking data accurately reflect learning progress?  
* Can system identify when user is struggling?  
* Are interventions timely and helpful?

**Tracking Metrics**:

* Chapter completion status  
* Quiz scores and time spent  
* Project submission and quality  
* Resource engagement (video watch time, article reads)  
* Struggle indicators (repeated quiz failures, long time gaps)

**Adaptive Features**:

* Suggest additional resources when struggling  
* Offer prerequisite review when gaps detected  
* Adjust difficulty of subsequent content  
* Provide motivational check-ins

**5.3 Re-assessment & Next Level**

**Purpose**: Support continuous learning and skill deepening.

**Deliverable**: Re-generation logic

**Quality Evaluation**:

* Does next level properly build on previous learning?  
* Is progression challenging but achievable?  
* Does it avoid redundant content?

**Re-assessment Triggers**:

* Completion of all 5 chapters  
* User-initiated skill re-evaluation  
* Periodic check-ins (3-6 months)

**Next-Level Generation**:

* Build on acquired skills (State A updated)  
* Deepen existing skills or branch to related areas  
* Maintain domain context  
* Increase project complexity

---

# Phase 6: Application Architecture

**6.1 System Design**

**Purpose**: Build scalable, maintainable full-stack application.

**Deliverable**: Full stack architecture

**Quality Evaluation**:

* Can handle concurrent users?  
* Integrates all components seamlessly?  
* Performant LLM calls with appropriate caching?

**Architecture Components**:

**Frontend (React)**:

* User onboarding flow  
* Assessment quiz interface  
* Learning path dashboard  
* Progress visualization  
* Project submission interface

**Backend (Node.js/Python)**:

* RESTful API design  
* Authentication and authorization  
* LLM orchestration layer  
* Job scheduler for periodic tasks

**AI Layer**:

* LLM integration (OpenAI, Claude, etc.)  
* Prompt management system  
* Response parsing and validation  
* Rate limiting and cost optimization

**Infrastructure**:

* Cloud hosting (AWS/GCP/Azure)  
* CDN for content delivery  
* Caching layer (Redis)  
* Job queue (for long-running LLM tasks)

**6.2 Data Models**

**Purpose**: Design robust, flexible database schemas.

**Deliverable**: Database schema \+ API design

**Quality Evaluation**:

* Supports all required queries efficiently?  
* Handles relationships correctly?  
* Scalable for growth?

**Core Entities**:

User  
\- id, email, auth\_credentials  
\- profile (role, industry, experience\_level)  
\- preferences (learning\_style, time\_commitment)  
\- created\_at, updated\_at  
   
Goal  
\- id, user\_id  
\- target\_role, target\_jd\_text  
\- target\_industry, domain\_focus  
\- state\_b\_skills (JSON: skill\_id, required\_level)  
\- created\_at  
   
SkillAssessment  
\- id, user\_id, goal\_id  
\- assessment\_type (quiz, project, self-reported)  
\- skill\_scores (JSON: skill\_id, proficiency\_level)  
\- completed\_at  
   
LearningPath  
\- id, user\_id, goal\_id  
\- chapters (JSON array of chapter objects)  
\- generation\_version, generation\_params  
\- validation\_scores  
\- created\_at  
   
Chapter  
\- id, learning\_path\_id, sequence  
\- title, learning\_objectives  
\- content\_structure (JSON)  
\- estimated\_duration  
\- resources (JSON array)  
\- project\_spec (JSON)  
   
Progress  
\- id, user\_id, learning\_path\_id  
\- current\_chapter  
\- chapter\_completion\_status (JSON)  
\- quiz\_scores, project\_submissions  
\- time\_spent, last\_active  
\- updated\_at  
   
Resource  
\- id, title, url, type  
\- skill\_tags, difficulty\_level  
\- duration, format  
\- quality\_score, last\_validated  
**API Endpoints**:

* POST /auth/register, /auth/login  
* POST /goals \- Create new learning goal  
* POST /assessments \- Submit skill assessment  
* POST /paths/generate \- Generate learning path  
* GET /paths/:id \- Retrieve learning path  
* PUT /progress/:pathId \- Update progress  
* GET /resources?skill=X\&level=Y \- Resource search

---

# Evaluation Framework

# Pre-Launch Evaluation

**Evaluation 1: Ontology Completeness**

**Test**: Map 10 diverse AI job descriptions **Metrics**:

* Skill coverage: % of JD requirements mappable to ontology  
* Granularity: Average skills extracted per JD  
* Consistency: Inter-coder reliability across multiple JDs

**Target**: 85%+ skill coverage, \<10% unmapped skills

**Evaluation 2: Parsing Accuracy**

**Test**: Process 15 documents (5 JDs, 10 LinkedIn PDFs) **Metrics**:

* Field extraction accuracy: % correct on key fields  
* Skill identification precision/recall  
* Processing time per document

**Target**: 90%+ accuracy on structured fields, 80%+ on skill extraction

**Evaluation 3: Assessment Validity**

**Test**: Compare quiz results with actual user capabilities **Metrics**:

* Correlation: Quiz scores vs. project performance  
* Consistency: Test-retest reliability  
* User feedback: Does assessment feel accurate?

**Target**: r \> 0.7 correlation, 85%+ user agreement

**Evaluation 4: Gap Analysis Quality**

**Test**: Expert review of 10 generated gap analyses **Metrics**:

* Prioritization appropriateness (1-5 scale)  
* Missing critical skills (count)  
* Irrelevant skills included (count)

**Target**: Average 4.0+ on appropriateness, \<1 critical skill missed

**Evaluation 5: Path Quality (MOST CRITICAL)**

**Test**: Multi-layer validation on 20 generated paths **Metrics**:

* Expert ratings: Pedagogical soundness (1-5)  
* Persona fit: Appropriateness for target user (1-5)  
* Learning science: Adherence to principles (checklist)  
* Completeness: Skills covered vs. required (%)

**Target**:

* Expert rating average: 4.0+  
* Persona fit: 4.0+  
* Learning science: 80%+ criteria met  
* Skill coverage: 90%+

**Evaluation 6: Content Matching**

**Test**: Attempt to find resources for 100 common AI skills **Metrics**:

* Coverage: % skills with quality resources  
* Quality score: Average resource rating  
* Freshness: % resources \<2 years old

**Target**: 90%+ coverage, 4.0+ quality score

# Post-Launch Evaluation

**Evaluation 7: User Engagement**

**Metrics**:

* Onboarding completion rate  
* Chapter 1 start rate  
* Path completion rate (all 5 chapters)  
* Time between chapters (pacing)  
* Return rate after completion

**Targets**:

* Onboarding: 70%+  
* Chapter 1 start: 80%+  
* Path completion: 40%+  
* Monthly active user retention: 60%+

**Evaluation 8: Learning Outcomes**

**Metrics**:

* Pre/post skill assessment delta  
* Quiz score progression through chapters  
* Project submission quality scores  
* User self-reported confidence gains  
* Job outcome tracking (if applicable)

**Targets**:

* Average skill level gain: \+1.0 level  
* Quiz improvement: 25%+ from chapter 1 to 5  
* Project quality: 70%+ meeting success criteria

**Evaluation 9: User Satisfaction**

**Metrics**:

* Net Promoter Score (NPS)  
* Path relevance rating (1-5)  
* Project usefulness rating (1-5)  
* Content quality rating (1-5)  
* Pace appropriateness (1-5)

**Targets**:

* NPS: 40+  
* All ratings: 4.0+ average

**Evaluation 10: System Performance**

**Metrics**:

* Path generation time (P50, P95)  
* API response times  
* LLM cost per path generated  
* System uptime  
* Error rates

**Targets**:

* Path generation: \<60 seconds (P95)  
* API responses: \<500ms (P95)  
* Uptime: 99.5%+

---

# Development Roadmap

**Sprint 1 (2-3 weeks)**

* Phase 1: AI Skills Ontology \+ Proficiency Rubric  
* Phase 2.1-2.2: User Intent Capture \+ JD Parser  
* **Deliverables**: Ontology JSON, intake form, working JD parser

**Sprint 2 (2-3 weeks)**

* Phase 2.3-2.4: LinkedIn Parser \+ Quiz Generator  
* Phase 3.1: Skill Gap Calculator  
* **Deliverables**: PDF parser, quiz engine, gap analysis algorithm

**Sprint 3 (3-4 weeks)**

* Phase 3.2-3.3: Learning Path \+ Project Generator  
* Phase 4: Full validation framework implementation  
* **Deliverables**: Path generation engine, validation system

**Sprint 4 (2-3 weeks)**

* Phase 5: Content aggregation, progress tracking, re-assessment  
* Phase 6: MVP application architecture  
* **Deliverables**: Working end-to-end MVP

**Sprint 5 (2 weeks)**

* Enhanced validation and testing  
* UI/UX polish  
* Performance optimization  
* **Deliverables**: Production-ready beta

**Total Timeline**: 11-15 weeks to MVP

---

# Risk Mitigation

**Technical Risks**

1. **LLM Output Quality**: Inconsistent path generation  
   * Mitigation: Extensive prompt engineering, validation layers, human review  
2. **Parsing Accuracy**: Variable document formats  
   * Mitigation: Multiple parser fallbacks, manual review option  
3. **Content Freshness**: AI field evolves rapidly  
   * Mitigation: Quarterly content audits, user-reported outdated content

**Product Risks**

1. **Personalization Effectiveness**: Generic-feeling paths despite customization  
   * Mitigation: Phase 4 validation framework, continuous user feedback  
2. **Completion Rates**: Users don't finish paths  
   * Mitigation: Engagement features, appropriate difficulty calibration, motivational design  
3. **Scalability**: Path generation costs with user growth  
   * Mitigation: Caching strategies, path template reuse, cost optimization

---

# Success Metrics (6-Month Post-Launch)

**Primary Metrics**

* Active users: 1,000+  
* Paths generated: 2,000+  
* Path completion rate: 35%+  
* Average skill gain: \+1.0 proficiency level  
* NPS: 40+

**Secondary Metrics**

* User retention (30-day): 50%+  
* Content resource coverage: 90%+  
* Expert path quality rating: 4.0+  
* System uptime: 99.5%+

---

**Next Steps**

1. **Immediate**: Begin ontology development and JD parser prototyping  
2. **Week 2**: Set up validation framework structure  
3. **Week 4**: First path generation test with expert review  
4. **Week 8**: MVP feature-complete internal testing  
5. **Week 12**: Beta launch with initial user cohort

---

**Questions for Discussion**

1. **Scope**: Should MVP include all 5 phases or focus on core path generation first?  
2. **LLM Provider**: Which LLM(s) for different components? Cost vs. quality trade-offs?  
3. **Content Strategy**: Build proprietary resources or aggregate existing content?  
4. **Validation Investment**: How much expert review budget for Phase 4?  
5. **Monetization**: Freemium model, subscription tiers, or enterprise focus?

---

**Appendix: Technical Considerations**

**LLM Integration Patterns**

* Structured output prompting for parsers  
* Few-shot examples for consistency  
* Temperature tuning per use case  
* Output validation and retry logic

**Scalability Considerations**

* Path generation job queues  
* Result caching strategies  
* Database indexing for common queries  
* CDN for static resources

**Security & Privacy**

* User data encryption  
* PII handling compliance  
* Secure file upload/storage  
* API authentication and rate limiting

 

