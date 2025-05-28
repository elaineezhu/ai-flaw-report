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
        title="Session ID(s)",
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
        name="Context Information",
        title="Context Information",
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

    "flaw_description_outputs": FormEntry(
        name="Flaw Description - Undesirable Outputs",
        title="Undesirable Outputs of Flaw",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="Describe the wrong or harmful outputs you saw.",
        info_text="Negative outputs or effects"
    ),

    "flaw_description_reproduction": FormEntry(
        name="Flaw Description - Reproduction Steps",
        title="Reproduction Steps for Flaw",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="List steps or code so others can make the AI do the same wrong thing.",
        info_text="Steps to reproduce flaw"
    ),

    "flaw_description_systematic": FormEntry(
        name="Flaw Description - Systematic Evidence",
        title="Flaw Systematic Evidence",
        input_type=InputType.TEXT_AREA,
        required=False,
        help_text="If this problem happens sometimes, explain how you tested it and what you found.",
        info_text="Evidence the flaw repeats"
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

    "incident_description_outputs": FormEntry(
        name="Incident Description - Undesirable Outputs",
        title="Undesirable Outputs of Incident",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="Tell us the harm or damage that happened.",
        info_text="Harmful outputs or effects"
    ),

    "incident_description_reproduction": FormEntry(
        name="Incident Description - Reproduction Steps",
        title="Reproduction Steps for Incident",
        input_type=InputType.TEXT_AREA,
        required=True,
        help_text="Give steps or code so others can recreate the incident.",
        info_text="Steps to reproduce incident"
    ),

    "incident_description_systematic": FormEntry(
        name="Incident Description - Systematic Evidence",
        title="Incident Systematic Evidence",
        input_type=InputType.TEXT_AREA,
        required=False,
        help_text="If the incident is not guaranteed, explain how often you saw it and how you tested.",
        info_text="Evidence incident repeats"
    ),
    
    "policy_violation": FormEntry(
        name="Policy Violation",
        title="Policy Violation",
        input_type=InputType.TEXT_AREA,
        help_text="Point to any rules or policies the AI broke and explain why it is wrong.",
        info_text="How the flaw breaks rules"
    ),
    
    "severity": FormEntry(
        name="Severity",
        title="Level of Harm",
        input_type=InputType.SELECT_SLIDER,
        options=SEVERITY_OPTIONS,
        help_text="Pick how bad the harm would be if someone hits this flaw.",
        info_text="How serious the flaw is"
    ),
        
    "prevalence": FormEntry(
        name="Prevalence",
        title="Prevalence",
        input_type=InputType.SELECT_SLIDER,
        options=PREVALENCE_OPTIONS,
        help_text="Pick how common you think this problem is for other users.",
        info_text="How common the flaw is"
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
        options=HARM_TYPES,
        help_text="Pick all types of harm people experienced from this incident.",
        info_text="What kind of harm happened"
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
    "tactic_select": FormEntry(
        name="Tactic Select",
        title="Tactic Select",
        input_type=InputType.MULTISELECT,
        options=TACTIC_OPTIONS,
        help_text="Pick tactics that bad actors might use to exploit this flaw.",
        info_text="Possible attack tactics"
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
    )
}