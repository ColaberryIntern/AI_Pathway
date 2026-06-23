# Skill descriptions - DRAFTS for SME review

LLM-drafted (220/220) from name + rubric anchors. **Not yet in ontology.json** - review/edit, then a separate step wires approved text into the ontology (that is what moves Natural 4 -> 5).

## AI Literacy & Foundations

| id | name | draft description |
|---|---|---|
| SK.FND.000 | What is AI vs traditional software | Understands the fundamental differences between AI systems and traditional software, providing a foundation for working with or adopting AI technologies in the workplace. |
| SK.FND.001 | LLM fundamentals (tokens, context, prediction) | Understands how large language models process input as tokens, manage context windows, and generate predictions, which is essential for crafting effective prompts and troubleshooting model behavior. |
| SK.FND.002 | Capabilities vs limitations (hallucinations) | Recognizes both the strengths and inherent limitations of AI models, including the risk of generating inaccurate or fabricated information (hallucinations), which is critical for ensuring reliable use of AI outputs. |
| SK.FND.003 | Model families (open vs closed) | Distinguishes between different types of AI models, such as open-source and proprietary (closed) systems, enabling informed decisions about model selection, integration, and governance. |
| SK.FND.004 | Reasoning vs retrieval vs tools | Understands the difference between AI generating answers through reasoning, retrieving information from external sources, or using specialized tools, which helps in choosing the right approach for specific tasks. |
| SK.FND.005 | Training data & knowledge cutoffs | Knows that AI models are trained on specific datasets up to a certain date, which affects their knowledge and accuracy, and is able to account for data freshness when using AI for current information. |
| SK.FND.006 | Temperature & sampling basics | Understands how parameters like temperature and sampling affect the creativity, diversity, and reliability of AI-generated outputs, allowing for better control over model responses. |
| SK.FND.010 | Transformer architecture overview | Has a basic grasp of transformer architectures, including the attention mechanism, which underpins most modern language models and is key to understanding their capabilities and limitations. |
| SK.FND.011 | Diffusion models overview | Understands the core principles of diffusion models, which are used for generating images and other media, enabling informed use and evaluation of generative AI tools. |
| SK.FND.012 | Embeddings & semantic similarity | Knows how embeddings represent data as vectors to capture semantic similarity, which is foundational for tasks like search, recommendation, and clustering in AI applications. |
| SK.FND.013 | Multimodal model basics | Recognizes that AI models can process and combine multiple types of data, such as text, images, and audio, which expands the range of possible applications and solutions. |
| SK.FND.020 | Privacy basics for GenAI | Understands basic privacy considerations when using generative AI, including risks of sharing sensitive information and the importance of compliance with data protection regulations. |
| SK.FND.021 | IP/copyright awareness | Is aware of intellectual property and copyright issues related to AI-generated content, which is necessary for responsible and legal use of AI in the workplace. |
| SK.FND.022 | Bias & fairness basics | Recognizes that AI systems can reflect or amplify biases present in their training data, and understands the importance of fairness and bias mitigation in AI outputs. |
| SK.FND.023 | Environmental impact awareness | Understands that developing and running AI models has environmental impacts, such as energy consumption and carbon footprint, which is important for making sustainable technology choices. |
| SK.FND.024 | Long-context model capabilities & tradeoffs (1M+ tokens) | Understands the capabilities and tradeoffs of AI models that handle very long contexts (over 1 million tokens), including when and how to use them based on cost, quality, and business needs. This skill helps organizations make informed decisions about deploying advanced language models. |
| SK.FND.025 | Mixture of Experts (MoE) architecture basics | Knows the basics of Mixture of Experts (MoE) architectures and can evaluate when to use MoE versus dense models, considering trade-offs in performance, scalability, and resource usage. This is important for selecting the right AI model architecture for organizational needs. |

## Agent Harness Engineering

| id | name | draft description |
|---|---|---|
| SK.HRNS.000 | Agent harness concepts & scaffold patterns | This skill focuses on understanding and applying patterns for building agent harnesses, which are frameworks that manage and coordinate AI agents. Mastery of these concepts enables scalable, maintainable deployment of multiple agent versions and configurations. |
| SK.HRNS.001 | Memory system design (working, episodic, semantic, procedural) | This skill is about designing memory systems for AI agents, including working, episodic, semantic, and procedural memory types. Effective memory design allows agents to retain and utilize relevant information over time, improving their usefulness and reliability. |
| SK.HRNS.002 | State machine patterns for long-running agents | This skill involves using state machine patterns to manage the behavior of long-running AI agents, allowing for structured transitions and coordination among sub-agents. It is essential for building robust, predictable agent workflows that can handle complex tasks. |
| SK.HRNS.003 | Context compression & conversation compaction | This skill covers techniques for compressing and managing the context and conversation history that AI agents use, ensuring relevant information is retained without exceeding system limits. Proper context management is key to maintaining agent performance and compliance. |
| SK.HRNS.004 | Hook-based agent middleware & interceptors | This skill involves implementing middleware and interceptors using hooks, allowing developers to modify or extend agent behavior dynamically. It is important for enabling customization, monitoring, and integration of agents in diverse environments. |
| SK.HRNS.005 | Conversation thread & history management | This skill focuses on managing conversation threads and histories across distributed AI agents, ensuring consistency and scalability. Effective thread management is necessary for supporting multi-user, multi-agent interactions in enterprise settings. |
| SK.HRNS.006 | Agent SDK patterns (Claude Agent SDK, LangGraph, AutoGen) | This skill is about applying patterns from various agent SDKs to build flexible agent platforms that support different frameworks. It enables organizations to standardize agent infrastructure while allowing teams to use their preferred development tools. |
| SK.HRNS.007 | Harness observability & step-level debugging | This skill covers implementing observability and debugging tools at the agent harness level, including step-by-step tracing and centralized monitoring. These capabilities are vital for diagnosing issues, ensuring reliability, and maintaining compliance in AI systems. |

## Agent Protocols

| id | name | draft description |
|---|---|---|
| SK.PROTO.000 | Agent-to-Agent (A2A) protocol | Knows how agents communicate directly with each other using specialized protocols, and can design systems that integrate multiple communication standards for seamless agent collaboration. This is important for building scalable, interoperable AI agent ecosystems in organizations. |
| SK.PROTO.001 | Agent cards & capability discovery | Understands how agents advertise their capabilities to other agents and can design mechanisms for automated discovery and coordination in large, multi-provider environments. This skill enables efficient agent collaboration and dynamic task allocation in complex systems. |
| SK.PROTO.002 | Context engineering | Distinguishes context engineering from prompt engineering and can design systems where agents share and manage context, memory, and state across interactions. Mastery of this skill ensures agents operate with relevant information, improving accuracy and coordination. |
| SK.PROTO.003 | Multi-protocol agent systems (MCP + A2A) | Understands the need for agents to operate across multiple communication protocols and can design unified architectures that support interoperability, governance, and security. This skill is crucial for integrating diverse agent systems within an enterprise. |
| SK.PROTO.004 | Agent protocol security | Recognizes and addresses security challenges in agent communication protocols, including designing architectures that enforce zero-trust principles. This ensures that agent interactions remain secure and resilient against threats. |
| SK.PROTO.005 | MCP server authoring & tool publishing | Develops and publishes tools for MCP (Multi-Agent Communication Protocol) servers, following organizational standards for naming, documentation, versioning, and security review. |
| SK.PROTO.006 | OpenAPI-to-MCP tool conversion | Converts OpenAPI specifications into MCP-compatible tools, establishing quality and review standards to ensure reliable integration and lifecycle management of agent tools. |

## Agentic Coding

| id | name | draft description |
|---|---|---|
| SK.ACODE.000 | Vibe coding & natural language development | This skill covers rapidly prototyping software and solutions by describing requirements in natural language, allowing AI to generate code and iterate quickly, which accelerates development and bridges communication gaps between technical and non-technical team members. |
| SK.ACODE.001 | CLI coding agent usage (Claude Code) | This skill involves using command-line interface (CLI) AI coding agents to write, modify, and manage code directly from the terminal, enabling efficient, AI-assisted development workflows for engineers. |
| SK.ACODE.002 | Agentic IDE mastery (Cursor, Windsurf) | This skill is about mastering AI-native integrated development environments (IDEs) that go beyond autocomplete, leveraging agentic features to boost productivity, automate repetitive tasks, and support advanced coding workflows. |
| SK.ACODE.003 | AI-assisted code review | This skill involves using AI tools to review code for errors, style issues, and potential improvements, helping teams maintain higher code quality and reduce manual review effort. |
| SK.ACODE.004 | AI-generated test suites | This skill covers generating comprehensive test suites with AI, allowing for faster and more thorough testing of software, which improves reliability and reduces manual test creation. |
| SK.ACODE.005 | Autonomous debugging with AI | This skill is about leveraging AI to autonomously detect, diagnose, and fix bugs in code, reducing downtime and manual debugging effort while improving software resilience. |
| SK.ACODE.006 | Code architecture with AI | This skill involves using AI to assist in making high-level software architecture decisions, supporting teams in designing scalable, maintainable, and robust systems. |
| SK.ACODE.007 | AI code quality & slop prevention | This skill focuses on ensuring that AI-generated code meets quality, security, and maintainability standards, preventing issues like insecure or poorly structured code from entering production. |
| SK.ACODE.008 | AI pair programming & TDD with agentic tools | Collaborates with AI tools for pair programming and applies test-driven development practices, ensuring code quality and clear attribution of AI-generated contributions in software projects. |

## Agents & Orchestration

| id | name | draft description |
|---|---|---|
| SK.AGT.000 | What are AI agents | AI agents are autonomous software entities that can perceive their environment, make decisions, and take actions to achieve specific goals. Understanding this concept is foundational for building systems that automate complex tasks or workflows. |
| SK.AGT.001 | Tool definitions & validation | Tool definitions and validation involve specifying which external tools an AI agent can use and ensuring those tools are safe and effective. This skill is crucial for extending agent capabilities while maintaining control and security. |
| SK.AGT.002 | Error handling & retries | Error handling and retries refer to strategies for managing failures or unexpected outcomes when agents interact with tools or services. This skill is important for building robust AI systems that can recover gracefully from errors. |
| SK.AGT.003 | State & memory management | State and memory management is about tracking and storing information over time so that agents can remember past actions, context, or conversations. This skill enables agents to operate effectively in multi-step or long-running tasks. |
| SK.AGT.010 | Single-agent loops | Single-agent loops are iterative processes where an agent repeatedly observes, decides, and acts to accomplish a task. Mastering this skill is key for building agents that can autonomously pursue goals through repeated cycles. |
| SK.AGT.011 | Multi-agent patterns | Multi-agent patterns involve designing systems where multiple agents collaborate or coordinate to solve complex problems. This skill allows for scalable solutions that leverage teamwork among autonomous agents. |
| SK.AGT.012 | Graph-based orchestration | Graph-based orchestration uses graph structures to model and manage workflows, enabling flexible and dynamic execution paths for agents. This skill supports the creation of sophisticated automation pipelines with complex dependencies. |
| SK.AGT.020 | MCP protocol concepts | MCP protocol concepts cover the principles behind the Model Context Protocol, which standardizes how agents and models exchange context and instructions. Understanding this protocol is important for building interoperable and extensible agent systems. |
| SK.AGT.021 | Agent permissions (least privilege) | Defines and enforces the minimum permissions AI agents need to perform their tasks, reducing security risks and ensuring compliance with organizational policies. |
| SK.AGT.030 | Guardrails & approval gates | Implements controls and approval processes that limit what AI agents can do, helping prevent unintended actions and ensuring agent behavior aligns with safety and organizational standards. |
| SK.AGT.031 | Agent auditability | Ensures that all actions taken by AI agents are recorded and traceable, supporting accountability, troubleshooting, and regulatory compliance. |
| SK.AGT.032 | Agent memory architectures (episodic, semantic, procedural) | Understands different types of agent memory (episodic, semantic, procedural) and can design systems that manage memory sharing, isolation, and compliance across agents. This skill is key for building agents that learn and operate effectively in complex environments. |
| SK.AGT.033 | Human-agent handoff & escalation design | Designs processes and standards for handing off tasks between humans and agents, including escalation paths, service level agreements, and accountability measures. This ensures smooth collaboration and reliable outcomes in human-agent workflows. |

## Communication & Collaboration

| id | name | draft description |
|---|---|---|
| SK.COM.001 | Explaining AI to non-technical audiences | Communicates complex AI concepts in clear, accessible language so that non-technical stakeholders can understand, make decisions, and engage with AI projects effectively. |
| SK.COM.002 | Writing AI project proposals | Prepares structured documents that outline the objectives, scope, benefits, and requirements of AI projects, ensuring stakeholders understand the proposal and can assess its feasibility. |
| SK.COM.003 | Facilitating AI workshops | Leads interactive sessions focused on AI topics, guiding participants through learning activities and discussions to build shared understanding and practical skills. |
| SK.COM.004 | Managing AI expectations | Sets realistic expectations about AI capabilities and limitations, helping teams and stakeholders avoid misunderstandings and plan projects based on what AI can actually deliver. |
| SK.COM.005 | Cross-functional AI collaboration | Works effectively with colleagues from different departments or specialties on AI projects, ensuring diverse expertise is integrated and project goals are aligned. |
| SK.COM.006 | AI documentation best practices | Creates and maintains clear, comprehensive documentation for AI systems, supporting transparency, compliance, and ease of future maintenance or audits. |

## Computer Use Agents

| id | name | draft description |
|---|---|---|
| SK.COMP.000 | Computer use agent concepts | This skill is about understanding how AI agents can interact with computer interfaces by visually interpreting screens, enabling automation of tasks that previously required human input. |
| SK.COMP.001 | Browser automation with AI | This skill involves using AI to autonomously control web browsers, automating tasks such as data entry, scraping, and web testing at scale. |
| SK.COMP.002 | Desktop automation with AI | This skill covers automating desktop applications using AI, even when no APIs are available, allowing organizations to modernize and streamline legacy workflows. |
| SK.COMP.003 | Operator-style task delegation | This skill is about delegating complex, multi-step tasks to AI agents in an operator-style fashion, enabling automation of entire workflows while maintaining oversight and compliance. |
| SK.COMP.004 | Computer use safety & governance | Understands the risks and governance requirements unique to agents that use computers, including how to design and enforce safety controls to prevent misuse or unauthorized access. This skill is essential for ensuring secure and compliant deployment of computer use agents in enterprise environments. |
| SK.COMP.005 | Stateful multi-step task orchestration | Designs and manages systems where AI agents coordinate multi-step tasks, maintain shared state, and support compliance requirements, enabling complex workflows to be automated reliably. |

## Critical Thinking & Info Eval

| id | name | draft description |
|---|---|---|
| SK.CTIC.001 | Evaluating source credibility | Assesses whether information sources are trustworthy and reliable, helping to avoid misinformation and make informed decisions. |
| SK.CTIC.002 | Identifying misinformation patterns | Recognizes common patterns and tactics used in spreading misinformation, which is important for identifying false or misleading content online. |
| SK.CTIC.003 | Cross-referencing claims | Checks information against multiple sources to verify its accuracy, reducing the risk of relying on incorrect or biased data. |
| SK.CTIC.004 | Understanding bias in content | Identifies potential bias in content, allowing for more objective analysis and fair interpretation of information. |
| SK.CTIC.005 | Distinguishing fact from opinion | Differentiates between factual statements and personal opinions, which is key for critical analysis and clear communication. |
| SK.CTIC.006 | Recognizing AI-generated content | Recognizes when content such as text, images, or videos has been generated by AI, which helps in assessing authenticity and potential risks. |

## Digital Literacy

| id | name | draft description |
|---|---|---|
| SK.DIG.001 | Web browsing & search fundamentals | Understands how to use web browsers and search engines to find information online, which is essential for efficiently accessing resources and conducting research in a digital work environment. |
| SK.DIG.002 | File management & cloud storage | Knows how to organize, store, and retrieve files both locally and in cloud storage, enabling secure and efficient management of digital documents and collaboration with others. |
| SK.DIG.003 | Basic spreadsheet operations | Can create, edit, and perform basic calculations in spreadsheets, which supports data organization, analysis, and reporting tasks common in many workplaces. |
| SK.DIG.004 | Email & digital communication | Uses email and digital messaging tools to communicate professionally, which is crucial for effective collaboration and information sharing in modern organizations. |
| SK.DIG.005 | Password & account security basics | Understands the importance of strong passwords and basic account security practices, helping to protect sensitive information and prevent unauthorized access. |
| SK.DIG.006 | Installing & using applications | Can install, update, and use software applications, ensuring access to necessary digital tools and maintaining productivity in a technology-driven workplace. |
| SK.DIG.007 | Copy/paste & keyboard shortcuts | Uses copy/paste functions and keyboard shortcuts to work more efficiently, saving time and reducing repetitive manual tasks. |
| SK.DIG.008 | Screen sharing & video calls | Participates in video calls and shares screens to collaborate remotely, which is vital for teamwork and communication in hybrid or distributed work settings. |

## Domain Applications

| id | name | draft description |
|---|---|---|
| SK.DOM.HC.001 | Healthcare: Clinical risk awareness | Understands how AI can introduce new types of clinical risk and why it is important to identify, assess, and mitigate these risks to protect patient safety and comply with healthcare regulations. |
| SK.DOM.HC.002 | Healthcare: Evidence synthesis | Knows how to use AI tools to gather, analyze, and summarize medical evidence, supporting clinical decision-making and ensuring recommendations are based on up-to-date, high-quality information. |
| SK.DOM.LGL.001 | Legal: Disclaimer & advice boundaries | Recognizes the boundaries between providing general information and legal advice when using AI, ensuring compliance with legal practice rules and protecting organizations from unauthorized practice risks. |
| SK.DOM.LGL.002 | Legal: Hallucination eval frameworks | Understands that AI can generate inaccurate or fabricated legal information and knows how to implement evaluation processes to detect, prevent, and monitor such errors in legal workflows. |
| SK.DOM.FIN.001 | Finance: Numerical auditability | Appreciates the need for transparent and traceable AI-generated financial outputs, enabling auditability and compliance with financial reporting standards and internal controls. |
| SK.DOM.EDU.001 | Education: Learning design with AI | Understands how to incorporate AI into instructional design to enhance learning experiences, while balancing personalization, educational quality, and fairness for all learners. |
| SK.DOM.MKT.001 | Marketing: Content generation ethics | Recognizes ethical challenges in using AI for marketing content, such as misinformation, bias, and brand safety, and knows how to address these issues to maintain trust and compliance. |
| SK.DOM.HR.001 | HR: AI in hiring considerations | Understands the risks of bias, discrimination, and legal non-compliance when using AI in hiring, and knows how to implement safeguards to ensure fair and lawful recruitment practices. |

## Evaluation & Observability

| id | name | draft description |
|---|---|---|
| SK.EVL.000 | Why AI evaluation matters | Understanding why AI evaluation matters ensures that AI outputs are reliable, accurate, and aligned with user needs. This skill is foundational for maintaining trust and effectiveness in AI-powered solutions. |
| SK.EVL.001 | Eval types (offline/online/red team) | Knowledge of evaluation types—such as offline, online, and red team testing—enables practitioners to assess AI systems from different perspectives and in various environments. This skill is vital for ensuring comprehensive quality assurance and risk mitigation. |
| SK.EVL.002 | LLM-as-judge patterns | LLM-as-judge patterns involve using large language models to automatically evaluate the outputs of other AI models, often at scale. This approach streamlines quality assessment and supports rapid iteration in AI development. |
| SK.EVL.010 | Tracing & observability | Tracing and observability for AI systems involve monitoring, logging, and analyzing the behavior of models in production. This skill is important for diagnosing issues, ensuring reliability, and maintaining transparency in complex AI workflows. |
| SK.EVL.011 | Quality dashboards & alerts | Quality dashboards and alerts provide real-time visibility into the performance and health of AI systems, enabling proactive management. This skill helps organizations detect problems early and maintain high standards for AI outputs. |
| SK.EVL.020 | Prompt unit tests | Prompt unit tests are automated checks that validate the behavior and reliability of prompts used with AI models. This skill is essential for preventing regressions and ensuring consistent performance as prompts evolve. |
| SK.EVL.021 | Release gates & rollback | Release gates and rollback mechanisms control when and how AI updates are deployed, allowing for safe rollouts and quick reversions if issues arise. This skill is critical for minimizing risk and maintaining system stability during continuous deployment. |
| SK.EVL.022 | A/B testing for AI | A/B testing for AI involves comparing different model versions or configurations to determine which performs better in real-world scenarios. This skill supports data-driven decision-making and continuous improvement of AI systems. |

## Extended Reasoning

| id | name | draft description |
|---|---|---|
| SK.RSN.000 | What are reasoning models (o3, R1, extended thinking) | Understands the differences between reasoning models and standard chat models, recognizing when advanced reasoning is needed for complex tasks. |
| SK.RSN.001 | Extended thinking & test-time compute | Applies knowledge of extended thinking and test-time compute scaling to balance the quality of AI outputs with resource and cost constraints. |
| SK.RSN.002 | Reasoning model selection & routing | Chooses and routes tasks to the appropriate AI model—reasoning or standard—based on task complexity, optimizing for accuracy, speed, and resource use. |
| SK.RSN.003 | Deep research agents | This skill involves using AI agents that can autonomously gather, synthesize, and summarize information from multiple sources in a single session, streamlining research tasks and supporting knowledge-intensive work. |
| SK.RSN.004 | Chain-of-thought verification | This skill is about evaluating and verifying the logical steps an AI takes to reach conclusions, helping ensure that automated reasoning is accurate and reliable, especially in situations where mistakes could have serious consequences. |
| SK.RSN.005 | Inference cost budgeting for reasoning models | This skill focuses on managing and optimizing the computational and financial costs associated with running advanced reasoning models, balancing resource use with the need for high-quality outputs. |
| SK.RSN.006 | Long-context strategies (needle-in-haystack, retrieval at scale) | Designs strategies for handling tasks that require processing or retrieving information from large volumes of data, ensuring AI systems can efficiently find relevant details in complex or lengthy contexts. |
| SK.RSN.007 | Thinking budget control & cost/quality tradeoff analysis | Analyzes and manages the tradeoffs between computational cost and output quality in AI reasoning tasks, helping organizations allocate resources effectively and control expenses. |

## Governance & Compliance

| id | name | draft description |
|---|---|---|
| SK.GOV.000 | AI governance fundamentals | Covers the foundational concepts of governing AI systems, including setting policies, roles, and processes to ensure responsible and compliant AI use within organizations. |
| SK.GOV.001 | AI risk framing | Involves identifying, assessing, and managing the risks associated with AI systems, which is essential for preventing unintended consequences and ensuring trustworthy AI deployment. |
| SK.GOV.002 | Policy to controls mapping | Focuses on translating organizational policies into actionable technical controls, which is necessary for ensuring that AI systems operate in compliance with internal and external requirements. |
| SK.GOV.010 | AI regulations landscape (EU AI Act) | Involves understanding the current landscape of AI regulations, such as the EU AI Act, to ensure that AI systems are designed and operated in compliance with legal requirements. |
| SK.GOV.020 | PII/PHI handling & retention | Covers best practices for handling and retaining personally identifiable information (PII) and protected health information (PHI), which is crucial for maintaining privacy and meeting regulatory obligations in AI projects. |
| SK.GOV.021 | Data minimization & anonymization | Involves applying techniques to minimize the amount of personal data collected and to anonymize data, which helps protect privacy and reduce compliance risks when training and deploying AI models. |
| SK.GOV.022 | AI-generated content disclosure | Covers the requirements and methods for disclosing when content is generated by AI, which is important for transparency, trust, and meeting regulatory or industry standards. |
| SK.GOV.023 | EU AI Act enforcement readiness | Involves preparing organizations to comply with the enforcement of the EU AI Act, including understanding timelines, obligations, and adapting systems to ongoing regulatory changes. |
| SK.GOV.024 | NIST AI RMF & US AI policy landscape | Understands the NIST AI Risk Management Framework and the broader US AI policy environment, enabling organizations to align their AI risk management practices with recognized standards and regulatory expectations. |
| SK.GOV.025 | Model cards & AI transparency documentation | Creates and maintains documentation that explains how AI models work, including model cards and datasheets, to promote transparency, accountability, and informed use of AI systems. |

## LLMOps & Deployment

| id | name | draft description |
|---|---|---|
| SK.OPS.000 | What is LLMOps | Refers to the set of practices and tools for managing, deploying, and maintaining large language models (LLMs) in production environments. Understanding LLMOps is essential for ensuring reliable, scalable, and efficient AI operations. |
| SK.OPS.001 | Latency drivers & optimization | Involves identifying the factors that contribute to latency in AI systems and applying techniques to reduce response times. Optimizing latency is critical for delivering fast and responsive AI-powered applications. |
| SK.OPS.002 | Cost modeling & token budgeting | Entails modeling the costs associated with AI inference and managing token usage to stay within budget. Effective cost modeling and token budgeting help organizations control expenses while maintaining AI performance. |
| SK.OPS.010 | Caching, batching, streaming | Covers techniques like caching, batching, and streaming to improve the efficiency and throughput of AI systems. Mastery of these methods enables scalable and cost-effective AI deployments. |
| SK.OPS.011 | Model routing strategies | Involves strategies for directing requests to the most appropriate AI model based on criteria like cost, latency, or accuracy. Model routing ensures optimal use of resources and consistent user experiences. |
| SK.OPS.020 | SLOs/SLAs & incident response | Focuses on defining service level objectives (SLOs) and agreements (SLAs) for AI systems, as well as planning for incident response. This skill is vital for maintaining reliability and quickly addressing issues in production AI environments. |
| SK.OPS.021 | Security reviews & deployment gates | Entails conducting security reviews and implementing deployment gates to ensure AI systems meet security standards before going live. These practices help prevent vulnerabilities from reaching production. |
| SK.OPS.022 | Versioning prompts & models | Involves tracking and managing different versions of prompts and models to ensure reproducibility and control over AI system behavior. Versioning is essential for auditing, rollback, and continuous improvement. |
| SK.OPS.023 | Local model deployment (Ollama, llama.cpp, GGUF) | Knows how to deploy AI models locally using tools like Ollama or llama.cpp, including hardware selection, governance, updates, and monitoring. This skill is essential for organizations that require on-premises AI solutions for privacy or compliance reasons. |
| SK.OPS.024 | Prompt caching strategies & latency/cost optimization | Understands prompt caching strategies to optimize latency and cost in AI applications, and can design shared caching infrastructure and governance for enterprise use. This skill improves efficiency and scalability of AI-powered products. |

## Learning & Adaptation

| id | name | draft description |
|---|---|---|
| SK.LRN.001 | Keeping up with AI developments | Regularly tracks advances in AI technology, research, and best practices to stay current and identify opportunities or risks relevant to one's work. |
| SK.LRN.002 | Evaluating new AI tools | Assesses new AI tools for suitability, effectiveness, and alignment with organizational needs, ensuring only valuable and reliable tools are adopted. |
| SK.LRN.003 | Building personal AI workflows | Integrates AI tools into daily work routines to increase productivity, automate tasks, or enhance decision-making, adapting workflows as new capabilities emerge. |
| SK.LRN.004 | Teaching others AI skills | Shares AI knowledge and skills with others through instruction, mentoring, or training, helping colleagues or teams build their own AI capabilities. |
| SK.LRN.005 | Experimenting safely with AI | Experiments with AI tools and systems while considering safety, ethical, and compliance factors, minimizing risks to data, users, and the organization. |

## Model Adaptation

| id | name | draft description |
|---|---|---|
| SK.MOD.000 | When to customize vs use off-the-shelf | Evaluates when it is appropriate to use pre-built AI models versus customizing them, balancing cost, performance, and business needs. |
| SK.MOD.001 | Prompt vs fine-tune decision | Assesses whether to adapt AI models through prompting or by fine-tuning, considering factors like task complexity, data availability, and required performance. |
| SK.MOD.002 | Data requirements for tuning | Identifies the type, quantity, and quality of data needed for effective model fine-tuning, ensuring that adaptation efforts lead to reliable outcomes. |
| SK.MOD.010 | Instruction tuning basics | Understands how to adjust AI models to follow specific instructions more accurately, improving their usefulness for targeted tasks. |
| SK.MOD.011 | PEFT/LoRA concepts | Applies parameter-efficient fine-tuning techniques such as LoRA to adapt large models with minimal computational resources, enabling scalable and cost-effective customization. |
| SK.MOD.012 | Synthetic data generation | Creates or sources artificial data to supplement real-world datasets, enhancing model training while managing issues like bias and data diversity. |

## Multimodal AI

| id | name | draft description |
|---|---|---|
| SK.MUL.000 | Types of multimodal AI | Recognizes and differentiates between AI systems that process text, images, audio, or video, enabling selection of the right approach for complex, real-world tasks. |
| SK.MUL.001 | Image-to-text extraction | Uses AI tools to extract text from images, supporting workflows like document digitization, data entry automation, and information retrieval. |
| SK.MUL.002 | Image generation prompting | Crafts effective prompts to generate images with AI, ensuring outputs match desired styles, content, and brand guidelines. |
| SK.MUL.003 | Image generation QA | Evaluates the quality, accuracy, and appropriateness of AI-generated images, ensuring they meet organizational standards before deployment. |
| SK.MUL.010 | Speech-to-text & summarization | Uses AI to transcribe and summarize spoken content, streamlining tasks like meeting documentation, accessibility, and information retrieval from audio sources. |
| SK.MUL.011 | Video understanding | Applies AI to interpret and analyze video content, enabling applications such as automated content tagging, security monitoring, and educational resource creation. |
| SK.MUL.012 | Text-to-speech applications | Text-to-speech applications use AI to convert written text into natural-sounding spoken audio, enabling accessibility, voice interfaces, and content localization. This skill is important for creating inclusive digital experiences and automating voice content generation. |
| SK.MUL.013 | Document/PDF understanding | Document/PDF understanding involves using AI to extract, interpret, and analyze information from documents in various formats, such as PDFs. Mastery of this skill allows efficient automation of data entry, compliance checks, and knowledge extraction from unstructured files. |
| SK.MUL.014 | Native audio/video generation (Kling, Sora, Veo) | Native audio/video generation refers to using AI tools to create synchronized audio and video content from prompts or scripts, often with control over style and branding. This capability is essential for producing scalable multimedia content and automating creative workflows. |
| SK.MUL.015 | Multimodal RAG | Multimodal RAG (Retrieval-Augmented Generation) integrates information from multiple data types—such as text, images, and audio—into AI-generated outputs. This skill is crucial for building systems that can answer questions or generate content using diverse, real-world data sources. |
| SK.MUL.016 | Real-time voice AI & streaming conversation pipelines | Understands how to build and manage real-time voice AI systems, including streaming pipelines, latency requirements, telephony integration, and compliance. This skill is vital for deploying voice-enabled AI solutions at scale. |
| SK.MUL.017 | Multimodal embeddings & cross-modal retrieval (CLIP, ImageBind) | Knows how to use multimodal embeddings for cross-modal retrieval, such as searching images with text or vice versa, and can design enterprise strategies for model selection, infrastructure, and governance. This enables advanced search and analysis across different data types. |

## Product & UX

| id | name | draft description |
|---|---|---|
| SK.PRD.000 | AI product thinking basics | Knows how to approach AI from a product perspective, considering user needs, business goals, and the unique opportunities and challenges AI brings to product development. |
| SK.PRD.001 | Use-case selection & prioritization | Can evaluate and prioritize potential AI use cases based on feasibility, impact, and alignment with organizational strategy, ensuring resources are focused on the most valuable opportunities. |
| SK.PRD.002 | Workflow mapping | Understands how to map and analyze workflows to identify where AI can be integrated for maximum efficiency and value, supporting effective process transformation. |
| SK.PRD.010 | Explainability UX design | Knows how to design user experiences that make AI decisions understandable and transparent, supporting user trust and meeting regulatory requirements for explainability. |
| SK.PRD.011 | Feedback loop design | Understands the importance of collecting and using user feedback to continuously improve AI systems, designing processes that enable iterative learning and optimization. |
| SK.PRD.020 | AI enablement & training strategy | Knows how to develop strategies for training and enabling users to effectively adopt and benefit from AI tools, including planning for organizational change and support. |
| SK.PRD.021 | Stakeholder management | Understands how to identify, engage, and manage stakeholders in AI projects, ensuring alignment, buy-in, and successful implementation across the organization. |
| SK.PRD.022 | ROI measurement for AI | Measures the financial and strategic impact of AI initiatives by tracking costs, benefits, and value delivered, enabling organizations to make informed investment decisions and justify AI spending. |

## Prompting & HITL Workflows

| id | name | draft description |
|---|---|---|
| SK.PRM.000 | Writing clear requests to AI | Knows how to write clear, specific, and effective requests or prompts for AI systems, which is essential for obtaining accurate and useful responses in professional settings. |
| SK.PRM.001 | Instructions + constraints + format | Crafting clear instructions, specifying constraints, and defining output formats helps AI systems generate responses that meet user needs and business requirements. Mastery of this skill enables scalable and reusable prompt designs for consistent, high-quality results. |
| SK.PRM.002 | Few-shot examples | Providing a few relevant examples in prompts helps AI models understand the desired pattern or style, improving output accuracy. Advanced use involves dynamically selecting examples to optimize performance in production environments. |
| SK.PRM.003 | Prompt debugging & iteration | Systematically testing and refining prompts allows users to identify issues and improve AI output quality over time. This skill is essential for maintaining reliable AI systems and ensuring prompts adapt to changing needs. |
| SK.PRM.004 | Role & persona prompting | Assigning roles or personas to AI prompts guides the model’s behavior and tone, making interactions more contextually appropriate. This technique is important for building multi-agent systems and tailoring AI responses to specific user scenarios. |
| SK.PRM.005 | Chain-of-thought prompting | Encouraging the AI to explain its reasoning step-by-step leads to more transparent and accurate outputs, especially for complex tasks. Combining this approach with other prompting techniques enhances the model’s problem-solving abilities. |
| SK.PRM.006 | Breaking complex tasks into steps | Dividing complex tasks into smaller, manageable steps helps AI systems process and solve problems more effectively. This approach supports the design of workflows where AI can handle multi-step processes with greater reliability. |
| SK.PRM.010 | JSON/schema outputs | Requesting structured outputs such as JSON or adhering to specific schemas ensures that AI responses can be easily parsed and integrated into downstream systems. This skill is crucial for building robust, automated workflows that rely on consistent data formats. |
| SK.PRM.011 | Rubrics as prompts | Using rubrics as part of prompts provides clear criteria for evaluating AI-generated content, leading to more objective and consistent outputs. This technique supports quality assurance and helps align AI responses with organizational standards. |
| SK.PRM.020 | Draft -> critique -> revise | Implementing iterative workflows where AI drafts, critiques, and revises content leads to higher quality and more refined outputs. This process enables continuous improvement and self-correction in content generation tasks. |
| SK.PRM.021 | Grounding & citations | Ensuring that AI outputs are grounded in reliable sources and include citations increases trust and accountability. This skill is vital for applications where accuracy and transparency are critical, such as research or regulated industries. |
| SK.PRM.022 | ReAct-style patterns | Applying reasoning-action (ReAct) patterns enables AI to alternate between thinking and taking actions, improving its ability to solve complex, multi-step problems autonomously. Mastery of this approach is key for building advanced, agentic AI systems. |

## Retrieval & RAG Systems

| id | name | draft description |
|---|---|---|
| SK.RAG.000 | What is RAG and why use it | Retrieval-augmented generation (RAG) combines information retrieval with generative AI to produce more accurate and up-to-date responses. Understanding RAG is essential for building systems that leverage external knowledge sources effectively. |
| SK.RAG.001 | Query rewriting | Rewriting user queries improves the relevance and accuracy of retrieved information by clarifying intent and optimizing for retrieval systems. This skill is important for ensuring users get the most useful results from AI-powered search and question-answering tools. |
| SK.RAG.002 | Chunking strategies | Splitting documents into appropriately sized and meaningful chunks enables efficient and accurate retrieval of relevant information. Advanced chunking strategies enhance retrieval performance and support scalable document processing. |
| SK.RAG.003 | Hybrid retrieval (vector + keyword) | Combining vector-based and keyword-based retrieval methods allows AI systems to find information using both semantic meaning and exact matches. This hybrid approach improves coverage and relevance in search and retrieval applications. |
| SK.RAG.010 | Reranking & scoring | Reranking and scoring involves ordering retrieved documents or passages based on their relevance to a query, often using learned models. This skill helps ensure that the most useful and accurate information is presented first in AI-driven search or retrieval systems. |
| SK.RAG.011 | Context budgeting | Context budgeting is the practice of managing the limited context window available to language models by selecting and prioritizing information to maximize relevance and utility. This skill is important for fitting the most valuable content into model prompts without exceeding token limits. |
| SK.RAG.012 | Lost in the middle mitigation | Lost in the middle mitigation addresses the issue where information placed in the middle of a context window is less likely to be used by language models. Mastering this skill helps ensure that all critical information is accessible and utilized effectively in retrieval-augmented generation. |
| SK.RAG.020 | Faithfulness evaluation | Faithfulness evaluation is the process of assessing whether AI-generated outputs accurately reflect the retrieved source material. This skill is essential for maintaining trust and reliability in systems that combine retrieval with generation. |
| SK.RAG.021 | Golden sets & regression testing | Golden sets and regression testing involve using curated datasets and repeatable tests to measure and maintain the quality of retrieval-augmented generation systems over time. This ensures that updates or changes do not degrade system performance or accuracy. |
| SK.RAG.022 | Agentic RAG patterns | Agentic RAG patterns refer to retrieval-augmented generation workflows where autonomous agents perform multi-step retrieval and reasoning tasks. This skill enables the design of systems that can dynamically gather and synthesize information without constant human intervention. |
| SK.RAG.023 | Temporal & time-aware RAG | Temporal and time-aware RAG focuses on incorporating document timestamps and recency into retrieval strategies. This skill ensures that AI systems provide up-to-date and contextually relevant information, especially when combining static and live data sources. |

## Safety & Security

| id | name | draft description |
|---|---|---|
| SK.SEC.000 | AI security threat landscape | Understanding the AI security threat landscape means recognizing the unique risks and attack vectors that target AI systems. This skill is necessary for protecting sensitive data and maintaining trust in AI applications. |
| SK.SEC.001 | Prompt injection mitigation | Prompt injection mitigation focuses on defending AI systems against attacks where malicious inputs manipulate model behavior. This skill is important for safeguarding AI-driven interfaces and preventing unintended actions or data leaks. |
| SK.SEC.002 | Data leakage prevention | Data leakage prevention in AI systems involves implementing controls to stop sensitive or confidential information from being exposed through model outputs or logs. This skill is crucial for compliance, privacy, and protecting organizational data assets. |
| SK.SEC.003 | Output security (XSS, injection) | Involves understanding and mitigating security risks such as cross-site scripting (XSS) and injection attacks that can be present in AI-generated outputs. This skill is important to prevent exploitation of vulnerabilities that could compromise user data or system integrity. |
| SK.SEC.010 | Agent permission design | Focuses on defining and enforcing permission boundaries for AI agents to control what actions they can perform and what data they can access. Proper agent permission design helps prevent unauthorized access and limits the potential impact of compromised agents. |
| SK.SEC.011 | Tool sandboxing | Entails isolating tools and code execution environments to prevent untrusted or potentially harmful code from affecting other systems or data. Tool sandboxing is crucial for safely integrating third-party tools or running code generated by AI. |
| SK.SEC.012 | Red teaming basics | Covers the basics of red teaming, which involves simulating attacks on AI systems to identify vulnerabilities and improve defenses. This proactive approach helps organizations anticipate and address security threats before they can be exploited. |
| SK.SEC.013 | AI supply chain security & model provenance | Understands the importance of securing the AI supply chain and tracking model provenance, including setting policies for approved sources, provenance verification, and regular security assessments. This skill protects organizations from risks associated with third-party AI components. |

## Synthetic Data & Flywheel

| id | name | draft description |
|---|---|---|
| SK.SYNTH.000 | Synthetic data generation concepts & use cases | Applies methods for generating synthetic data to augment training datasets, supporting model development while maintaining data quality and governance standards. |
| SK.SYNTH.001 | Data flywheel design & self-improvement loops | Designs systems that continuously collect, label, and use data to improve AI models, aligning incentives and processes to create self-reinforcing improvement loops. |
| SK.SYNTH.002 | Knowledge distillation & model compression | This skill involves techniques for reducing the size and complexity of AI models while maintaining their performance, making them more efficient to deploy and operate. It is important for optimizing resource usage and cost when running AI systems at scale. |
| SK.SYNTH.003 | Benchmark contamination & eval data hygiene | This skill covers methods for ensuring that evaluation datasets remain uncontaminated by training data and are properly maintained. Maintaining data hygiene is crucial for obtaining accurate, unbiased benchmarks of AI model performance. |

## Technical Prerequisites

| id | name | draft description |
|---|---|---|
| SK.PRQ.000 | Command line basics | Operates a command line terminal to navigate files, run programs, and automate tasks, which is foundational for technical work and interacting with many AI tools. |
| SK.PRQ.001 | Version control (Git basics) | Uses version control systems like Git to track code changes, collaborate with others, and manage software development projects efficiently. |
| SK.PRQ.010 | Python basics | Writes basic Python code to automate tasks, analyze data, or build simple applications, which is a core skill for many AI and data science workflows. |
| SK.PRQ.011 | Data handling (Pandas/NumPy) | Manipulates and analyzes data using Python libraries such as Pandas and NumPy, enabling efficient data cleaning, transformation, and exploration. |
| SK.PRQ.012 | JavaScript/TypeScript basics | Writes JavaScript or TypeScript code to build interactive web applications or scripts, which is essential for integrating AI features into web-based products. |
| SK.PRQ.013 | SQL fundamentals | Involves understanding how to write and execute SQL queries to retrieve, update, and manage data in relational databases, which is essential for working with structured data and integrating AI solutions with existing data systems. |
| SK.PRQ.020 | REST API basics | Covers the principles of how REST APIs enable communication between software applications over the web, which is crucial for connecting AI models and services to other systems and workflows. |
| SK.PRQ.021 | Authentication (OAuth, tokens) | Focuses on methods for verifying user identity and granting access using protocols like OAuth and token-based authentication, which is vital for securing AI applications and protecting sensitive data. |
| SK.PRQ.022 | Backend service fundamentals | Entails understanding how backend services operate, including handling requests, processing data, and serving responses, which is necessary for deploying and scaling AI-powered applications. |
| SK.PRQ.030 | Cloud primitives (compute, storage) | Involves knowledge of basic cloud computing resources such as virtual machines (compute) and object storage, which is important for deploying, scaling, and managing AI workloads efficiently. |
| SK.PRQ.031 | Secrets management | Covers techniques for securely storing and managing sensitive information like API keys and passwords, which is critical for protecting AI systems from unauthorized access and data breaches. |
| SK.PRQ.032 | CI/CD concepts | Involves understanding continuous integration and continuous deployment (CI/CD) practices, which automate software testing and delivery, ensuring reliable and rapid updates to AI applications. |

## Tools & Frameworks

| id | name | draft description |
|---|---|---|
| SK.TOOL.000 | AI tool landscape overview | Provides an overview of the current landscape of AI tools and frameworks available for different tasks and industries. Familiarity with the tool landscape helps users select the best solutions for their needs. |
| SK.TOOL.001 | ChatGPT/Claude/Gemini usage | Covers the use of popular chatbot-style AI assistants like ChatGPT, Claude, and Gemini for tasks such as drafting text, answering questions, or automating workflows. Proficiency in these tools can boost productivity and streamline communication. |
| SK.TOOL.002 | AI coding assistants (Copilot) | Involves using AI-powered coding assistants, such as GitHub Copilot, to generate code, suggest improvements, and automate repetitive programming tasks. This skill helps developers write code more efficiently and reduce errors. |
| SK.TOOL.003 | Image generation tools (Midjourney, DALL-E) | Uses AI-powered tools to generate images from text prompts, enabling rapid creation of visual content for presentations, marketing, or design projects. |
| SK.TOOL.010 | LangChain/LlamaIndex concepts | Understands frameworks like LangChain and LlamaIndex that help build applications connecting language models to external data and tools, which is essential for developing advanced AI workflows. |
| SK.TOOL.011 | Hugging Face ecosystem | Navigates the Hugging Face ecosystem to access, fine-tune, and deploy state-of-the-art AI models, making it easier to integrate cutting-edge machine learning into projects. |
| SK.TOOL.020 | API key management | Manages API keys securely to control access to AI services and protect sensitive credentials, which is critical for maintaining security and compliance in AI-powered applications. |
| SK.TOOL.021 | Provider selection criteria | Evaluates and compares AI service providers based on factors like cost, performance, reliability, and compliance, ensuring the best fit for organizational needs and risk management. |
| SK.TOOL.030 | Docker for AI apps | Uses Docker to package and run AI applications in isolated containers, enabling consistent deployment and easier scaling across different environments. |
| SK.TOOL.031 | Kubernetes awareness | Understands the basics of Kubernetes for orchestrating containerized AI workloads, which is important for deploying and managing scalable AI systems in production. |
| SK.TOOL.032 | Claude Code & CLI coding agents | Leverages command-line AI coding agents like Claude Code to automate coding tasks and streamline software development directly from the terminal. |
| SK.TOOL.033 | Agentic IDEs (Cursor, Windsurf) | Works with AI-native integrated development environments (IDEs) that use agentic features to automate coding, debugging, and workflow management for developers. |
| SK.TOOL.034 | Deep research tools (Perplexity, ChatGPT DR) | Uses AI-powered research tools to synthesize information from multiple sources, accelerating the process of gathering and analyzing complex information for decision-making. |

## Voice AI

| id | name | draft description |
|---|---|---|
| SK.VOICE.000 | Real-time voice model concepts (GPT-4o RT, Gemini Live) | Understands the architecture and operational considerations of real-time voice AI models, enabling informed decisions about platform selection, latency management, and compliance for voice-enabled applications. |
| SK.VOICE.001 | Voice pipeline design (VAD, STT, TTS integration) | Designs modular voice processing pipelines that integrate voice activity detection, speech-to-text, and text-to-speech components, allowing flexible configuration for different languages and use cases. |
| SK.VOICE.002 | Latency & turn-taking optimization for voice apps | Optimizes the responsiveness and conversational flow of voice applications by minimizing latency and managing turn-taking, using infrastructure and deployment strategies tailored to user needs. |
| SK.VOICE.003 | Multilingual voice robustness & accent handling | Ensures voice AI systems perform well across multiple languages and accents, addressing regional compliance and reducing bias to support diverse user populations. |
| SK.VOICE.004 | Voice agent security & spoofing risk mitigation | Implements security measures and risk mitigation strategies for voice agents, including speaker verification and usage policies, to prevent spoofing and unauthorized actions. |
