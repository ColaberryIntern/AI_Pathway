"""Batch test: 50 random profiles (25 technical, 25 non-technical) with full curriculum generation."""
import httpx
import asyncio
import json
import random
from datetime import datetime

BASE = "http://95.216.199.47:3000/api"

# ── Profile Templates ──────────────────────────────────────────────

TECHNICAL_PROFILES = [
    {"name": "Marcus Chen", "current_role": "Senior Software Engineer", "industry": "FinTech", "experience_years": 8, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "Full-stack engineer with 8 years building trading platforms. Python, Java, React, AWS. Led team of 5 developers.", "technical_skills": ["Python", "Java", "React", "AWS", "PostgreSQL", "Docker", "Kubernetes"], "soft_skills": ["Team leadership", "Code review", "Technical mentoring"]},
    {"name": "Priya Sharma", "current_role": "Data Scientist", "industry": "Healthcare", "experience_years": 5, "technical_background": "Professional developer", "ai_exposure_level": "Advanced", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "Data scientist specializing in clinical analytics. Built ML models for patient outcome prediction. Python, R, TensorFlow.", "technical_skills": ["Python", "R", "TensorFlow", "SQL", "Tableau", "Statistical modeling", "Clinical data analysis"], "soft_skills": ["Research presentation", "Cross-functional collaboration"]},
    {"name": "Jake Morrison", "current_role": "DevOps Engineer", "industry": "E-commerce", "experience_years": 6, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "DevOps engineer managing CI/CD pipelines and cloud infrastructure for high-traffic e-commerce platform. AWS, Terraform, Docker.", "technical_skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Jenkins", "Python", "Bash scripting"], "soft_skills": ["Incident response", "Documentation"]},
    {"name": "Sofia Rodriguez", "current_role": "Machine Learning Engineer", "industry": "Autonomous Vehicles", "experience_years": 4, "technical_background": "Professional developer", "ai_exposure_level": "Advanced", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "ML engineer building perception models for self-driving cars. PyTorch, computer vision, sensor fusion.", "technical_skills": ["PyTorch", "Python", "Computer Vision", "CUDA", "C++", "ROS", "MLOps"], "soft_skills": ["Technical writing", "Research"]},
    {"name": "David Kim", "current_role": "Backend Developer", "industry": "SaaS", "experience_years": 3, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Backend developer building RESTful APIs and microservices. Node.js, PostgreSQL, Redis.", "technical_skills": ["Node.js", "TypeScript", "PostgreSQL", "Redis", "Docker", "GraphQL"], "soft_skills": ["Agile methodology", "Pair programming"]},
    {"name": "Aisha Patel", "current_role": "Security Engineer", "industry": "Banking", "experience_years": 7, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "OpenAI API / Anthropic API"], "summary": "Application security engineer for major bank. Penetration testing, SAST/DAST, compliance frameworks.", "technical_skills": ["Penetration testing", "OWASP", "Python", "Burp Suite", "AWS Security", "SOC 2", "PCI DSS"], "soft_skills": ["Risk assessment", "Security training"]},
    {"name": "Tom Williams", "current_role": "Full Stack Developer", "industry": "EdTech", "experience_years": 5, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "Full stack developer building learning platforms. React, Node.js, MongoDB. Experience with LMS integrations.", "technical_skills": ["React", "Node.js", "MongoDB", "TypeScript", "AWS", "GraphQL"], "soft_skills": ["UX thinking", "Agile"]},
    {"name": "Elena Volkov", "current_role": "Data Engineer", "industry": "Retail", "experience_years": 6, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Data engineer building ETL pipelines and data warehouses for retail analytics. Spark, Airflow, Snowflake.", "technical_skills": ["Apache Spark", "Airflow", "Snowflake", "Python", "SQL", "dbt", "Kafka"], "soft_skills": ["Data governance", "Stakeholder management"]},
    {"name": "Chris Johnson", "current_role": "iOS Developer", "industry": "Health & Fitness", "experience_years": 4, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "iOS developer building health tracking apps. Swift, SwiftUI, HealthKit, CoreML.", "technical_skills": ["Swift", "SwiftUI", "CoreML", "HealthKit", "Xcode", "Git"], "soft_skills": ["UI design", "User testing"]},
    {"name": "Nina Okafor", "current_role": "QA Automation Engineer", "industry": "Insurance", "experience_years": 5, "technical_background": "Some coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "QA automation engineer building test frameworks for insurance claim processing systems. Selenium, Python, CI/CD.", "technical_skills": ["Selenium", "Python", "Jest", "Cypress", "Jenkins", "SQL", "Postman"], "soft_skills": ["Test planning", "Bug reporting"]},
    {"name": "Ryan Foster", "current_role": "Platform Engineer", "industry": "Media & Entertainment", "experience_years": 7, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "Platform engineer scaling video streaming infrastructure. Kubernetes, Go, distributed systems.", "technical_skills": ["Go", "Kubernetes", "gRPC", "Redis", "Kafka", "Prometheus", "Terraform"], "soft_skills": ["System design", "On-call management"]},
    {"name": "Lisa Zhang", "current_role": "AI Research Engineer", "industry": "NLP/Language Tech", "experience_years": 3, "technical_background": "Professional developer", "ai_exposure_level": "Advanced", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "AI research engineer working on large language models. Fine-tuning, RLHF, evaluation frameworks.", "technical_skills": ["PyTorch", "Transformers", "Python", "CUDA", "Weights & Biases", "HuggingFace"], "soft_skills": ["Research papers", "Conference presentations"]},
    {"name": "Omar Hassan", "current_role": "Solutions Architect", "industry": "Cloud Computing", "experience_years": 10, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "OpenAI API / Anthropic API"], "summary": "AWS Solutions Architect designing enterprise cloud migrations. 10 years across startups and Fortune 500.", "technical_skills": ["AWS", "Azure", "System design", "Microservices", "Serverless", "IaC", "Python"], "soft_skills": ["Client consulting", "Technical presentations", "Team mentoring"]},
    {"name": "Maria Santos", "current_role": "Embedded Systems Engineer", "industry": "IoT/Smart Home", "experience_years": 6, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Embedded systems engineer building firmware for smart home devices. C, C++, RTOS, Bluetooth LE.", "technical_skills": ["C", "C++", "RTOS", "Bluetooth LE", "PCB design", "Python", "Linux"], "soft_skills": ["Hardware-software integration", "Technical documentation"]},
    {"name": "Alex Turner", "current_role": "Frontend Lead", "industry": "Digital Agency", "experience_years": 8, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "Midjourney / DALL-E"], "summary": "Frontend lead managing team of 4 building client websites and web apps. React, Next.js, design systems.", "technical_skills": ["React", "Next.js", "TypeScript", "CSS", "Figma", "Storybook", "Jest"], "soft_skills": ["Team management", "Client communication", "Design thinking"]},
    {"name": "Kevin Park", "current_role": "Database Administrator", "industry": "Government", "experience_years": 12, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Senior DBA managing Oracle and PostgreSQL databases for federal government systems. Performance tuning, disaster recovery.", "technical_skills": ["Oracle", "PostgreSQL", "SQL Server", "PL/SQL", "Performance tuning", "Backup/Recovery"], "soft_skills": ["Compliance documentation", "Change management"]},
    {"name": "Sarah Mitchell", "current_role": "Robotics Software Engineer", "industry": "Manufacturing", "experience_years": 4, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "Robotics software engineer programming industrial robots for manufacturing lines. ROS2, Python, computer vision.", "technical_skills": ["ROS2", "Python", "C++", "Computer Vision", "OpenCV", "Motion Planning"], "soft_skills": ["Safety protocols", "Cross-team collaboration"]},
    {"name": "James Wright", "current_role": "Blockchain Developer", "industry": "DeFi", "experience_years": 3, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "Smart contract developer building DeFi protocols. Solidity, Rust, Web3.js.", "technical_skills": ["Solidity", "Rust", "Web3.js", "Ethereum", "Hardhat", "TypeScript"], "soft_skills": ["Audit reviews", "Documentation"]},
    {"name": "Diana Chen", "current_role": "Site Reliability Engineer", "industry": "Social Media", "experience_years": 5, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "SRE maintaining 99.99% uptime for social media platform serving 50M users. Kubernetes, observability, incident response.", "technical_skills": ["Kubernetes", "Prometheus", "Grafana", "Go", "Python", "Terraform", "PagerDuty"], "soft_skills": ["Incident command", "Postmortem facilitation"]},
    {"name": "Brian Adams", "current_role": "Game Developer", "industry": "Gaming", "experience_years": 6, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"], "summary": "Game developer building multiplayer experiences. Unity, C#, networking, procedural generation.", "technical_skills": ["Unity", "C#", "Networking", "Shader programming", "Git", "Blender"], "soft_skills": ["Game design", "Playtesting"]},
    {"name": "Rachel Green", "current_role": "Bioinformatics Scientist", "industry": "Pharma", "experience_years": 7, "technical_background": "Professional developer", "ai_exposure_level": "Advanced", "tools_used": ["ChatGPT / Claude / Gemini", "OpenAI API / Anthropic API"], "summary": "Bioinformatics scientist developing genomic analysis pipelines. Python, R, ML for drug discovery.", "technical_skills": ["Python", "R", "Bioinformatics", "Machine Learning", "AWS", "Docker", "Nextflow"], "soft_skills": ["Scientific communication", "Regulatory compliance"]},
    {"name": "Carlos Mendez", "current_role": "API Developer", "industry": "Logistics", "experience_years": 4, "technical_background": "Professional developer", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "API developer building integration layers for logistics tracking. Python, FastAPI, message queues.", "technical_skills": ["Python", "FastAPI", "RabbitMQ", "PostgreSQL", "Docker", "REST APIs"], "soft_skills": ["API documentation", "Partner integrations"]},
    {"name": "Hannah Lee", "current_role": "Computer Vision Engineer", "industry": "Agriculture", "experience_years": 3, "technical_background": "Professional developer", "ai_exposure_level": "Advanced", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "CV engineer building crop disease detection models using drone imagery. PyTorch, YOLO, edge deployment.", "technical_skills": ["PyTorch", "YOLO", "Python", "OpenCV", "Edge AI", "TensorRT", "Docker"], "soft_skills": ["Field testing", "Research"]},
    {"name": "Mike O'Brien", "current_role": "Technical Lead", "industry": "Real Estate Tech", "experience_years": 9, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "Tech lead managing property search platform. Full stack, system design, team of 6. React, Python, Elasticsearch.", "technical_skills": ["Python", "React", "Elasticsearch", "PostgreSQL", "AWS", "System Design", "Docker"], "soft_skills": ["Team leadership", "Architecture reviews", "Hiring"]},
    {"name": "Yuki Tanaka", "current_role": "NLP Engineer", "industry": "Legal Tech", "experience_years": 4, "technical_background": "Professional developer", "ai_exposure_level": "Advanced", "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"], "summary": "NLP engineer building contract analysis and legal document processing tools. Transformers, spaCy, fine-tuning.", "technical_skills": ["Python", "Transformers", "spaCy", "FastAPI", "Docker", "HuggingFace", "LangChain"], "soft_skills": ["Legal domain knowledge", "Technical writing"]},
]

NON_TECHNICAL_PROFILES = [
    {"name": "Jennifer Campbell", "current_role": "Content Editor", "industry": "Corporate Communications", "experience_years": 9, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Strategic communications professional with 9+ years in Fortune 100. Translates complex technical concepts into accessible content.", "technical_skills": ["Executive Communications", "Content Strategy", "Keyword Research"], "soft_skills": ["Mentoring", "Training", "Leadership"]},
    {"name": "Amanda Foster", "current_role": "Marketing Director", "industry": "Consumer Goods", "experience_years": 12, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Marketing director leading brand strategy for CPG company. 12 years of campaign management, market research, and team leadership.", "technical_skills": ["Brand Strategy", "Market Research", "Campaign Management", "Google Analytics"], "soft_skills": ["Team leadership", "Budget management", "Presentation skills"]},
    {"name": "Robert Chen", "current_role": "HR Business Partner", "industry": "Technology", "experience_years": 8, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "HR business partner supporting engineering teams. Talent acquisition, performance management, organizational design.", "technical_skills": ["HRIS Systems", "Talent Analytics", "Compensation Benchmarking"], "soft_skills": ["Employee relations", "Conflict resolution", "Change management"]},
    {"name": "Lisa Park", "current_role": "Financial Analyst", "industry": "Investment Banking", "experience_years": 5, "technical_background": "Some coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Financial analyst building DCF models and pitch books. Excel power user, some VBA macros.", "technical_skills": ["Financial Modeling", "Excel/VBA", "Bloomberg Terminal", "PowerPoint"], "soft_skills": ["Client presentations", "Detail orientation"]},
    {"name": "Michael Brown", "current_role": "Operations Manager", "industry": "Manufacturing", "experience_years": 15, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Operations manager overseeing 200-person manufacturing plant. Lean Six Sigma, supply chain optimization.", "technical_skills": ["Lean Six Sigma", "ERP Systems", "Supply Chain Management", "Quality Control"], "soft_skills": ["Team management", "Process improvement", "Safety compliance"]},
    {"name": "Sarah Johnson", "current_role": "Executive Assistant", "industry": "Law Firm", "experience_years": 10, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Executive assistant to managing partner at top 50 law firm. Calendar management, travel, client communications.", "technical_skills": ["Microsoft Office", "Document Management", "Travel Planning"], "soft_skills": ["Discretion", "Organization", "Multi-tasking"]},
    {"name": "Daniel Lee", "current_role": "Sales Director", "industry": "B2B Software", "experience_years": 11, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Sales director managing $20M pipeline. Enterprise sales, solution selling, team of 8 account executives.", "technical_skills": ["Salesforce CRM", "Sales Forecasting", "Pipeline Management"], "soft_skills": ["Negotiation", "Relationship building", "Team coaching"]},
    {"name": "Emily Watson", "current_role": "UX Researcher", "industry": "Consumer Tech", "experience_years": 6, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "Midjourney / DALL-E"], "summary": "UX researcher conducting user interviews, usability tests, and survey design. Figma, Maze, UserTesting.", "technical_skills": ["User Interviews", "Usability Testing", "Survey Design", "Figma", "Maze"], "soft_skills": ["Empathy", "Storytelling", "Data synthesis"]},
    {"name": "James Wilson", "current_role": "Supply Chain Analyst", "industry": "Retail", "experience_years": 4, "technical_background": "Some coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Supply chain analyst optimizing inventory and logistics. Excel, Tableau, some SQL queries.", "technical_skills": ["Tableau", "Excel", "SQL basics", "SAP", "Inventory Management"], "soft_skills": ["Analytical thinking", "Vendor relations"]},
    {"name": "Karen Thompson", "current_role": "Nurse Manager", "industry": "Healthcare", "experience_years": 14, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Nurse manager overseeing ICU unit with 30 nurses. Clinical protocols, patient safety, staff scheduling.", "technical_skills": ["Clinical Protocols", "EHR Systems", "Staff Scheduling", "Patient Safety"], "soft_skills": ["Clinical leadership", "Crisis management", "Patient advocacy"]},
    {"name": "David Martinez", "current_role": "Real Estate Agent", "industry": "Commercial Real Estate", "experience_years": 8, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Commercial real estate agent specializing in office leasing. $50M in transactions annually.", "technical_skills": ["MLS Systems", "Market Analysis", "Contract Negotiation"], "soft_skills": ["Client relations", "Negotiation", "Networking"]},
    {"name": "Rachel Adams", "current_role": "Project Manager", "industry": "Construction", "experience_years": 7, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Project manager overseeing commercial construction projects $5-50M. Scheduling, budgets, subcontractor management.", "technical_skills": ["MS Project", "Procore", "Budget Management", "Blueprint Reading"], "soft_skills": ["Contractor management", "Safety compliance", "Client communication"]},
    {"name": "Michelle Kim", "current_role": "L&D Manager", "industry": "Consulting", "experience_years": 9, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "Midjourney / DALL-E"], "summary": "Learning & Development manager designing training programs for Big 4 consulting firm. Instructional design, facilitation.", "technical_skills": ["Instructional Design", "LMS Administration", "Articulate Storyline", "Needs Assessment"], "soft_skills": ["Facilitation", "Curriculum design", "Executive coaching"]},
    {"name": "Steve Clark", "current_role": "Account Manager", "industry": "Advertising", "experience_years": 6, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Account manager at advertising agency managing $5M portfolio. Client relationships, campaign oversight, media buying.", "technical_skills": ["Media Planning", "Campaign Analytics", "Google Ads", "Social Media Management"], "soft_skills": ["Client management", "Creative briefing", "Budget tracking"]},
    {"name": "Laura Nguyen", "current_role": "Compliance Officer", "industry": "Financial Services", "experience_years": 10, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Compliance officer managing regulatory requirements for investment firm. SEC, FINRA, AML/KYC compliance.", "technical_skills": ["Regulatory Compliance", "AML/KYC", "Risk Assessment", "Audit Management"], "soft_skills": ["Policy writing", "Regulatory liaison", "Training delivery"]},
    {"name": "Paul Rivera", "current_role": "Curriculum Designer", "industry": "Higher Education", "experience_years": 8, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini", "Midjourney / DALL-E"], "summary": "Curriculum designer for university business school. Developing online MBA courses, assessment design.", "technical_skills": ["Canvas LMS", "Articulate", "Assessment Design", "Bloom's Taxonomy"], "soft_skills": ["Faculty collaboration", "Pedagogical research", "Content curation"]},
    {"name": "Jessica Taylor", "current_role": "Event Director", "industry": "Hospitality", "experience_years": 11, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Event director managing 200+ corporate events annually. Venue selection, vendor management, logistics.", "technical_skills": ["Event Management Software", "Budget Management", "Vendor Management"], "soft_skills": ["Logistics planning", "Client relations", "Crisis management"]},
    {"name": "Andrew Hayes", "current_role": "Policy Analyst", "industry": "Government", "experience_years": 6, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Policy analyst at federal agency. Researching regulations, drafting policy briefs, stakeholder engagement.", "technical_skills": ["Policy Research", "Legislative Analysis", "Report Writing", "Data Visualization"], "soft_skills": ["Stakeholder engagement", "Public speaking", "Research methodology"]},
    {"name": "Megan Scott", "current_role": "Brand Manager", "industry": "Fashion", "experience_years": 5, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini", "Midjourney / DALL-E"], "summary": "Brand manager for luxury fashion label. Product launches, influencer partnerships, brand positioning.", "technical_skills": ["Brand Strategy", "Social Media", "Influencer Marketing", "Adobe Creative Suite"], "soft_skills": ["Creative direction", "Trend analysis", "Vendor management"]},
    {"name": "Thomas Wright", "current_role": "Clinical Research Coordinator", "industry": "Pharmaceuticals", "experience_years": 4, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Clinical research coordinator managing Phase III drug trials. IRB submissions, patient recruitment, data collection.", "technical_skills": ["Clinical Trial Management", "REDCap", "GCP Compliance", "IRB Submissions"], "soft_skills": ["Patient communication", "Regulatory compliance", "Detail orientation"]},
    {"name": "Nicole Baker", "current_role": "Customer Success Manager", "industry": "SaaS", "experience_years": 5, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Customer success manager handling enterprise accounts. Onboarding, retention, upselling. $3M ARR portfolio.", "technical_skills": ["Gainsight", "Salesforce", "Customer Health Scoring", "Churn Analysis"], "soft_skills": ["Relationship management", "Product advocacy", "Executive presentations"]},
    {"name": "Greg Phillips", "current_role": "Procurement Director", "industry": "Aerospace", "experience_years": 15, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Procurement director managing $100M annual spend for aerospace manufacturer. Strategic sourcing, supplier quality.", "technical_skills": ["SAP Procurement", "Strategic Sourcing", "Supplier Auditing", "Contract Management"], "soft_skills": ["Negotiation", "Supply chain risk", "Vendor development"]},
    {"name": "Amy Collins", "current_role": "Social Worker", "industry": "Non-Profit", "experience_years": 7, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Licensed social worker managing case load of 40 families. Crisis intervention, resource coordination, advocacy.", "technical_skills": ["Case Management Systems", "Assessment Tools", "Documentation"], "soft_skills": ["Crisis intervention", "Empathy", "Community advocacy", "Cultural competency"]},
    {"name": "Mark Davis", "current_role": "Logistics Coordinator", "industry": "Food Distribution", "experience_years": 6, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini"], "summary": "Logistics coordinator managing cold chain distribution for regional food distributor. Route optimization, fleet management.", "technical_skills": ["TMS Systems", "Route Planning", "Fleet Management", "HACCP Compliance"], "soft_skills": ["Driver coordination", "Problem solving", "Vendor relations"]},
    {"name": "Diane Foster", "current_role": "Interior Designer", "industry": "Architecture & Design", "experience_years": 10, "technical_background": "No coding experience", "ai_exposure_level": "Basic", "tools_used": ["ChatGPT / Claude / Gemini", "Midjourney / DALL-E"], "summary": "Senior interior designer specializing in commercial office spaces. AutoCAD, space planning, sustainability.", "technical_skills": ["AutoCAD", "SketchUp", "Space Planning", "Material Selection", "LEED"], "soft_skills": ["Client consultation", "Project management", "Vendor coordination"]},
]

# ── Job Descriptions ───────────────────────────────────────────────

TECHNICAL_JDS = [
    "AI/ML Engineer - Design and implement machine learning pipelines for production systems. Build and optimize model training infrastructure. Deploy models using containerized microservices. Monitor model performance and implement retraining strategies. Required: Python, PyTorch/TensorFlow, Docker, Kubernetes, AWS/GCP. 3+ years ML engineering experience.",
    "AI Solutions Architect - Lead the design of enterprise AI solutions integrating LLMs and agentic systems. Translate business requirements into technical architectures. Evaluate and select AI platforms. Build proof-of-concepts. Required: System design, cloud architecture, API development, LLM integration, prompt engineering.",
    "AI Platform Engineer - Build internal AI/ML platform for data science teams. Design feature stores, model registries, and experiment tracking. Implement CI/CD for ML pipelines. Required: Python, Kubernetes, MLflow, Airflow, cloud platforms.",
    "AI Security Engineer - Develop security frameworks for AI systems. Implement prompt injection defenses, model access controls, and data privacy measures. Audit AI systems for vulnerabilities. Required: Security engineering, Python, LLM security, threat modeling.",
    "AI Data Engineer - Build data pipelines feeding AI/ML models. Design real-time streaming architectures. Implement data quality monitoring. Optimize storage for vector embeddings. Required: Spark, Kafka, Python, SQL, vector databases.",
    "AI DevOps Engineer - Automate AI model deployment and monitoring. Build GPU cluster management. Implement A/B testing for models. Required: Kubernetes, Docker, Terraform, Python, GPU orchestration, monitoring.",
    "Conversational AI Developer - Build chatbots and virtual assistants using LLMs. Design dialog flows, implement RAG systems, fine-tune models for specific domains. Required: Python, LangChain, vector databases, prompt engineering.",
    "Computer Vision AI Engineer - Develop image and video analysis systems using deep learning. Object detection, segmentation, OCR. Deploy models on edge devices. Required: PyTorch, OpenCV, ONNX, Python, edge deployment.",
    "AI Infrastructure Engineer - Scale GPU computing infrastructure for model training. Optimize distributed training. Manage model serving at scale. Required: CUDA, distributed computing, Kubernetes, Python, cloud GPUs.",
    "Full Stack AI Developer - Build end-to-end AI-powered applications. Frontend with AI features, backend API integration, LLM orchestration. Required: React, Python/FastAPI, LLM APIs, prompt engineering, database design.",
    "AI Product Engineer - Bridge product and engineering for AI features. Implement AI-powered recommendations, search, and personalization. A/B test AI features. Required: Python, ML basics, product analytics, API development.",
    "Robotics AI Engineer - Develop AI systems for autonomous robots. Reinforcement learning, path planning, sensor fusion. Required: ROS, Python, C++, reinforcement learning, computer vision.",
    "NLP Engineer - Build natural language understanding and generation systems. Text classification, entity extraction, summarization. Required: Transformers, spaCy, Python, fine-tuning, evaluation metrics.",
    "AI Quality Engineer - Design testing frameworks for AI systems. Evaluate model accuracy, bias, and robustness. Implement continuous evaluation. Required: Python, ML testing, statistical analysis, CI/CD.",
    "AI Backend Engineer - Build scalable APIs serving AI models. Implement caching, load balancing, and failover for model inference. Required: Python, FastAPI/Flask, Redis, Docker, model serving.",
    "MLOps Engineer - Implement ML lifecycle management. Model versioning, experiment tracking, automated retraining. Required: MLflow, Kubeflow, Python, Docker, CI/CD.",
    "AI Research Engineer - Implement and evaluate novel ML techniques. Reproduce papers, run experiments, publish findings. Required: PyTorch, Python, research methodology, statistics.",
    "Generative AI Engineer - Build applications using generative AI. Image generation, text synthesis, code generation tools. Required: Stable Diffusion, LLM APIs, Python, prompt engineering.",
    "AI Edge Engineer - Deploy AI models on mobile and IoT devices. Model compression, quantization, on-device inference. Required: TensorFlow Lite, ONNX, Python, C++, mobile development.",
    "AI Integration Specialist - Connect AI services with enterprise systems. Build middleware, data connectors, and API gateways for AI platforms. Required: Python, REST APIs, cloud platforms, enterprise integration patterns.",
    "Search & Recommendation Engineer - Build AI-powered search and recommendation systems. Vector search, collaborative filtering, content-based recommendations. Required: Elasticsearch, Python, ML, embeddings.",
    "AI Observability Engineer - Monitor AI systems in production. Build dashboards for model drift, latency, and accuracy. Alert on anomalies. Required: Prometheus, Grafana, Python, ML monitoring.",
    "Autonomous Systems Engineer - Develop decision-making systems for autonomous vehicles/drones. Reinforcement learning, simulation, safety verification. Required: Python, C++, simulation frameworks, safety standards.",
    "AI Compliance Engineer - Implement AI governance frameworks. Model documentation, bias auditing, regulatory compliance. Required: Python, ML fairness tools, documentation, regulatory knowledge.",
    "Voice AI Engineer - Build speech recognition and synthesis systems. ASR, TTS, speaker identification. Required: Python, speech processing, deep learning, audio engineering.",
]

NON_TECHNICAL_JDS = [
    "AI Content Editor - Evaluate and edit AI-generated content for accuracy, tone, and clarity. Collaborate with developers to refine content generation algorithms. Ensure content aligns with brand voice. Develop AI content disclosure guidelines. Review AI outputs for bias and factual accuracy.",
    "AI Product Manager - Define product strategy for AI-powered features. Work with engineering to prioritize AI capabilities. Measure AI feature impact. Manage stakeholder expectations around AI limitations. Required: Product management experience, basic AI/ML understanding.",
    "AI Ethics Officer - Develop and implement responsible AI policies. Review AI systems for bias and fairness. Create ethical guidelines for AI deployment. Train employees on responsible AI use. Required: Ethics/compliance background, policy writing.",
    "AI Training Specialist - Design and deliver AI literacy training programs. Create workshops for non-technical employees. Develop training materials explaining AI concepts. Evaluate training effectiveness. Required: L&D experience, instructional design.",
    "AI Project Coordinator - Coordinate AI implementation projects across departments. Track milestones, manage budgets, facilitate cross-team communication. Required: Project management, stakeholder communication.",
    "AI Marketing Strategist - Develop marketing strategies leveraging AI tools. Use AI for content personalization, audience targeting, campaign optimization. Measure AI-driven campaign ROI. Required: Marketing experience, data-driven decision making.",
    "AI Customer Experience Manager - Redesign customer journeys using AI touchpoints. Implement AI chatbots, recommendation engines, personalized communications. Measure customer satisfaction. Required: CX experience, basic AI understanding.",
    "AI Change Manager - Lead organizational change initiatives for AI adoption. Manage resistance, design communication plans, build AI champions network. Required: Change management, organizational development.",
    "AI Business Analyst - Analyze business processes for AI automation opportunities. Document requirements, create ROI models, support implementation. Required: Business analysis, process mapping, basic data analysis.",
    "AI Communications Director - Lead internal and external communications about AI initiatives. Write thought leadership content, manage media inquiries, position company as AI leader. Required: Communications/PR experience.",
    "AI Talent Acquisition Specialist - Recruit AI/ML talent. Understand technical roles, screen candidates, partner with hiring managers. Required: Technical recruiting experience, basic AI terminology.",
    "AI Governance Analyst - Monitor AI systems for compliance with regulations and internal policies. Document model decisions, maintain audit trails, report to leadership. Required: Governance/audit experience.",
    "Healthcare AI Coordinator - Coordinate AI implementation in clinical settings. Liaise between medical staff and IT. Ensure AI tools meet clinical workflow needs. Required: Healthcare operations, clinical knowledge.",
    "AI Sales Enablement Manager - Train sales teams on AI product capabilities. Create demo scripts, competitive positioning, objection handling for AI products. Required: Sales training, product knowledge.",
    "AI Partnership Manager - Identify and manage partnerships with AI vendors and platforms. Evaluate AI tools, negotiate contracts, oversee integrations. Required: Partner management, vendor evaluation.",
    "Legal AI Specialist - Review AI contracts, licensing, and IP issues. Advise on AI regulation compliance. Draft AI usage policies. Required: Legal background, contract review, regulatory knowledge.",
    "AI Strategy Consultant - Advise clients on AI transformation roadmaps. Assess AI readiness, identify use cases, develop implementation plans. Required: Strategy consulting, business acumen.",
    "Sustainability AI Analyst - Use AI to analyze and report on ESG metrics. Implement AI-powered sustainability tracking. Required: Sustainability knowledge, reporting, data analysis basics.",
    "AI Education Program Director - Design university-level AI curriculum for non-CS students. Develop practical AI literacy courses. Required: Higher education, curriculum design, pedagogy.",
    "AI Operations Analyst - Monitor AI system performance and usage. Generate reports, identify optimization opportunities, support troubleshooting. Required: Operations analysis, reporting, basic technical aptitude.",
    "AI Procurement Specialist - Evaluate and procure AI tools and platforms. Assess vendor capabilities, negotiate pricing, manage vendor relationships. Required: Procurement, vendor management.",
    "Creative AI Director - Lead creative teams using AI tools (Midjourney, DALL-E, etc.) for visual content. Define AI usage guidelines for creative work. Required: Creative direction, art direction, brand management.",
    "AI Risk Analyst - Assess risks associated with AI deployments. Model failure scenarios, quantify business impact, develop mitigation strategies. Required: Risk management, analytical thinking.",
    "Patient Experience AI Lead - Implement AI solutions to improve patient experience in healthcare. Chatbots, appointment scheduling, patient feedback analysis. Required: Healthcare experience, patient advocacy.",
    "AI Curriculum Writer - Write course content teaching professionals to use AI tools. Create exercises, assessments, and practical guides. Required: Content writing, instructional design, AI tool familiarity.",
]


async def run_single(client, profile_data, jd_text, run_id):
    """Create profile, run analysis, activate path, start first lesson, return results."""
    result_data = {
        "run_id": run_id,
        "name": profile_data["name"],
        "role": profile_data["current_role"],
        "industry": profile_data["industry"],
        "technical": profile_data["technical_background"] != "No coding experience",
        "status": "pending",
    }

    try:
        # Create profile
        r = await client.post(f"{BASE}/profiles/", json={
            "name": profile_data["name"],
            "current_role": profile_data["current_role"],
            "industry": profile_data["industry"],
            "experience_years": profile_data["experience_years"],
            "ai_exposure_level": profile_data["ai_exposure_level"],
            "technical_background": profile_data["technical_background"],
            "learning_intent": f"Transition to AI role in {profile_data['industry']}",
            "target_jd_text": jd_text,
            "tools_used": profile_data["tools_used"],
            "current_profile": {
                "summary": profile_data["summary"],
                "technical_skills": profile_data["technical_skills"],
                "soft_skills": profile_data["soft_skills"],
            },
        })
        if r.status_code not in (200, 201):
            result_data["status"] = f"profile_fail:{r.status_code}"
            return result_data
        pid = r.json()["id"]
        result_data["profile_id"] = pid

        # Run analysis
        r = await client.post(f"{BASE}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": jd_text,
            "target_role": jd_text.split(" - ")[0].strip() if " - " in jd_text else "AI Professional",
            "skip_assessment": True,
        }, timeout=180)
        if r.status_code != 200:
            result_data["status"] = f"analysis_fail:{r.status_code}"
            await client.delete(f"{BASE}/profiles/{pid}")
            return result_data

        analysis = r.json()
        result_obj = analysis.get("result", {})
        path_id = analysis.get("learning_path_id")

        # Extract skills
        top10 = result_obj.get("top_10_target_skills", [])
        chapters = result_obj.get("learning_path", {}).get("chapters", [])
        result_data["top_10_skills"] = [{"id": s.get("skill_id"), "name": s.get("skill_name")} for s in top10]
        result_data["chapters"] = [
            {"skill_id": ch.get("primary_skill_id", ch.get("skill_id", "")),
             "skill_name": ch.get("primary_skill_name", ch.get("skill_name", "")),
             "current_level": ch.get("current_level", 0),
             "target_level": ch.get("target_level", 1)}
            for ch in chapters
        ]
        result_data["fit_score"] = result_obj.get("fit_score", 0)

        # Activate path
        r = await client.post(f"{BASE}/learning/{path_id}/activate")
        if r.status_code != 200:
            result_data["status"] = f"activate_fail:{r.status_code}"
            await client.delete(f"{BASE}/profiles/{pid}")
            return result_data

        act = r.json()
        modules = act.get("modules", [])
        result_data["total_lessons"] = act.get("total_lessons", 0)
        result_data["modules"] = []

        for mod in modules:
            mod_data = {
                "chapter": mod.get("chapter_number"),
                "skill_id": mod.get("skill_id"),
                "skill_name": mod.get("skill_name"),
                "lessons": [],
            }
            for lesson_info in mod.get("lesson_outline", []):
                lid = lesson_info.get("id")
                lesson_data = {
                    "lesson_number": lesson_info.get("lesson_number"),
                    "title": lesson_info.get("title"),
                    "type": lesson_info.get("type"),
                }
                # Generate first lesson of each module
                if lid and lesson_info.get("lesson_number") == 1:
                    try:
                        r = await client.post(
                            f"{BASE}/learning/{path_id}/lessons/{lid}/start",
                            timeout=120,
                        )
                        if r.status_code == 200:
                            content = r.json().get("content", {})
                            lesson_data["has_concept"] = bool(content.get("concept_snapshot"))
                            lesson_data["has_code"] = bool(content.get("code_examples"))
                            lesson_data["has_knowledge_checks"] = len(content.get("knowledge_checks", []))
                            lesson_data["has_reflection"] = len(content.get("reflection_questions", []))
                            lesson_data["has_implementation"] = bool(content.get("implementation_task"))
                            lesson_data["concept_preview"] = (content.get("concept_snapshot") or "")[:200]
                        else:
                            lesson_data["error"] = f"start_fail:{r.status_code}"
                    except Exception as e:
                        lesson_data["error"] = str(e)[:80]
                mod_data["lessons"].append(lesson_data)
            result_data["modules"].append(mod_data)

        result_data["status"] = "success"

        # Cleanup
        await client.delete(f"{BASE}/profiles/{pid}")

    except Exception as e:
        result_data["status"] = f"error:{str(e)[:80]}"

    return result_data


async def main():
    random.seed(42)  # Reproducible
    all_results = []

    # Pair profiles with JDs
    tech_pairs = list(zip(TECHNICAL_PROFILES[:25], random.sample(TECHNICAL_JDS, 25)))
    nontech_pairs = list(zip(NON_TECHNICAL_PROFILES[:25], random.sample(NON_TECHNICAL_JDS, 25)))

    async with httpx.AsyncClient(timeout=180) as client:
        # Run technical profiles
        print(f"{'='*70}")
        print("RUNNING 25 TECHNICAL PROFILES")
        print(f"{'='*70}")
        for i, (profile, jd) in enumerate(tech_pairs):
            print(f"  [{i+1}/25] {profile['name']} ({profile['current_role']})...", end=" ", flush=True)
            result = await run_single(client, profile, jd, f"tech_{i+1}")
            all_results.append(result)
            status = result["status"]
            if status == "success":
                ch_count = len(result.get("chapters", []))
                lessons = result.get("total_lessons", 0)
                has_code = any(
                    l.get("has_code")
                    for m in result.get("modules", [])
                    for l in m.get("lessons", [])
                    if "has_code" in l
                )
                print(f"OK ({ch_count} chapters, {lessons} lessons, code={has_code})")
            else:
                print(f"FAIL: {status}")
                # Restart if 502
                if "502" in status:
                    import subprocess
                    subprocess.run(["ssh", "root@95.216.199.47", "cd /opt/ai-pathway && docker compose restart backend"], capture_output=True)
                    await asyncio.sleep(15)

        # Run non-technical profiles
        print(f"\n{'='*70}")
        print("RUNNING 25 NON-TECHNICAL PROFILES")
        print(f"{'='*70}")
        for i, (profile, jd) in enumerate(nontech_pairs):
            print(f"  [{i+1}/25] {profile['name']} ({profile['current_role']})...", end=" ", flush=True)
            result = await run_single(client, profile, jd, f"nontech_{i+1}")
            all_results.append(result)
            status = result["status"]
            if status == "success":
                ch_count = len(result.get("chapters", []))
                lessons = result.get("total_lessons", 0)
                has_code = any(
                    l.get("has_code")
                    for m in result.get("modules", [])
                    for l in m.get("lessons", [])
                    if "has_code" in l
                )
                print(f"OK ({ch_count} chapters, {lessons} lessons, code={has_code})")
            else:
                print(f"FAIL: {status}")
                if "502" in status:
                    import subprocess
                    subprocess.run(["ssh", "root@95.216.199.47", "cd /opt/ai-pathway && docker compose restart backend"], capture_output=True)
                    await asyncio.sleep(15)

    # Save full results
    output_path = f"../docs/batch_test_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")

    # Summary report
    print(f"\n{'='*70}")
    print("BATCH TEST SUMMARY")
    print(f"{'='*70}")

    success = [r for r in all_results if r["status"] == "success"]
    failed = [r for r in all_results if r["status"] != "success"]
    tech_success = [r for r in success if r["technical"]]
    nontech_success = [r for r in success if not r["technical"]]

    print(f"\nTotal: {len(all_results)} | Success: {len(success)} | Failed: {len(failed)}")
    print(f"Technical: {len(tech_success)}/25 | Non-technical: {len(nontech_success)}/25")

    if failed:
        print(f"\nFailures:")
        for r in failed:
            print(f"  {r['name']} ({r['role']}): {r['status']}")

    # Code examples analysis
    tech_with_code = 0
    tech_without_code = 0
    nontech_with_code = 0
    nontech_without_code = 0

    for r in success:
        has_any_code = any(
            l.get("has_code")
            for m in r.get("modules", [])
            for l in m.get("lessons", [])
            if "has_code" in l
        )
        if r["technical"]:
            if has_any_code:
                tech_with_code += 1
            else:
                tech_without_code += 1
        else:
            if has_any_code:
                nontech_with_code += 1
            else:
                nontech_without_code += 1

    print(f"\nCODE EXAMPLES:")
    print(f"  Technical profiles WITH code: {tech_with_code}/{len(tech_success)}")
    print(f"  Technical profiles WITHOUT code: {tech_without_code}/{len(tech_success)}")
    print(f"  Non-technical profiles WITH code: {nontech_with_code}/{len(nontech_success)} (should be 0)")
    print(f"  Non-technical profiles WITHOUT code: {nontech_without_code}/{len(nontech_success)}")

    # Average chapters/lessons
    if tech_success:
        avg_ch_tech = sum(len(r.get("chapters", [])) for r in tech_success) / len(tech_success)
        avg_les_tech = sum(r.get("total_lessons", 0) for r in tech_success) / len(tech_success)
        print(f"\nTECHNICAL avg: {avg_ch_tech:.1f} chapters, {avg_les_tech:.1f} lessons")

    if nontech_success:
        avg_ch_nt = sum(len(r.get("chapters", [])) for r in nontech_success) / len(nontech_success)
        avg_les_nt = sum(r.get("total_lessons", 0) for r in nontech_success) / len(nontech_success)
        print(f"NON-TECHNICAL avg: {avg_ch_nt:.1f} chapters, {avg_les_nt:.1f} lessons")


asyncio.run(main())
