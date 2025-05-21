import streamlit as st
from form.utils.helpers import handle_other_option
from form.data.constants import *
from form.form_entry import FormEntry, InputType
import uuid
from form.data.hf_get_models import get_systems_options
from form.data.hf_get_models import searchable_model_selector

def display_basic_information():
    """Display and gather basic information section using FormEntry"""
    st.subheader("Basic Information")
    
    with st.sidebar.expander("Models API Settings", expanded=False):
        use_api = st.checkbox("Use Hugging Face API for models", value=True)
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_field = FormEntry(
                name="Reporter ID",
                title="Reporter ID (anonymous or real identity)",
                input_type=InputType.TEXT,
                help_text="Enter your anonymous or real identity.",
                info_text="Anonymous or real identity",
                required=True
            )
            reporter_id = reporter_field.to_streamlit()
            
            report_id_field = FormEntry(
                name="Report ID",
                title="Report ID",
                input_type=InputType.TEXT,
                default=st.session_state.report_id,
                help_text="This automatically generated report ID allows us to keep track of the submission when it is processed. The report ID can be referenced in future submissions and mitigation efforts.",
                info_text="Report ID to keep track of submission",
                extra_params={"disabled": True}
            )
            report_id = report_id_field.to_streamlit()
            
            systems_options = get_systems_options(use_api=use_api)
            
            st.write("**Systems**")
            st.caption("AI systems and versions involved in the flaw")
            systems = searchable_model_selector(
                available_models=systems_options,
                key_prefix="systems",
                max_selections=20,
                help_text="Select one or more AI systems and versions involved in the flaw you are reporting."
            )
        
        with col2:
            status_field = FormEntry(
                name="Report Status",
                title="Report Status",
                input_type=InputType.SELECT,
                options=REPORT_STATUS_OPTIONS,
                help_text="This field is auto-filled.",
                info_text=""
            )
            report_status = status_field.to_streamlit()
            
            session_field = FormEntry(
                name="Session ID",
                title="Session ID",
                input_type=InputType.TEXT,
                help_text="Enter the session link or session ID for a session that shows the flaw you encountered if available. For example, many chatbots have a \"Share\" feature located at a top that can generate a link that you can share with others so that they have access to your chat. We will not share this link in the public AI flaw database to ensure no private information is accidentally shared too broadly.",
                info_text="Session link or ID for a session that shows the flaw"
            )
            session_id = session_field.to_streamlit()
            
            # Timestamps side by side within column 2
            timestamp_col1, timestamp_col2 = st.columns(2)
            with timestamp_col1:
                start_date_field = FormEntry(
                    name="Flaw Timestamp Start",
                    title="Flaw Timestamp Start",
                    input_type=InputType.DATE,
                    help_text="Enter the date and time when you encountered the flaw, or your best estimation.",
                    info_text="Start date of flaw"
                )
                flaw_timestamp_start = start_date_field.to_streamlit()
            with timestamp_col2:
                end_date_field = FormEntry(
                    name="Flaw Timestamp End",
                    title="Flaw Timestamp End",
                    input_type=InputType.DATE,
                    help_text="If the flaw occurred multiple times, enter the full time range from the first occurrence to the most recent occurrence.",
                    info_text="End date of flaw"
                )
                flaw_timestamp_end = end_date_field.to_streamlit()
    
    return {
        "Reporter ID": reporter_id,
        "Report ID": report_id,
        "Report Status": report_status,
        "Session ID": session_id,
        "Flaw Timestamp Start": flaw_timestamp_start.isoformat() if flaw_timestamp_start else None,
        "Flaw Timestamp End": flaw_timestamp_end.isoformat() if flaw_timestamp_end else None,
        "Systems": systems,
    }

def display_common_fields():
    """Display and gather common fields section"""
    st.subheader("Common Fields")
    
    # Context Info
    context_info_field = FormEntry(
        name="Context Info",
        title="Context Info (versions of other software/hardware involved)",
        input_type=InputType.TEXT_AREA,
        help_text="Enter the versions of other software or hardware systems involved in the flaw if applicable. For example, if you used an open-source model, add information on the hardware you are running it on.",
        info_text="Versions of other software or hardware systems involved in the flaw"
    )
    context_info = context_info_field.to_streamlit()
    
    # Flaw Description
    flaw_description_field = FormEntry(
        name="Flaw Description",
        title="Flaw Description (identification, reproduction, how it violates system policies)",
        input_type=InputType.TEXT_AREA,
        help_text="Describe the flaw, how you identified it, how it can be reproduced, and how it violates user expectations of the AI system or AI system policies. Add as much detail as possible to help reproduce and mitigate the flaw.",
        info_text="Flaw description, identification details, reproduction instructions, which policies/expectations were violated"
    )
    flaw_description = flaw_description_field.to_streamlit()
    
    # Policy Violation
    policy_violation_field = FormEntry(
        name="Policy Violation",
        title="Policy Violation (how expectations of the system are violated)",
        input_type=InputType.TEXT_AREA,
        help_text="Point to relevant evidence that shows how the expectations of the system are violated or undocumented, for example by pointing to the terms of use, acceptable use policy, system card, or other documentation. Policies may be explicitly or implicitly violated.",
        info_text="Pointer to relevant policies, documentation, etc. showing that the flaw violates them"
    )
    policy_violation = policy_violation_field.to_streamlit()
    
    # Severity and Prevalence
    col1, col2 = st.columns(2)
    with col1:
        severity_field = FormEntry(
            name="Severity",
            title="Severity",
            input_type=InputType.SELECT_SLIDER,
            options=SEVERITY_OPTIONS,
            help_text="Your best estimate of how negatively stakeholders will be impacted by this flaw in a worst-case scenario.",
            info_text="How negatively stakeholders may be impacted"
        )
        severity = severity_field.to_streamlit()
    with col2:
        prevalence_field = FormEntry(
            name="Prevalence",
            title="Prevalence",
            input_type=InputType.SELECT_SLIDER,
            options=PREVALENCE_OPTIONS,
            help_text="Your best estimate of how common the flaw may be, i.e. how often the flaw might occur across AI systems.",
            info_text="How common the flaw is"
        )
        prevalence = prevalence_field.to_streamlit()
    
    # Impacts and Stakeholders
    col1, col2 = st.columns(2)
    with col1:
        impacts_field = FormEntry(
            name="Impacts",
            title="Impacts",
            input_type=InputType.MULTISELECT,
            options=IMPACT_OPTIONS,
            help_text="Choose one or more impacts that affected stakeholders may experience if the flaw is not addressed.",
            info_text="Impacts that may occur if the flaw is not addressed"
        )
        impacts = impacts_field.to_streamlit()
        impacts_other = handle_other_option(impacts, impacts, "Please specify other impacts:")
            
    with col2:
        stakeholders_field = FormEntry(
            name="Impacted Stakeholder(s)",
            title="Impacted Stakeholder(s)",
            input_type=InputType.MULTISELECT,
            options=STAKEHOLDER_OPTIONS,
            help_text="Choose one or more impacted stakeholders who may suffer if the flaw is not addressed.",
            info_text="Who is impacted if the flaw is not addressed"
        )
        impacted_stakeholders = stakeholders_field.to_streamlit()
        impacted_stakeholders_other = handle_other_option(impacted_stakeholders, impacted_stakeholders, 
                                                      "Please specify other impacted stakeholders:")
    
    # Risk Source and Bounty Eligibility
    col1, col2 = st.columns(2)
    with col1:
        risk_source_field = FormEntry(
            name="Risk Source",
            title="Risk Source",
            input_type=InputType.MULTISELECT,
            options=RISK_SOURCE_OPTIONS,
            help_text="Choose one or more presumed sources of the flaw.",
            info_text="Presumed sources of the flaw"
        )
        risk_source = risk_source_field.to_streamlit()
        risk_source_other = handle_other_option(risk_source, risk_source, "Please specify other risk sources:")
            
    with col2:
        bounty_field = FormEntry(
            name="Bounty Eligibility",
            title="Bounty Eligibility",
            input_type=InputType.RADIO,
            options=BOUNTY_OPTIONS,
            help_text="Whether this flaw is likely eligible for a bug bounty",
            info_text=""
        )
        bounty_eligibility = bounty_field.to_streamlit()
    
    return {
        "Context Info": context_info,
        "Flaw Description": flaw_description,
        "Policy Violation": policy_violation,
        "Severity": severity,
        "Prevalence": prevalence,
        "Impacts": impacts,
        "Impacts_Other": impacts_other,
        "Impacted Stakeholder(s)": impacted_stakeholders,
        "Impacted_Stakeholders_Other": impacted_stakeholders_other,
        "Risk Source": risk_source,
        "Risk_Source_Other": risk_source_other,
        "Bounty Eligibility": bounty_eligibility
    }

def display_real_world_event_fields():
    """Display fields for Real-World Events report type"""
    st.subheader("Real-World Event Details")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            incident_desc_field = FormEntry(
                name="Description of the Incident(s)",
                title="Description of the Incident(s)",
                input_type=InputType.TEXT_AREA,
                help_text="Describe the specific real-world event(s) that have occurred where this flaw caused harm, and what harm it caused.",
                info_text="The real-world event(s) where the flaw caused harm, and the harm caused"
            )
            incident_description = incident_desc_field.to_streamlit()
            
            implicated_systems_field = FormEntry(
                name="Implicated Systems",
                title="Implicated Systems",
                input_type=InputType.TEXT_AREA,
                help_text="Name any systems beyond the ones listed above that were involved in the real-world event(s).",
                info_text="Other systems involved in event"
            )
            implicated_systems = implicated_systems_field.to_streamlit()
        
        with col2:
            submitter_relation_field = FormEntry(
                name="Submitter Relationship",
                title="Submitter Relationship",
                input_type=InputType.SELECT,
                options=["Affected stakeholder", "Independent observer", "System developer", "Other"],
                help_text="Describe your relationship to the event.",
                info_text="Your relationship to event"
            )
            submitter_relationship = submitter_relation_field.to_streamlit()
            submitter_relationship_other = handle_other_option(submitter_relationship, submitter_relationship, 
                                                             "Please specify your relationship:")
            
            event_dates_field = FormEntry(
                name="Event Date(s)",
                title="Event Date(s)",
                input_type=InputType.DATE,
                help_text="Enter the date and time when the real-world event occurred, or your best estimation. If the real-world event occurred multiple times, enter the full time range from the first occurrence to the most recent occurrence.",
                info_text="Start date / end date of event"
            )
            event_dates = event_dates_field.to_streamlit()
            
            event_locations_field = FormEntry(
                name="Event Location(s)",
                title="Event Location(s)",
                input_type=InputType.TEXT,
                help_text="Enter the geographical location in which the real-world event occurred.",
                info_text="Geographical location of event"
            )
            event_locations = event_locations_field.to_streamlit()
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            harm_types_field = FormEntry(
                name="Experienced Harm Types",
                title="Experienced Harm Types",
                input_type=InputType.MULTISELECT,
                options=HARM_TYPES,
                help_text="Choose one or more types of harm that resulted from the real-world event(s) involving this flaw.",
                info_text="Harm caused by the event"
            )
            experienced_harm_types = harm_types_field.to_streamlit()
            harm_types_other = handle_other_option(experienced_harm_types, experienced_harm_types, 
                                                "Please specify other harm types:")
        
        with col2:
            harm_severity_field = FormEntry(
                name="Experienced Harm Severity",
                title="Experienced Harm Severity",
                input_type=InputType.SELECT_SLIDER,
                options=HARM_SEVERITY_OPTIONS,
                help_text="Your best estimate of how severe the harm caused is.",
                info_text="Severity of the harm caused by the event"
            )
            experienced_harm_severity = harm_severity_field.to_streamlit()
    
    harm_narrative_field = FormEntry(
        name="Harm Narrative",
        title="Harm Narrative (justification of why the event constitutes harm)",
        input_type=InputType.TEXT_AREA,
        help_text="Please describe why the real-world event that occurred is harmful, and how the flaw contributed to it.",
        info_text="Why the event is harmful and how the flaw contributed to it"
    )
    harm_narrative = harm_narrative_field.to_streamlit()
    
    return {
        "Description of the Incident(s)": incident_description,
        "Implicated Systems": implicated_systems,
        "Submitter Relationship": submitter_relationship,
        "Submitter_Relationship_Other": submitter_relationship_other,
        "Event Date(s)": event_dates.isoformat() if event_dates else None,
        "Event Location(s)": event_locations,
        "Experienced Harm Types": experienced_harm_types,
        "Harm_Types_Other": harm_types_other,
        "Experienced Harm Severity": experienced_harm_severity,
        "Harm Narrative": harm_narrative
    }

def display_malign_actor_fields():
    """Display fields for Malign Actor report type"""
    st.subheader("Malign Actor Details")
    
    col1, col2 = st.columns(2)
    with col1:
        tactic_field = FormEntry(
            name="Tactic Select",
            title="Tactic Select (e.g., from MITRE's ATLAS Matrix)",
            input_type=InputType.MULTISELECT,
            options=TACTIC_OPTIONS,
            help_text="Choose one or more tactics that could be used to exploit the flaw.",
            info_text="Tactic(s) that could be used to exploit the flaw"
        )
        tactic_select = tactic_field.to_streamlit()
        tactic_select_other = handle_other_option(tactic_select, tactic_select, "Please specify other tactics:")
            
    with col2:
        impact_field = FormEntry(
            name="Impact",
            title="Impact",
            input_type=InputType.MULTISELECT,
            options=IMPACT_TYPE_OPTIONS,
            help_text="Describe the potential impact of the flaw.",
            info_text="Potential impact of the flaw"
        )
        impact = impact_field.to_streamlit()
        impact_other = handle_other_option(impact, impact, "Please specify other impacts:")
    
    return {
        "Tactic Select": tactic_select,
        "Tactic_Select_Other": tactic_select_other,
        "Impact": impact,
        "Impact_Other": impact_other
    }

def display_security_incident_fields():
    """Display fields for Security Incident report type"""
    st.subheader("Security Incident Details")
    
    col1, col2 = st.columns(2)
    with col1:
        threat_actor_field = FormEntry(
            name="Threat Actor Intent",
            title="Threat Actor Intent",
            input_type=InputType.RADIO,
            options=THREAT_ACTOR_INTENT_OPTIONS,
            help_text="Describe the intent of the threat actor.",
            info_text="Intent of the threat actor"
        )
        threat_actor_intent = threat_actor_field.to_streamlit()
        threat_actor_intent_other = handle_other_option(threat_actor_intent, threat_actor_intent, 
                                                     "Please specify other threat actor intent:")
            
    with col2:
        detection_field = FormEntry(
            name="Detection",
            title="Detection",
            input_type=InputType.MULTISELECT,
            options=DETECTION_METHODS,
            help_text="Describe how you came to know about this real-world event, including which methods you used to discover and observe it.",
            info_text="How you learnt about flaw"
        )
        detection = detection_field.to_streamlit()
        detection_other = handle_other_option(detection, detection, "Please specify other detection methods:")
    
    return {
        "Threat Actor Intent": threat_actor_intent,
        "Threat_Actor_Intent_Other": threat_actor_intent_other,
        "Detection": detection,
        "Detection_Other": detection_other
    }

def display_vulnerability_fields():
    """Display fields for Vulnerability report type"""
    st.subheader("Vulnerability Details")
    
    poc_field = FormEntry(
        name="Proof-of-Concept Exploit",
        title="Proof-of-Concept Exploit",
        input_type=InputType.TEXT_AREA,
        help_text="Provide code and documentation that proves the existence of a vulnerability.",
        info_text="Code and documentation documenting the vulnerability"
    )
    proof_of_concept = poc_field.to_streamlit()
    
    return {
        "Proof-of-Concept Exploit": proof_of_concept
    }

def display_hazard_fields():
    """Display fields for Hazard report type"""
    st.subheader("Hazard Details")
    
    examples_field = FormEntry(
        name="Examples",
        title="Examples (list of system inputs/outputs)",
        input_type=InputType.TEXT_AREA,
        help_text="Provide a list of AI system inputs/outputs that help understand how to reproduce the flaw.",
        info_text="AI system inputs/outputs that help reproduce the flaw"
    )
    examples = examples_field.to_streamlit()
    
    replication_field = FormEntry(
        name="Replication Packet",
        title="Replication Packet (files evidencing the flaw)",
        input_type=InputType.TEXT_AREA,
        help_text="Provide data that helps reproduce the flaw, e.g. test data, custom evaluations or structured datasets used.",
        info_text="Data that help reproduce the flaw"
    )
    replication_packet = replication_field.to_streamlit()
    
    statistical_field = FormEntry(
        name="Statistical Argument",
        title="Statistical Argument (supporting evidence of a flaw)",
        input_type=InputType.TEXT_AREA,
        help_text="Provide your reasoning why this flaw is statistically likely to reoccur and not a one-off event.",
        info_text="Reasoning why this flaw is statistically likely to reoccur"
    )
    statistical_argument = statistical_field.to_streamlit()
    
    return {
        "Examples": examples,
        "Replication Packet": replication_packet,
        "Statistical Argument": statistical_argument
    }

def display_disclosure_plan():
    """Display fields for public disclosure plan"""
    st.subheader("Public Disclosure Plan")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            disclosure_intent_field = FormEntry(
                name="Disclosure Intent",
                title="Do you intend to publicly disclose this issue?",
                input_type=InputType.RADIO,
                options=["Yes", "No", "Undecided"],
                help_text="Required field",
                info_text=""
            )
            disclosure_intent = disclosure_intent_field.to_streamlit()
            
            if disclosure_intent == "Yes":
                disclosure_timeline_field = FormEntry(
                    name="Disclosure Timeline",
                    title="Planned disclosure timeline",
                    input_type=InputType.SELECT,
                    options=["Immediate (0 days)", "Short-term (1-30 days)", "Medium-term (31-90 days)", "Long-term (90+ days)"],
                    help_text="When do you plan to publicly disclose this issue?",
                    info_text=""
                )
                disclosure_timeline = disclosure_timeline_field.to_streamlit()
            else:
                disclosure_timeline = None
            
        with col2:
            if disclosure_intent == "Yes":
                disclosure_channels_field = FormEntry(
                    name="Disclosure Channels",
                    title="Disclosure channels",
                    input_type=InputType.MULTISELECT,
                    options=["Academic paper", "Blog post", "Social media", "Media outlet", "Conference presentation", "Other"],
                    help_text="Where do you plan to disclose this issue?",
                    info_text=""
                )
                disclosure_channels = disclosure_channels_field.to_streamlit()
                disclosure_channels_other = handle_other_option(disclosure_channels, disclosure_channels, 
                                                  "Please specify other disclosure channels:")
            else:
                disclosure_channels = []
                disclosure_channels_other = ""
    
    # Only show embargo request if they plan to disclose
    if disclosure_intent == "Yes":
        embargo_field = FormEntry(
            name="Embargo Request",
            title="Embargo request details",
            input_type=InputType.TEXT_AREA,
            help_text="If you're requesting an embargo period before public disclosure, please provide details",
            info_text=""
        )
        embargo_request = embargo_field.to_streamlit()
    else:
        embargo_request = ""
    
    return {
        "Disclosure Intent": disclosure_intent,
        "Disclosure Timeline": disclosure_timeline,
        "Disclosure Channels": disclosure_channels,
        "Disclosure_Channels_Other": disclosure_channels_other,
        "Embargo Request": embargo_request,
    }