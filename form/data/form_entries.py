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
        help_text="You can leave this blank or add your email or social media so we can follow up.",
        info_text="Your contact details (optional)",
        required=False
    ),
    
    "report_id": FormEntry(
        name="Report ID",
        title="Report ID",
        input_type=InputType.TEXT,
        default=None, 
        help_text="This ID is made for you to track your report. You don’t need to fill it in.",
        info_text="Report ID for tracking",
        extra_params={"disabled": True}
    ),
    
    "session_id": FormEntry(
        name="Session ID(s)",
        title="Session Link(s)/Session ID(s)",
        input_type=InputType.TEXT,
        help_text="Paste the chat link or ID here so others can see the same interaction.",
        info_text="Link or ID of the chat session"
    ),

    "ai_systems": FormEntry(
        name="ai_systems",
        title="AI System(s)",
        input_type=InputType.MULTISELECT,
        options=[],
        required=True,
        help_text="Pick all the AI versions you used when you found the problem.",
        info_text="Which AI systems are involved?"
    ),
    
    "flaw_timestamp_start": FormEntry(
        name="Flaw Timestamp Start",
        title="When was the flaw first found?",
        input_type=InputType.DATE,
        required=True,
        help_text="Enter the date you first saw this problem.",
        info_text="Date you first found the flaw"
    ),

    "incident_timestamp_start": FormEntry(
        name="Incident Timestamp Start",
        title="When did the incident happen?",
        input_type=InputType.DATE,
        required=True,
        help_text="Enter the date the incident took place.",
        info_text="Date the incident happened"
    ),
    
    # Common Fields
    "context_info": FormEntry(
        name="Reproduction Context",
        title="Reproduction Steps for Flaw",
        input_type=InputType.TEXT_AREA,
        help_text="Tell us what other tools or devices you used when you saw the flaw.",
        info_text="Other software or hardware info",
    ),
    
    # Flaw Description Fields
    "flaw_description_detailed": FormEntry(
        name="Flaw Description - Detailed Description",
        title="Detailed Flaw Description",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="Explain exactly what the AI did wrong or did not do.",
        info_text="What the flaw is"
    ),

    # Incident Description Fields
    "incident_description_detailed": FormEntry(
        name="Incident Description - Detailed Description",
        title="Detailed Incident Description",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="Explain what happened and how the AI was at fault.",
        info_text="What the incident was"
    ),
    
    "policy_violation": FormEntry(
        name="Policy Violation",
        title="Policy Violation",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="Point to any rules or policies the AI broke and explain why it is wrong.",
        info_text="How the flaw breaks rules"
    ),
    
    "severity": FormEntry(
        name="Severity",
        title="Level of Harm",
        input_type=InputType.SELECT_SLIDER,
        options=SEVERITY_OPTIONS,
        help_text="Pick how bad the harm would be if someone hits this flaw.",
        info_text="If the flaw is encountered, how negative will the impact be for any stakeholder (user, system developer, or other)?"
    ),
        
    "prevalence": FormEntry(
        name="Prevalence",
        title="Prevalence",
        input_type=InputType.SELECT_SLIDER,
        options=PREVALENCE_OPTIONS,
        help_text="• Rare: Unlikely for other real-world users to identify or have encountered this. \n • Occasional: Other real-world users may occasionally encounter this. \n • Common: Other real-world users will commonly encounter this. \n • Widespread: Other real-world users have likely widely encountered this.",
        info_text="How likely is the flaw to be encountered?"
    ),
    
    "impacts": FormEntry(
        name="Impacts",
        title="Possible Impacts",
        input_type=InputType.MULTISELECT,
        options=IMPACT_OPTIONS,
        help_text="Choose all impacts people might face if the flaw stays unfixed.",
        info_text="What impacts could happen",
        required=True
    ),

    "specific_harm_types": FormEntry(
        name="Specific Impact Types",
        title="Specific Impact Types",
        input_type=InputType.MULTISELECT,
        options=[], # dynamic population
        help_text="Select the specific types of harm that apply based on your impact selections.",
        info_text="Detailed harm classifications from the taxonomy",
        required=False
    ),
    
    "impacted_stakeholders": FormEntry(
        name="Impacted Stakeholder(s)",
        title="Impacted Stakeholder(s)",
        input_type=InputType.MULTISELECT,
        options=STAKEHOLDER_OPTIONS,
        help_text="Pick the people or groups hurt by this flaw.",
        info_text="Who is impacted",
        required=True
    ),
    
    "risk_source": FormEntry(
        name="Risk Source",
        title="Possible Sources of the Risk",
        input_type=InputType.MULTISELECT,
        options=RISK_SOURCE_OPTIONS,
        help_text="Pick the causes you think led to this flaw.",
        info_text="Where the flaw might come from"
    ),

    "csam_related_question": FormEntry(
        name="CSAM Related Question",
        title="Is this flaw related to child sexual-abuse material, or any explicit sexualization of children?",
        input_type=InputType.RADIO,
        options=["Yes", "No"],
        help_text="Please answer this question to help us route your report appropriately.",
        info_text="CSAM-related content requires special handling",
        required=True,
        extra_params={"key": "csam_related_selection"}
    ),
    
    # Real-World Event Fields
    "submitter_relationship": FormEntry(
        name="Submitter Relationship",
        title="Submitter Relationship",
        input_type=InputType.SELECT,
        options=["Affected stakeholder", "Independent observer", "System developer", "Other"],
        help_text="Tell us if you saw this, were hurt by this, built the system, or other.",
        info_text="Your relationship to the incident"
    ),
        
    "event_locations": FormEntry(
        name="Incident Location(s)",
        title="Incident Location(s)",
        input_type=InputType.TEXT,
        help_text="Enter the place (city, country) where this incident took place.",
        info_text="Where the incident happened"
    ),
    
    "experienced_harm_types": FormEntry(
        name="Experienced Harm Types",
        title="Experienced Harm Types",
        input_type=InputType.MULTISELECT,
        options=EXPERIENCED_HARM_OPTIONS,
        help_text="Choose the types of harm that were experienced in this incident.",
        info_text="What kind of harm happened",
        required=True,
        extra_params={"key": "experienced_harm_types"}
    ),

    "experienced_harm_severity": FormEntry(
        name="Experienced Harm Severity",
        title="Severity of the Harm",
        input_type=InputType.SELECT_SLIDER,
        options=HARM_SEVERITY_OPTIONS,
        help_text="Choose how severe the harm was.",
        info_text="How bad the harm was"
    ),

    "harm_narrative": FormEntry(
        name="Harm Narrative",
        title="Harm Narrative",
        input_type=InputType.TEXT_AREA,
        help_text="Explain why the incident is harmful and how the flaw caused it.",
        info_text="Why the incident is harmful"
    ),
    
    # Malign Actor Fields
    "attacker_resources": FormEntry(
        name="Attacker Resources",
        title="Attacker Resources",
        input_type=InputType.MULTISELECT,
        options=ATTACKER_RESOURCES_OPTIONS,
        help_text="Select the types of access or control the attacker has.",
        info_text="What resources does the attacker have access to?",
        required=False,
        extra_params={"key": "attacker_resources_selection"}
    ),
    
    "attacker_objectives": FormEntry(
        name="Attacker Objectives", 
        title="Attacker Objectives",
        input_type=InputType.MULTISELECT,
        options=ATTACKER_OBJECTIVES_OPTIONS,
        help_text="Select what the attacker is trying to achieve.",
        info_text="What are the attacker's goals?",
        required=False,
        extra_params={"key": "attacker_objectives_selection"}
    ),
    
    "objective_context": FormEntry(
        name="Objective Context",
        title="Objective Context", 
        input_type=InputType.TEXT_AREA,
        help_text="Provide more context about the attacker's specific goals and motivations.",
        info_text="Additional details about what the attacker wants to accomplish",
        required=False,
        extra_params={"key": "objective_context_input"}
    ),
    
    "impact": FormEntry(
        name="Impact",
        title="Impacts of the Flaw",
        input_type=InputType.MULTISELECT,
        options=IMPACT_TYPE_OPTIONS,
        help_text="Choose impacts that could happen if the flaw is used by attackers.",
        info_text="Potential attacker impacts"
    ),
    
    # Security Incident Fields
    "threat_actor_intent": FormEntry(
        name="Threat Actor Intent",
        title="Attacker's Intent",
        input_type=InputType.RADIO,
        options=THREAT_ACTOR_INTENT_OPTIONS,
        help_text="Explain what you think the attacker was trying to do.",
        info_text="What the attacker wanted to achieve"
    ),
    
    "detection": FormEntry(
        name="Detection",
        title="Detection",
        input_type=InputType.MULTISELECT,
        options=DETECTION_METHODS,
        help_text="Describe methods you used to discover or observe this incident.",
        info_text="How you detected the incident"
    ),
    
    # Vulnerability Fields
    "proof_of_concept": FormEntry(
        name="Proof-of-Concept Exploit",
        title="Proof-of-Concept Exploit",
        input_type=InputType.TEXT_AREA,
        help_text="Share code or steps that show the vulnerability is real.",
        info_text="Exploit code or documentation"
    ),
    
    # Hazard Fields
    "statistical_argument": FormEntry(
        name="Statistical Argument with Examples",
        title="Statistical Argument with Examples",
        input_type=InputType.TEXT_AREA,
        help_text="Explain with examples why this flaw is likely to reoccur.",
        info_text="Reasoning why flaw repeats"
    ),
    
    # Disclosure Plan Fields
    "disclosure_intent": FormEntry(
        name="Disclosure Intent",
        title="Disclosure Intent",
        input_type=InputType.RADIO,
        options=["Yes", "No", "Undecided"],
        help_text="Tell us if you want to disclose this issue publicly.",
        info_text="Do you plan to share this publicly?"
    ),
    
    "disclosure_timeline": FormEntry(
        name="Disclosure Timeline",
        title="Planned Disclosure Timeline",
        input_type=InputType.SELECT,
        options=["Immediate (0 days)", "Short-term (1-30 days)", "Medium-term (31-90 days)", "Long-term (90+ days)"],
        help_text="Pick when you plan to disclose the issue.",
        info_text="When will you share this issue?"
    ),
    
    "disclosure_channels": FormEntry(
        name="Disclosure Channels",
        title="Disclosure Methods",
        input_type=InputType.MULTISELECT,
        options=["Academic paper", "Blog post", "Social media", "Media outlet", "Conference presentation", "Other"],
        help_text="Choose channels you plan to use for disclosure.",
        info_text="How do you plan to share this issue?"
    ),
    
    "embargo_request": FormEntry(
        name="Embargo Request",
        title="Embargo Details",
        input_type=InputType.TEXT_AREA,
        help_text="If you want to delay public release, explain your embargo request.",
        info_text="Details for embargo request"
    ),

    # Responsible Factors Fields
    "responsible_factors": FormEntry(
        name="Responsible Factors",
        title="Responsible Factors",
        input_type=InputType.MULTISELECT,
        options=RESPONSIBLE_FACTORS_OPTIONS,
        help_text="Select the technical factors that contributed to this flaw.",
        info_text="What aspects of the system contributed to the flaw?",
        required=False,
        extra_params={"key": "responsible_factors_selection"}
    ),
    
    "responsible_factors_context": FormEntry(
        name="Responsible Factors Context",
        title="Responsible Factors Context",
        input_type=InputType.TEXT_AREA,
        help_text="Provide additional evidence about each of the factors identified which contributed to the flaw.",
        info_text="Additional details about how these factors contributed to the flaw",
        required=False,
        extra_params={"key": "responsible_factors_context_input"}
    ),
    
}