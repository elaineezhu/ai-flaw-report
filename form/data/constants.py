PRIORITY_MODELS = [
    # Text models
    "GPT-4.5-Preview",
    "o3-mini",
    "o1",
    "GPT-4o",
    "GPT-4",
    "GPT-3.5-Turbo",
    "Claude-3.7-Sonnet-Reasoning",
    "Claude-3.7-Sonnet",
    "Claude-3.5-Sonnet",
    "Claude-3",
    "Claude-instant",
    "Claude-2",
    "Gemini-2.0",
    "Gemini-1.5",
    "Gemini-1.0",
    "DeepSeek-R1",
    "DeepSeek-V3",
    "Grok-2",
    "Grok-beta",

    # Image models
    "FLUX-pro-1.1-ultra",
    "FLUX-pro-1.1",
    "FLUX-pro",
    "FLUX-schnell",
    "FLUX-dev",
    "Imagen3",
    "Luma-Photon",
    "DALL-E-3",
    "StableDiffusion3.5",
    "StableDiffusion3",
    "StableDiffusionXL",
    "Playground-v3",
    "Playground-v2.5",
    "Ideogram-v2",
    "Ideogram",

    # Video models
    "Runway",
    "Ray2",
    "Dream-Machine",
    "Pika-2.0",
    "Pika-1.5",
    "Pika-1.0",
    "Hailuo-AI",
    "Kling-Pro-v1.5",
    "HunyuanVideo",
    "Haiper2.0",
    "Veo-2"
]


SYSTEM_OPTIONS = [
    "v1.0",
    "v1.1",
    "v2.0",
    "v3.0",
    "v4.0",
    "Other"
]

REPORT_STATUS_OPTIONS = [
    "New",
    "Update to Under Investigation Report",
    "Update to Rejected Report",
    "Update to Closed/Fixed Report"
]

SEVERITY_OPTIONS = [
    "Negligible",
    "Low",
    "Medium",
    "High",
    "Critical"
]

PREVALENCE_OPTIONS = [
    "Unknown",
    "Rare",
    "Occasional",
    "Common",
    "Widespread"
]

IMPACT_OPTIONS = [
    "Autonomy",
    "Physical",
    "Psychological",
    "Reputational",
    "Financial and Business",
    "Human Rights and Civil Liberties",
    "Societal and Cultural",
    "Political and Economic",
    "Environmental",
    "Sexualization"
]

HARM_TYPE_MAPPINGS = {
    "Autonomy": [
        "Autonomy/agency loss - Loss of an individual, group or organisation's ability to make informed decisions or pursue goals",
        "Impersonation/identity theft - Theft of an individual, group or organisation's identity by a third-party in order to defraud, mock or otherwise harm them",
        "IP/copyright loss - Misuse or abuse of an individual or organisation's intellectual property, including copyright, trademarks, and patents",
        "Personality rights loss - Loss of or restrictions to the rights of an individual to control the commercial use of their identity, such as name, image, likeness, or other unequivocal identifiers"
    ],
    "Physical": [
        "Bodily injury - Physical pain, injury, illness, or disease suffered by an individual or group due to the malfunction, use or misuse of a technology system",
        "Loss of life - Accidental or deliberate loss of life, including suicide, extinction or cessation, due to the use or misuse of a technology system",
        "Personal health deterioration - Physical deterioration of an individual or animal over time, increasing their risk of disease, organ failure, prolonged hospital stay or death, etc",
        "Property damage - Action(s) that lead directly or indirectly to the damage or destruction of tangible property eg. buildings, possessions, vehicles, robots"
    ],
    "Psychological": [
        "Addiction - Emotional or material dependence on technology or a technology system",
        "Alienation/isolation - An individual's or group's feeling of lack of connection with those around as a result of technology use or misuse",
        "Anxiety/depression - Mental health decline due to addiction, negative social interactions such as humiliation and shaming and traumatic distressing events such as online violence or rape",
        "Coercion/manipulation - Use of a technology system to covertly alter user beliefs and behaviour using nudging, dark patterns and/or other opaque techniques, resulting in potential erosion of privacy, addiction, anxiety/distress, etc",
        "Dehumanisation/objectification - Use or misuse of a technology system to depict and/or treat people as not human, less than human, or as objects",
        "Harassment/abuse/intimidation - Online behaviour, including sexual harassment, that makes an individual or group feel alarmed or threatened",
        "Over-reliance - Unfettered and/or obsessive belief in the accuracy or other quality of a technology system, resulting in addiction, anxiety, introversion, sentience, complacency, lack of critical thinking and other actual or potential negative impacts",
        "Radicalisation - Adoption of extreme political, social, or religious ideals and aspirations due to the nature or misuse of an algorithmic system, potentially resulting in abuse, violence, or terrorism",
        "Self-harm - Intentional seeking out or sharing of hurtful content about oneself that leads to, supports, or exacerbates low self-esteem and self-harm",
        "Sexualisation - Sexual interest in a technology or application",
        "Trauma - Severe and lasting emotional shock and pain caused by an extremely upsetting experience"
    ],
    "Reputational": [
        "Defamation/libel/slander - Use of a technology system to create, facilitate or amplify false perception(s) about an individual, group, or organisation",
        "Loss of confidence/trust - Misleading or unfair change(s) in how an individual, group, or organisation is viewed, leading to loss of ability to conduct relationships, raise capital, recruit people, etc"
    ],
    "Financial and Business": [
        "Business operations/infrastructure damage - Damage, disruption, or destruction of a business system and/or its components due to malfunction, cyberattacks, etc",
        "Confidentiality loss - Unauthorised sharing of sensitive, confidential information and documents such as corporate strategy and financial plans with third-parties",
        "Financial/earnings loss - Loss of money, income or value due to the use or misuse of a technology system",
        "Livelihood loss - An individual or group's loss of ability to support themselves financially or vocationally due to natural disasters, lack of demand for products/services, cost increases, etc, resulting in inability to procure food, reduced employment prospects, bankruptcy, foreclosure, homelessness, etc",
        "Increased competition - The inappropriate or unethical use of technology to gain market share",
        "Monopolisation - Abuse of market power through the control of prices, thereby limiting competition and creating unfair barriers to entry",
        "Opportunity loss - Loss of ability to take advantage of a financial or other opportunity, such as education, employability/securing a job"
    ],
    "Human Rights and Civil Liberties": [
        "Benefits/entitlements loss - Denial or or loss of access to welfare benefits, pensions, housing, etc due to the malfunction, use or abuse of a technology system",
        "Dignity loss - Perceived loss of value experienced by or disrespect shown to an individual or group, resulting in self-sheltering, loss of connections and relationships, and public stigmatisation",
        "Discrimination - Unfair or inadequate treatment or arbitrary distinction based on a person's race, ethnicity, age, gender, sexual preference, religion, national origin, marital status, disability, language, or other protected groups",
        "Loss of freedom of speech/expression - Restrictions to or loss of people's right to articulate their opinions and ideas without fear of retaliation, censorship, or legal sanction",
        "Loss of freedom of assembly/association - Restrictions to or loss of people's right to come together and collectively express, promote, pursue, and defend their collective or shared ideas, and/or to join an association",
        "Loss of social rights and access to public services - Restrictions to or loss of rights to work, social security, and adequate standard of living, housing, health and education",
        "Loss of right to information - Restrictions to or loss of people's right to seek, receive and impart information held by public bodies",
        "Loss of right to free elections - Restrictions to or loss of people's right to participate in free elections at reasonable intervals by secret ballot",
        "Loss of right to liberty and security - Restrictions to or loss of liberty as a result of illegal or arbitrary arrest or false imprisonment",
        "Loss of right to due process - Restrictions to or loss of right to be treated fairly, efficiently and effectively by the administration of justice",
        "Privacy loss - Unwarranted exposure of an individual's private life or personal data through cyberattacks, doxxing, etc"
    ],
    "Societal and Cultural": [
        "Breach of ethics/values/norms - An actual or perceived violation or deviation from the established societal values, norms or ethical standards or principles",
        "Cheating/plagiarism - Use of another person's or group's words or ideas without consent and/or acknowledgement",
        "Chilling effect - The creation of a climate of self-censorship that deters democratic actors such as journalists, advocates and judges from speaking out",
        "Cultural dispossession - Intentional and/or unintentional erasure of cultural goods and values, such as ways of speaking, expressing humour, or sounds and voices that contribute to a cultural identity, or their inappropriate re-use in other cultures",
        "Damage to public health - Adverse impacts on the health of groups, communities or societies, including malnutrition, disease and infection conditions",
        "Historical revisionism - Deliberate or unintentional reinterpretation of established/orthodox historical events or accounts held by societies, communities, academics",
        "Information degradation - Creation or spread of false, hallucinatory, low-quality, misleading, or inaccurate information that degrades the information ecosystem and causes people to develop false or inaccurate perceptions, decisions and beliefs; or to lose trust in accurate information",
        "Job loss/losses - Replacement/displacement of human jobs by a technology system, leading to increased unemployment, inequality, reduced consumer spending, and social friction",
        "Labour exploitation - Use of under-paid and/or offshore labour to develop, manage or optimise a technology system",
        "Loss of creativity/critical thinking - Devaluation and/or deterioration of human creativity, artistic expression, imagination, critical thinking or problem-solving skills",
        "Stereotyping - Derogatory or otherwise harmful stereotyping or homogenisation of individuals, groups, societies or cultures due to the mis-representation, over-representation, under-representation, or non-representation of specific identities, groups, or perspectives",
        "Public service delivery deterioration - Poor performance of a public technology system due to malfunction, over-use, under-staffing etc, resulting in individuals, groups, or organisations unable to use it in a manner they can reasonably expect",
        "Societal destabilisation - Societal instability in the form of strikes, demonstrations and other types of civil unrest caused by loss of jobs to technology, unfair algorithmic outcomes, disinformation, etc",
        "Societal inequality - Increased difference in social status or wealth between individuals or groups caused or amplified by a technology system, leading to the loss of social and community wellbeing/cohesion and destabilisation",
        "Violence/armed conflict - Use or misuse of a technology system to incite, facilitate or conduct cyberattacks, security breaches, lethal, biological and chemical weapons development, resulting in violence and armed conflict"
    ],
    "Political and Economic": [
        "Critical infrastructure damage - Damage, disruption to or destruction of systems essential to the functioning and safety of a nation or state, including energy, transport, health, finance, and communications systems",
        "Economic instability - Uncontrolled fluctuations impacting the financial system, or parts thereof, due to the use or misuse of a technology system, or set of systems",
        "Power concentration - Amplification of concentration of economic and/or political wealth and power, potentially resulting in increased inequality and instability",
        "Electoral interference - Generation of false or misleading information that can interrupt or mislead voters and/or undermine trust in electoral processes",
        "Institutional trust loss - Erosion of trust in public institutions and weakened checks and balances due to mis/disinformation, influence operations, over-dependence on technology, etc",
        "Political instability - Political polarisation or unrest caused by increased inequality, job losses, over-dependence on technology making societies vulnerable to systemic failures, etc, arising from or amplified by the use or misuse of a technology system",
        "Political manipulation - Use or misuse of personal data to target individuals' interests, personalities and vulnerabilities with tailored political messages via micro-advertising or deepfakes/synthetic media"
    ],
    "Environmental": [
        "Biodiversity loss - Over-expansion of technology infrastructure, or inadequate alignment of technology with sustainable practices, leading to deforestation, habitat destruction, and fragmentation and loss of biodiversity",
        "Carbon emissions - Release of carbon dioxide, nitric oxide and other gases, increasing carbon emissions, exacerbating climate change, and negatively impacting local communities",
        "Electronic waste - Electrical or electronic equipment that is waste, including all components, sub-assemblies and consumables that are part of the equipment at the time the equipment becomes waste",
        "Excessive energy consumption - Excessive energy use, leading to energy bottlenecks and shortages for communities, organisations, and businesses",
        "Excessive landfill - Excessive disposal of electrical or electronic equipment leading to ecological/biodiversity damage, and disrupting the livelihoods and eroding the rights of local communities",
        "Excessive water consumption - Excessive use of water to cool data centres and for other purposes, leading to water restrictions or shortages for local communities or businesses",
        "Natural resource depletion - Extraction of minerals, metals, rare earths, and fossil fuels that deplete natural resources and increase carbon emissions",
        "Pollution - Actual or potential pollution to the air, ground, noise, or water caused by a technology system"
    ]
}
STAKEHOLDER_OPTIONS = [
    "Users",
    "Developers",
    "Administrators",
    "General Public",
    "Vulnerable populations",
    "Organizations",
    "Other"
]

RISK_SOURCE_OPTIONS = [
    "Design flaw",
    "Implementation error",
    "Data bias",
    "Deployment issue",
    "Integration problem",
    "Other"
]

BOUNTY_OPTIONS = [
    "Yes",
    "No",
    "Not sure"
]

HARM_TYPES = [
    "Physical",
    "Psychological",
    "Reputational",
    "Economic/property",
    "Environmental",
    "Public interest/critical infrastructure",
    "Fundamental rights",
    "Sexualization",
    "Other"
]

EXPERIENCED_HARM_OPTIONS = [
    "Physical",
    "Psychological", 
    "Reputational",
    "Economic/property",
    "Environmental",
    "Public interest/critical infrastructure",
    "Fundamental rights",
    "Sexualization",
    "Other"
]

HARM_SEVERITY_OPTIONS = [
    "Low",
    "Medium",
    "Significant",
    "Critical",
]

TACTIC_OPTIONS = [
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Command and Control",
    "Exfiltration",
    "Impact"
]

IMPACT_TYPE_OPTIONS = [
    "Confidentiality breach",
    "Integrity violation",
    "Availability disruption",
    "Abuse of system"
]

THREAT_ACTOR_INTENT_OPTIONS = [
    "Deliberate",
    "Unintentional",
    "Unknown"
]

DETECTION_METHODS = [
    "User observation",
    "Monitoring",
    "Testing",
    "External report",
    "Automated analysis"
]

REPORT_TYPES = [
    "All Flaw Reports",
    "Real-World Events",
    "Malign Actor",
    "Security Incident Report",
    "Vulnerability Report",
    "Hazard Report"
]

ATTACKER_RESOURCES_OPTIONS = [
    "Training data/feedback control — An attacker can modify training data/feedback and/or insert a subset of examples.",
    "Model/system supply chain control — An attacker can modify the AI model itself, such as via public fine-tuning", 
    "Direct query access — white-box — An attacker can query the system—the degree of control can vary substantially (e.g., ability to control temperature, view logits, etc.).",
    "Direct query access — black-box — An attacker can query the system—the degree of control can vary substantially (e.g., ability to control temperature, view logits, etc.).",
    "Direct query access — grey-box — An attacker can query the system—the degree of control can vary substantially (e.g., ability to control temperature, view logits, etc.).",
    "Application/plugin supply chain control — An attacker can modify the agent framework, tools and/or services with which a model interacts, such as introducing vulnerabilities into application software or appending malicious text to plugin instructions.",
    "Application/plugin output control — An attacker can modify the context that the agent views during inference by modifying sources (e.g., webpages, memory, etc.)."
]

ATTACKER_OBJECTIVES_OPTIONS = [
    "Availability breakdown — An attacker disrupts the ability of users to obtain access to AI systems or their functionality.",
    "Integrity violation —  An attacker causes AI systems to perform tasks inadequately or behave undesirably.",
    "Privacy compromise — An attacker gains access to sensitive and confidential information, including information about the AI system (e.g., architecture or weights) or sensitive information that the model accesses (e.g., training data, external knowledge databases.", 
    "Abuse violation — An attacker uses an AI system for purposes that are harmful or otherwise unintended by the developer, often by evading guardrails."
]

RESPONSIBLE_FACTORS_OPTIONS = [
    "Training data",
    "Feedback", 
    "System prompt",
    "Tool instructions",
    "Tool outputs/external inputs",
    "Supply chain weaknesses (e.g., software libraries and hardware)",
    "User prompt",
    "Memory",
    "Multi-agent interactions",
    "Other"
]

RESPONSIBLE_FACTORS_SUBCATEGORIES = {
    "Training data": [
        "Data poisoning",
        "Sensitive information (e.g., PII)",
        "Other"
    ],
    "Feedback": [
        "Poisoning",
        "Misspecification (no threat actor)",
        "Other"
    ],
    "Tool instructions": [
        "Indirect prompt injection",
        "Malicious code execution",
        "Other"
    ],
    "Tool outputs/external inputs": [
        "Resource overload/accessibility issues",
        "Reliability issues (e.g., false information)",
        "Indirect prompt injection"
    ],
    "Memory": [
        "Indirect prompt injection (memory poisoning)",
        "False information/cascading hallucinations",
        "Vector and embedding weaknesses",
        "Sensitive information"
    ],
    "User prompt": [
        "Misinterpretation of user instructions",
        "Jailbreak/adversarial attack",
        "Other"
    ],
    "Multi-agent interactions": [
        "Agent communication poisoning",
        "Rogue agents",
        "Other"
    ]
}

TOOL_OUTPUT_DESCRIPTIONS = {
    "Resource overload/accessibility issues": "Tools and/or their outputs are not available to the agent",
    "Reliability issues (e.g., false information)": "Tools do not always function as intended (excludes cases of malicious attacks)"
}