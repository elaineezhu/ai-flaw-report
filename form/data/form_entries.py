from form.utils.helpers import handle_other_option
from form.data.constants import *
from form.form_entry import FormEntry, InputType
import uuid
from form.data.hf_get_models import get_systems_options

"""
Contains all form entries used throughout the application, organized by section
"""

form_entries = {
    # Basic Information
    "contact_info": FormEntry(
        name="Contact Information",
        title="Contact Information (Optional)",
        input_type=InputType.TEXT,
        help_text="Optionally provide your email, social media handle, or other contact method. Leave blank to remain anonymous.",
        info_text="Contact details for follow-up communication",
        required=False
    ),
    
    "report_id": FormEntry(
        name="Report ID",
        title="Report ID",
        input_type=InputType.TEXT,
        default=None, 
        help_text="This automatically generated report ID allows us to keep track of the submission when it is processed. The report ID can be referenced in future submissions and mitigation efforts.",
        info_text="Report ID to keep track of submission",
        extra_params={"disabled": True}
    ),
    
    "session_id": FormEntry(
        name="Session ID(s)",
        title="Session ID(s)",
        input_type=InputType.TEXT,
        help_text="Many AI chatbots have a 'share' feature, that generate a shareable link for a specific conversation. This allows reporter reviewers to more easily reproduce these findings.",
        info_text="Session link or ID for a session that shows the flaw"
    ),

    "ai_systems": FormEntry(
        name="ai_systems",
        title="AI System(s)",
        input_type=InputType.MULTISELECT,
        options=[],
        required=True,
        info_text="AI systems and versions involved in the flaw",
        help_text="Select one or more AI systems and versions involved in the flaw you are reporting."
    ),
    
    "flaw_timestamp_start": FormEntry(
        name="Flaw Timestamp Start",
        title="When was the flaw first identified?",
        input_type=InputType.DATE,
        required=True,
        help_text="In cases where systems frequently change, this can help reproduce the context.",
        info_text="Start date of flaw"
    ),

    "incident_timestamp_start": FormEntry(
        name="Incident Timestamp Start",
        title="When did the incident occur?",
        input_type=InputType.DATE,
        required=True,
        help_text="Enter the date and time when the real-world incident occurred, or your best estimation.",
        info_text="Start date of incident"
    ),
    
    # Common Fields
    "context_info": FormEntry(
        name="Context Information",
        title="Context Information (versions of other software/hardware involved)",
        input_type=InputType.TEXT_AREA,
        help_text="Enter the versions of other software or hardware systems involved in the flaw if applicable. For example, if you used an open-source model, add information on the hardware you are running it on.",
        info_text="Versions of other software or hardware systems involved in the flaw",
    ),
    
    "flaw_description": FormEntry(
        name="Flaw Description",
        title="Flaw Description (identification, reproduction, how it violates system policies)",
        input_type=InputType.TEXT_AREA,
        help_text="Describe the flaw, how you identified it, how it can be reproduced, and how it violates user expectations of the AI system or AI system policies. Add as much detail as possible to help reproduce and mitigate the flaw.",
        info_text="Describe the following about the flow: (1) a detailed description of the flaw, (2) what undesirable outputs, effects, or impacts you observed, (3) how specifically to reproduce it (the inputs, actions, and/or links to any code), and (4) for probabilistic flaws, have you shown/verified it happens systematically for many inputs or conditions?"
    ),
    
    "policy_violation": FormEntry(
        name="Policy Violation",
        title="Policy Violation (how expectations of the system are violated)",
        input_type=InputType.TEXT_AREA,
        help_text="Provide evidence that the identified flaw is undesirable, or has violated expectations of the AI system. Ideally, point to a documented system policy, acceptable usage policy, or terms that indicate this is undesirable. Explain your reasoning.",
        info_text="Pointer to relevant policies, documentation, etc. showing that the flaw violates them"
    ),
    
    "severity": FormEntry(
            name="Severity",
            title="Severity",
            input_type=InputType.SELECT_SLIDER,
            options=SEVERITY_OPTIONS,
            help_text="If the flaw is encountered, how negative will the impact be for any stakeholder (user, system developer, or other)?",
            info_text="How negatively stakeholders may be impacted"
        ),
        
        "prevalence": FormEntry(
            name="Prevalence",
            title="Prevalence",
            input_type=InputType.SELECT_SLIDER,
            options=PREVALENCE_OPTIONS,
            help_text="""How likely is the flaw to be encountered?
            
    - Rare: Unlikely for other real-world users to identify or have encountered this.
    - Occasional: Other real-world users may occasionally encounter this.
    - Common: Other real-world users will commonly encounter this.
    - Widespread: Other real-world users have likely widely encountered this.""",
            info_text="How common the flaw is"
        ),
    
    "impacts": FormEntry(
        name="Impacts",
        title="Impacts",
        input_type=InputType.MULTISELECT,
        options=IMPACT_OPTIONS,
        help_text="Choose one or more impacts that affected stakeholders may experience if the flaw is not addressed.",
        info_text="Impacts that may occur if the flaw is not addressed"
    ),
    
    "impacted_stakeholders": FormEntry(
        name="Impacted Stakeholder(s)",
        title="Impacted Stakeholder(s)",
        input_type=InputType.MULTISELECT,
        options=STAKEHOLDER_OPTIONS,
        help_text="Choose one or more impacted stakeholders who may suffer if the flaw is not addressed.",
        info_text="Who is impacted if the flaw is not addressed"
    ),
    
    "risk_source": FormEntry(
        name="Risk Source",
        title="Risk Source",
        input_type=InputType.MULTISELECT,
        options=RISK_SOURCE_OPTIONS,
        help_text="Choose one or more presumed sources of the flaw.",
        info_text="Presumed sources of the flaw"
    ),
    
    # Real-World Event Fields
    "submitter_relationship": FormEntry(
        name="Submitter Relationship",
        title="Submitter Relationship",
        input_type=InputType.SELECT,
        options=["Affected stakeholder", "Independent observer", "System developer", "Other"],
        help_text="Describe your relationship to the incident.",
        info_text="Your relationship to incident"
    ),
        
    "event_locations": FormEntry(
        name="Incident Location(s)",
        title="Incident Location(s)",
        input_type=InputType.TEXT,
        help_text="Enter the geographical location in which the real-world incident occurred.",
        info_text="Geographical location of incident"
    ),
    
    "experienced_harm_types": FormEntry(
        name="Experienced Harm Types",
        title="Experienced Harm Types",
        input_type=InputType.MULTISELECT,
        options=HARM_TYPES,
        help_text="Choose one or more types of harm that resulted from the real-world incident(s) involving this flaw.",
        info_text="Harm caused by the incident"
    ),
    
    "experienced_harm_severity": FormEntry(
        name="Experienced Harm Severity",
        title="Experienced Harm Severity",
        input_type=InputType.SELECT_SLIDER,
        options=HARM_SEVERITY_OPTIONS,
        help_text="Your best estimate of how severe the harm caused is.",
        info_text="Severity of the harm caused by the incident"
    ),
    
    "harm_narrative": FormEntry(
        name="Harm Narrative",
        title="Harm Narrative (justification of why the incident constitutes harm)",
        input_type=InputType.TEXT_AREA,
        help_text="Please describe why the real-world incident that occurred is harmful, and how the flaw contributed to it.",
        info_text="Why the incident is harmful and how the flaw contributed to it"
    ),
    
    # Malign Actor Fields
    "tactic_select": FormEntry(
        name="Tactic Select",
        title="Tactic Select (e.g., from MITRE's ATLAS Matrix)",
        input_type=InputType.MULTISELECT,
        options=TACTIC_OPTIONS,
        help_text="Choose one or more tactics that could be used to exploit the flaw.",
        info_text="Tactic(s) that could be used to exploit the flaw"
    ),
    
    "impact": FormEntry(
        name="Impact",
        title="Impact",
        input_type=InputType.MULTISELECT,
        options=IMPACT_TYPE_OPTIONS,
        help_text="Describe the potential impact of the flaw.",
        info_text="Potential impact of the flaw"
    ),
    
    # Security Incident Fields
    "threat_actor_intent": FormEntry(
        name="Threat Actor Intent",
        title="Threat Actor Intent",
        input_type=InputType.RADIO,
        options=THREAT_ACTOR_INTENT_OPTIONS,
        help_text="Describe the intent of the threat actor.",
        info_text="Intent of the threat actor"
    ),
    
    "detection": FormEntry(
        name="Detection",
        title="Detection",
        input_type=InputType.MULTISELECT,
        options=DETECTION_METHODS,
        help_text="Describe how you came to know about this real-world incident, including which methods you used to discover and observe it.",
        info_text="How you learnt about flaw"
    ),
    
    # Vulnerability Fields
    "proof_of_concept": FormEntry(
        name="Proof-of-Concept Exploit",
        title="Proof-of-Concept Exploit",
        input_type=InputType.TEXT_AREA,
        help_text="Provide code and documentation that proves the existence of a vulnerability.",
        info_text="Code and documentation documenting the vulnerability"
    ),
    
    # Hazard Fields
    "statistical_argument": FormEntry(
        name="Statistical Argument with Examples",
        title="Statistical Arguments with Examples (reasoning why this flaw is statistically likely to reoccur)",
        input_type=InputType.TEXT_AREA,
        help_text="Provide your reasoning why this flaw is statistically likely to reoccur and not a one-off incident.",
        info_text="Reasoning why this flaw is statistically likely to reoccur"
    ),
    
    # Disclosure Plan Fields
    "disclosure_intent": FormEntry(
        name="Disclosure Intent",
        title="Do you intend to publicly disclose this issue?",
        input_type=InputType.RADIO,
        options=["Yes", "No", "Undecided"],
        help_text="Required field",
        info_text=""
    ),
    
    "disclosure_timeline": FormEntry(
        name="Disclosure Timeline",
        title="Planned disclosure timeline",
        input_type=InputType.SELECT,
        options=["Immediate (0 days)", "Short-term (1-30 days)", "Medium-term (31-90 days)", "Long-term (90+ days)"],
        help_text="When do you plan to publicly disclose this issue?",
        info_text=""
    ),
    
    "disclosure_channels": FormEntry(
        name="Disclosure Channels",
        title="Disclosure channels",
        input_type=InputType.MULTISELECT,
        options=["Academic paper", "Blog post", "Social media", "Media outlet", "Conference presentation", "Other"],
        help_text="Where do you plan to disclose this issue?",
        info_text=""
    ),
    
    "embargo_request": FormEntry(
        name="Embargo Request",
        title="Embargo request details",
        input_type=InputType.TEXT_AREA,
        help_text="If you're requesting an embargo period before public disclosure, please provide details",
        info_text=""
    )
}