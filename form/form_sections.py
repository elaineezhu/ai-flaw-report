import streamlit as st
from form.utils.helpers import handle_other_option
from form.data.hf_get_models import get_systems_options
from form.data.form_entries import form_entries
from form.report_type_logic import determine_report_types
from form.data.policy_mappings import display_policy_links
from form.data.constants import *
import uuid

def display_basic_information():
    """Display and gather basic information section using imported FormEntry objects"""
    st.subheader("Basic Information")
    
    with st.sidebar.expander("Models API Settings", expanded=False):
        use_api = st.checkbox("Use Hugging Face API for models", value=True)
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            contact_info = form_entries["contact_info"].to_streamlit()
            
            systems_options = get_systems_options(use_api=use_api)
            
            st.write("**AI System(s)**")
            st.caption("AI systems and versions involved in the flaw")
            
            systems = st.multiselect(
                label="AI System(s)",
                options=systems_options,
                default=None,
                help="Select one or more AI systems and versions involved in the flaw you are reporting.",
                placeholder="Choose AI systems...",
                key="systems_selections"
            )
        
        with col2:
            session_id = form_entries["session_id"].to_streamlit()
            
            involves_incident_types = (
                st.session_state.get('involves_real_world_incident')
            )
            
            report_types = determine_report_types(
                st.session_state.get('involves_real_world_incident'), 
                st.session_state.get('involves_threat_actor')
            )
            
            uses_incident_timestamp = any(report_type in report_types for report_type in [
                "Real-World Incidents", 
                "Security Incident Report"
            ])
            
            if uses_incident_timestamp:
                flaw_timestamp_start = form_entries["incident_timestamp_start"].to_streamlit()
            else:
                flaw_timestamp_start = form_entries["flaw_timestamp_start"].to_streamlit()
    
    reporter_id = contact_info if contact_info else f"anonymous-{str(uuid.uuid4())[:8]}"

    return {
        "Reporter ID": reporter_id,
        "Session ID": session_id,
        "Flaw Timestamp Start": flaw_timestamp_start.isoformat() if flaw_timestamp_start else None,
        "Systems": systems,
    }

def display_common_fields():
    """Display and gather common fields section with improved Risks and Impacts"""
    
    # Flaw Description
    flaw_description = form_entries["flaw_description"].to_streamlit()
    
    # Policy Violation
    st.write("**Policy Violation (how expectations of the system are violated)**")
    st.caption("Pointer to relevant policies, documentation, etc. showing that the flaw violates them")
    
    selected_systems = st.session_state.get('systems_selections', [])
    display_policy_links(selected_systems)
    
    policy_violation = st.text_area(
        label="",
        help="Provide evidence that the identified flaw is undesirable, or has violated expectations of the AI system. Ideally, point to a documented system policy, acceptable usage policy, or terms that indicate this is undesirable. Explain your reasoning.",
    )
    
    # Risks and Impacts section
    st.subheader("Risks and Impacts")
    
    col1, col2 = st.columns(2)
    with col1:
        prevalence = form_entries["prevalence"].to_streamlit()
    with col2:
        severity = form_entries["severity"].to_streamlit()
    
    # Impacts and Stakeholders
    col1, col2 = st.columns(2)
    with col1:
        st.multiselect(
                label="Impacts",
                options=IMPACT_OPTIONS,
                default=None,
                help="Choose impacts that affected stakeholders may experience if the flaw is not addressed.",
            )
            
    with col2:
        st.multiselect(
                label="Impacted Stakeholder(s)",
                options=STAKEHOLDER_OPTIONS,
                default=None,
                help="Choose stakeholders who may suffer if the flaw is not addressed.",
            )
    # Risk Source
    col1, col2 = st.columns(2)
    with col1:
        st.multiselect(
                label="Risk Source(s)",
                options=RISK_SOURCE_OPTIONS,
                default=None,
                help="Choose presumed sources of the flaw.",
            )
    
    return {
        "Flaw Description": flaw_description,
        "Policy Violation": policy_violation,
        "Prevalence": prevalence,
        "Severity": severity
    }

def display_real_world_event_fields():
    """Display fields for Real-World Events report type"""
    st.subheader("Real-World Incident Details")
    
    with st.container():
        submitter_relationship = form_entries["submitter_relationship"].to_streamlit()
        submitter_relationship_other = handle_other_option(submitter_relationship, submitter_relationship, 
                                                             "Please specify your relationship:")
            
        event_locations = form_entries["event_locations"].to_streamlit()
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            experienced_harm_types = form_entries["experienced_harm_types"].to_streamlit()
            harm_types_other = handle_other_option(experienced_harm_types, experienced_harm_types, 
                                                "Please specify other harm types:")
        
        with col2:
            experienced_harm_severity = form_entries["experienced_harm_severity"].to_streamlit()
    
    harm_narrative = form_entries["harm_narrative"].to_streamlit()
    
    return {
        "Submitter Relationship": submitter_relationship,
        "Submitter_Relationship_Other": submitter_relationship_other,
        "Incident Location(s)": event_locations,
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
        tactic_select = form_entries["tactic_select"].to_streamlit()
        tactic_select_other = handle_other_option(tactic_select, tactic_select, "Please specify other tactics:")
            
    with col2:
        impact = form_entries["impact"].to_streamlit()
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
        threat_actor_intent = form_entries["threat_actor_intent"].to_streamlit()
        threat_actor_intent_other = handle_other_option(threat_actor_intent, threat_actor_intent, 
                                                     "Please specify other threat actor intent:")
            
    with col2:
        detection = form_entries["detection"].to_streamlit()
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
    
    proof_of_concept = form_entries["proof_of_concept"].to_streamlit()
    
    return {
        "Proof-of-Concept Exploit": proof_of_concept
    }

def display_hazard_fields():
    """Display fields for Hazard report type"""
    st.subheader("Hazard Details")

    statistical_argument = form_entries["statistical_argument"].to_streamlit()
    
    return {
        "Statistical Argument with Examples": statistical_argument
    }

def display_disclosure_plan():
    """Display fields for public disclosure plan"""
    st.subheader("Public Disclosure Plan")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            disclosure_intent = form_entries["disclosure_intent"].to_streamlit()
            
            if disclosure_intent == "Yes":
                disclosure_timeline = form_entries["disclosure_timeline"].to_streamlit()
            else:
                disclosure_timeline = None
            
        with col2:
            if disclosure_intent == "Yes":
                disclosure_channels = form_entries["disclosure_channels"].to_streamlit()
                disclosure_channels_other = handle_other_option(disclosure_channels, disclosure_channels, 
                                                  "Please specify other disclosure channels:")
            else:
                disclosure_channels = []
                disclosure_channels_other = ""
    
    # Only show embargo request if they plan to disclose
    if disclosure_intent == "Yes":
        embargo_request = form_entries["embargo_request"].to_streamlit()
    else:
        embargo_request = ""
    
    return {
        "Disclosure Intent": disclosure_intent,
        "Disclosure Timeline": disclosure_timeline,
        "Disclosure Channels": disclosure_channels,
        "Disclosure_Channels_Other": disclosure_channels_other,
        "Embargo Request": embargo_request,
    }

def display_reproducibility():
    """Display reproducibility section with context info and file upload"""
    st.subheader("Reproducibility")
    st.caption("Information needed to understand and reproduce the flaw")
    
    # Context Info
    context_info = form_entries["context_info"].to_streamlit()
    
    # File Upload
    uploaded_files = st.file_uploader(
        "Upload Relevant Files", 
        accept_multiple_files=True,
        help="Any files that pertain to the reproducibility or documentation of the flaw. Please title them and refer to them in descriptions."
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.write(f"{len(uploaded_files)} file(s) uploaded")
    
    return {
        "Context Info": context_info
    }
