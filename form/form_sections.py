import streamlit as st
from form.utils.helpers import handle_other_option
from form.data.hf_get_models import searchable_model_selector, get_systems_options
from form.data.form_entries import form_entries
from form.data.hf_get_models import searchable_select_with_other 
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
            systems = searchable_model_selector(
                available_models=systems_options,
                key_prefix="systems",
                max_selections=20,
                help_text="Select one or more AI systems and versions involved in the flaw you are reporting."
            )
        
        with col2:
            session_id = form_entries["session_id"].to_streamlit()
            
            timestamp_col1, timestamp_col2 = st.columns(2)
            with timestamp_col1:
                flaw_timestamp_start = form_entries["flaw_timestamp_start"].to_streamlit()
            with timestamp_col2:
                flaw_timestamp_end = form_entries["flaw_timestamp_end"].to_streamlit()
    
    reporter_id = contact_info if contact_info else f"anonymous-{str(uuid.uuid4())[:8]}"

    return {
        "Reporter ID": reporter_id,
        "Session ID": session_id,
        "Flaw Timestamp Start": flaw_timestamp_start.isoformat() if flaw_timestamp_start else None,
        "Flaw Timestamp End": flaw_timestamp_end.isoformat() if flaw_timestamp_end else None,
        "Systems": systems,
    }

def display_common_fields():
    """Display and gather common fields section with improved Risks and Impacts"""
    
    # Flaw Description
    flaw_description = form_entries["flaw_description"].to_streamlit()
    
    # Policy Violation
    policy_violation = form_entries["policy_violation"].to_streamlit()
    
    # Context Info
    context_info = form_entries["context_info"].to_streamlit()
    
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
        impacts, impacts_other = searchable_select_with_other(
            available_models=IMPACT_OPTIONS,
            key_prefix="impacts",
            title="Impacts",
            caption="Choose impacts that affected stakeholders may experience if the flaw is not addressed",
            max_selections=10
        )
            
    with col2:
        impacted_stakeholders, impacted_stakeholders_other = searchable_select_with_other(
            available_models=STAKEHOLDER_OPTIONS,
            key_prefix="stakeholders",
            title="Impacted Stakeholder(s)",
            caption="Choose stakeholders who may suffer if the flaw is not addressed",
            max_selections=10
        )
    
    # Risk Source
    col1, col2 = st.columns(2)
    with col1:
        risk_source, risk_source_other = searchable_select_with_other(
            available_models=RISK_SOURCE_OPTIONS,
            key_prefix="risk_source",
            title="Risk Source",
            caption="Choose presumed sources of the flaw",
            max_selections=10
        )

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
    }

def display_real_world_event_fields():
    """Display fields for Real-World Events report type"""
    st.subheader("Real-World Incident Details")
    
    with st.container():
        submitter_relationship = form_entries["submitter_relationship"].to_streamlit()
        submitter_relationship_other = handle_other_option(submitter_relationship, submitter_relationship, 
                                                             "Please specify your relationship:")
            
        event_dates = form_entries["event_dates"].to_streamlit()
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
        "Incident Date(s)": event_dates.isoformat() if event_dates else None,
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