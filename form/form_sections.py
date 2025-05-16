import streamlit as st
from form.utils.helpers import handle_other_option
from form.data.constants import *

def display_basic_information():
    """Display and gather basic information section"""
    st.subheader("Basic Information")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_id = st.text_input("Reporter ID (anonymous or real identity)", 
                                      help="Required field")
            
            st.text_input("Report ID", st.session_state.report_id, disabled=True)
            
            systems = st.multiselect("Systems", options=SYSTEM_OPTIONS)
            systems_other = handle_other_option(systems, systems, "Please specify other systems:")
        
        with col2:
            report_status = st.selectbox("Report Status", options=REPORT_STATUS_OPTIONS)
            session_id = st.text_input("Session ID", help="Optional")
            
            timestamp_col1, timestamp_col2 = st.columns(2)
            with timestamp_col1:
                flaw_timestamp_start = st.date_input("Flaw Timestamp Start")
            with timestamp_col2:
                flaw_timestamp_end = st.date_input("Flaw Timestamp End")
    
    return {
        "Reporter ID": reporter_id,
        "Report ID": st.session_state.report_id,
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
                             help="Optional")
    
    # Flaw Description and Policy Violation
    flaw_description = st.text_area("Flaw Description (identification, reproduction, how it violates system policies)", 
                                 help="Required field")
    
    policy_violation = st.text_area("Policy Violation (how expectations of the system are violated)", 
                                 help="Required field")
    
    # Severity and Prevalence
    col1, col2 = st.columns(2)
    with col1:
        severity = st.select_slider("Severity", options=SEVERITY_OPTIONS)
    with col2:
        prevalence = st.select_slider("Prevalence", options=PREVALENCE_OPTIONS)
    
    # Impacts and Stakeholders
    col1, col2 = st.columns(2)
    with col1:
        impacts = st.multiselect("Impacts", options=IMPACT_OPTIONS, 
                               help="Required field")
        impacts_other = handle_other_option(impacts, impacts, "Please specify other impacts:")
            
    with col2:
        impacted_stakeholders = st.multiselect("Impacted Stakeholder(s)", options=STAKEHOLDER_OPTIONS, 
                                             help="Required field")
        impacted_stakeholders_other = handle_other_option(impacted_stakeholders, impacted_stakeholders, 
                                                      "Please specify other impacted stakeholders:")
    
    # Risk Source and Bounty Eligibility
    col1, col2 = st.columns(2)
    with col1:
        risk_source = st.multiselect("Risk Source", options=RISK_SOURCE_OPTIONS)
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
                                             help="Required field")
            implicated_systems = st.text_area("Implicated Systems", 
                                           help="Required field")
        
        with col2:
            submitter_relationship = st.selectbox("Submitter Relationship", 
                                               options=["Affected stakeholder", "Independent observer", "System developer", "Other"])
            submitter_relationship_other = handle_other_option(submitter_relationship, submitter_relationship, 
                                                             "Please specify your relationship:")
                
            event_dates = st.date_input("Event Date(s)")
            event_locations = st.text_input("Event Location(s)", 
                                         help="Required field")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            experienced_harm_types = st.multiselect("Experienced Harm Types", options=HARM_TYPES, 
                                                  help="Required field")
            harm_types_other = handle_other_option(experienced_harm_types, experienced_harm_types, 
                                                "Please specify other harm types:")
        
        with col2:
            experienced_harm_severity = st.select_slider("Experienced Harm Severity", options=HARM_SEVERITY_OPTIONS)
    
    harm_narrative = st.text_area("Harm Narrative (justification of why the event constitutes harm)", 
                               help="Required field")
    
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
                                     help="Required field")
        tactic_select_other = handle_other_option(tactic_select, tactic_select, "Please specify other tactics:")
            
    with col2:
        impact = st.multiselect("Impact", options=IMPACT_TYPE_OPTIONS, 
                              help="Required field")
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
        threat_actor_intent = st.radio("Threat Actor Intent", options=THREAT_ACTOR_INTENT_OPTIONS)
        threat_actor_intent_other = handle_other_option(threat_actor_intent, threat_actor_intent, 
                                                     "Please specify other threat actor intent:")
            
    with col2:
        detection = st.multiselect("Detection", options=DETECTION_METHODS, 
                                 help="Required field")
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
                                 help="Required field")
    
    return {
        "Proof-of-Concept Exploit": proof_of_concept
    }

def display_hazard_fields():
    """Display fields for Hazard report type"""
    st.subheader("Hazard Details")
    
    examples = st.text_area("Examples (list of system inputs/outputs)", 
                          help="Required field")
    
    replication_packet = st.text_area("Replication Packet (files evidencing the flaw)", 
                                   help="Required field")
    
    statistical_argument = st.text_area("Statistical Argument (supporting evidence of a flaw)", 
                                     help="Required field")
    
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