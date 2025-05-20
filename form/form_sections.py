import streamlit as st
from form.utils.helpers import handle_other_option
from form.data.constants import *
from form.form_entry import FormEntry, InputType
import uuid
from form.data.hf_get_models import get_systems_options

def display_basic_information():
    """Display and gather basic information section using FormEntry"""
    st.subheader("Basic Information")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_field = FormEntry(
                name="Reporter ID",
                title="Reporter ID (anonymous or real identity)",
                input_type=InputType.TEXT,
                help_text="Enter your anonymous or real identity.",
                required=True
            )
            reporter_id = reporter_field.to_streamlit()
            
            report_id_field = FormEntry(
                name="Report ID",
                title="Report ID",
                input_type=InputType.TEXT,
                default=st.session_state.report_id,
                help_text="This automatically generated report ID allows us to keep track of the submission when it is processed. The report ID can be referenced in future submissions and mitigation efforts.",
                extra_params={"disabled": True}
            )
            report_id = report_id_field.to_streamlit()
            
            # Toggle to enable/disable Hugging Face API (for future debugging if necessary)
            use_api = st.sidebar.checkbox("Use Hugging Face API for models", value=True)
            
            systems_options = get_systems_options(use_api=use_api)
            
            systems_field = FormEntry(
                name="Systems",
                title="Systems",
                input_type=InputType.MULTISELECT,
                options=systems_options,
                help_text="Select one or more AI systems and versions involved in the flaw you are reporting."
            )
            systems = systems_field.to_streamlit()
            systems_other = handle_other_option(systems, systems, "Please specify other systems:")
        
        with col2:
            status_field = FormEntry(
                name="Report Status",
                title="Report Status",
                input_type=InputType.SELECT,
                options=REPORT_STATUS_OPTIONS,
                help_text="This field is auto-filled."
            )
            report_status = status_field.to_streamlit()
            
            session_field = FormEntry(
                name="Session ID",
                title="Session ID",
                input_type=InputType.TEXT,
                help_text="Enter the session link or session ID for a session that shows the flaw you encountered if available. For example, many chatbots have a \"Share\" feature located at a top that can generate a link that you can share with others so that they have access to your chat. We will not share this link in the public AI flaw database to ensure no private information is accidentally shared too broadly."
            )
            session_id = session_field.to_streamlit()
            
            timestamp_col1, timestamp_col2 = st.columns(2)
            with timestamp_col1:
                start_date_field = FormEntry(
                    name="Flaw Timestamp Start",
                    title="Flaw Timestamp Start",
                    input_type=InputType.DATE,
                    help_text="Enter the date and time when you encountered the flaw, or your best estimation."
                )
                flaw_timestamp_start = start_date_field.to_streamlit()
            with timestamp_col2:
                end_date_field = FormEntry(
                    name="Flaw Timestamp End",
                    title="Flaw Timestamp End",
                    input_type=InputType.DATE,
                    help_text="If the flaw occurred multiple times, enter the full time range from the first occurrence to the most recent occurrence."
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
        "Systems_Other": systems_other
    }

def display_common_fields():
    """Display and gather common fields section"""
    st.subheader("Common Fields")
    
    context_info = st.text_area("Context Info (versions of other software/hardware involved)", 
                             help="Enter the versions of other software or hardware systems involved in the flaw if applicable. For example, if you used an open-source model, add information on the hardware you are running it on.")
    
    # Flaw Description and Policy Violation
    flaw_description = st.text_area("Flaw Description (identification, reproduction, how it violates system policies)", 
                                 help="Describe the flaw, how you identified it, how it can be reproduced, and how it violates user expectations of the AI system or AI system policies. Add as much detail as possible to help reproduce and mitigate the flaw.")
    
    policy_violation = st.text_area("Policy Violation (how expectations of the system are violated)", 
                                 help="Point to relevant evidence that shows how the expectations of the system are violated or undocumented, for example by pointing to the terms of use, acceptable use policy, system card, or other documentation. Policies may be explicitly or implicitly violated.")
    
    # Severity and Prevalence
    col1, col2 = st.columns(2)
    with col1:
        severity = st.select_slider("Severity", options=SEVERITY_OPTIONS, 
                                  help="Your best estimate of how negatively stakeholders will be impacted by this flaw in a worst-case scenario.")
    with col2:
        prevalence = st.select_slider("Prevalence", options=PREVALENCE_OPTIONS, 
                                    help="Your best estimate of how common the flaw may be, i.e. how often the flaw might occur across AI systems.")
    
    # Impacts and Stakeholders
    col1, col2 = st.columns(2)
    with col1:
        impacts = st.multiselect("Impacts", options=IMPACT_OPTIONS, 
                               help="Choose one or more impacts that affected stakeholders may experience if the flaw is not addressed.")
        impacts_other = handle_other_option(impacts, impacts, "Please specify other impacts:")
            
    with col2:
        impacted_stakeholders = st.multiselect("Impacted Stakeholder(s)", options=STAKEHOLDER_OPTIONS, 
                                             help="Choose one or more impacted stakeholders who may suffer if the flaw is not addressed.")
        impacted_stakeholders_other = handle_other_option(impacted_stakeholders, impacted_stakeholders, 
                                                      "Please specify other impacted stakeholders:")
    
    # Risk Source and Bounty Eligibility
    col1, col2 = st.columns(2)
    with col1:
        risk_source = st.multiselect("Risk Source", options=RISK_SOURCE_OPTIONS, 
                                   help="Choose one or more presumed sources of the flaw.")
        risk_source_other = handle_other_option(risk_source, risk_source, "Please specify other risk sources:")
            
    with col2:
        bounty_eligibility = st.radio("Bounty Eligibility", options=BOUNTY_OPTIONS)
    
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
            incident_description = st.text_area("Description of the Incident(s)", 
                                             help="Describe the specific real-world event(s) that have occurred where this flaw caused harm, and what harm it caused.")
            implicated_systems = st.text_area("Implicated Systems", 
                                           help="Name any systems beyond the ones listed above that were involved in the real-world event(s).")
        
        with col2:
            submitter_relationship = st.selectbox("Submitter Relationship", 
                                               options=["Affected stakeholder", "Independent observer", "System developer", "Other"],
                                               help="Describe your relationship to the event.")
            submitter_relationship_other = handle_other_option(submitter_relationship, submitter_relationship, 
                                                             "Please specify your relationship:")
                
            event_dates = st.date_input("Event Date(s)", 
                                      help="Enter the date and time when the real-world event occurred, or your best estimation. If the real-world event occurred multiple times, enter the full time range from the first occurrence to the most recent occurrence.")
            event_locations = st.text_input("Event Location(s)", 
                                         help="Enter the geographical location in which the real-world event occurred.")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            experienced_harm_types = st.multiselect("Experienced Harm Types", options=HARM_TYPES, 
                                                  help="Choose one or more types of harm that resulted from the real-world event(s) involving this flaw.")
            harm_types_other = handle_other_option(experienced_harm_types, experienced_harm_types, 
                                                "Please specify other harm types:")
        
        with col2:
            experienced_harm_severity = st.select_slider("Experienced Harm Severity", options=HARM_SEVERITY_OPTIONS, 
                                                       help="Your best estimate of how severe the harm caused is.")
    
    harm_narrative = st.text_area("Harm Narrative (justification of why the event constitutes harm)", 
                               help="Please describe why the real-world event that occurred is harmful, and how the flaw contributed to it.")
    
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
        tactic_select = st.multiselect("Tactic Select (e.g., from MITRE's ATLAS Matrix)", options=TACTIC_OPTIONS, 
                                     help="Choose one or more tactic that could be used to exploit the flaw.")
        tactic_select_other = handle_other_option(tactic_select, tactic_select, "Please specify other tactics:")
            
    with col2:
        impact = st.multiselect("Impact", options=IMPACT_TYPE_OPTIONS, 
                              help="Describe the potential impact of the flaw.")
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
        threat_actor_intent = st.radio("Threat Actor Intent", options=THREAT_ACTOR_INTENT_OPTIONS, 
                                     help="Describe the intent of the threat actor.")
        threat_actor_intent_other = handle_other_option(threat_actor_intent, threat_actor_intent, 
                                                     "Please specify other threat actor intent:")
            
    with col2:
        detection = st.multiselect("Detection", options=DETECTION_METHODS, 
                                 help="Describe how you came to know about this real-world event, including which methods you used to discover and observe it.")
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
    
    proof_of_concept = st.text_area("Proof-of-Concept Exploit", 
                                 help="Provide code and documentation that proves the existence of a vulnerability.")
    
    return {
        "Proof-of-Concept Exploit": proof_of_concept
    }

def display_hazard_fields():
    """Display fields for Hazard report type"""
    st.subheader("Hazard Details")
    
    examples = st.text_area("Examples (list of system inputs/outputs)", 
                          help="Provide a list of system inputs/outputs that help understand how to replicate the flaw.")
    
    replication_packet = st.text_area("Replication Packet (files evidencing the flaw)", 
                                   help="Provide data that helps replicate the flaw, e.g. test data, custom evaluations or structured datasets used.")
    
    statistical_argument = st.text_area("Statistical Argument (supporting evidence of a flaw)", 
                                     help="Provide your reasoning why this flaw is statistically likely to occur and not a one-off event.")
    
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
            disclosure_intent = st.radio(
                "Do you intend to publicly disclose this issue?",
                options=["Yes", "No", "Undecided"],
                help="Required field"
            )
            
            if disclosure_intent == "Yes":
                disclosure_timeline = st.selectbox(
                    "Planned disclosure timeline",
                    options=["Immediate (0 days)", "Short-term (1-30 days)", "Medium-term (31-90 days)", "Long-term (90+ days)"],
                    help="When do you plan to publicly disclose this issue?"
                )
            else:
                disclosure_timeline = None
            
        with col2:
            if disclosure_intent == "Yes":
                disclosure_channels = st.multiselect(
                    "Disclosure channels",
                    options=["Academic paper", "Blog post", "Social media", "Media outlet", "Conference presentation", "Other"],
                    help="Where do you plan to disclose this issue?"
                )
                disclosure_channels_other = handle_other_option(disclosure_channels, disclosure_channels, 
                                                  "Please specify other disclosure channels:")
            else:
                disclosure_channels = []
                disclosure_channels_other = ""
    
    # Only show embargo request if they plan to disclose
    if disclosure_intent == "Yes":
        embargo_request = st.text_area(
            "Embargo request details",
            help="If you're requesting an embargo period before public disclosure, please provide details"
        )
    else:
        embargo_request = ""
    
    return {
        "Disclosure Intent": disclosure_intent,
        "Disclosure Timeline": disclosure_timeline,
        "Disclosure Channels": disclosure_channels,
        "Disclosure_Channels_Other": disclosure_channels_other,
        "Embargo Request": embargo_request,
    }