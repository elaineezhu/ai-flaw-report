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
    
    use_api = True
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            contact_info = form_entries["contact_info"].to_streamlit()
            
            systems_options = get_systems_options(use_api=use_api)
            
            form_entries["ai_systems"].options = systems_options
            form_entries["ai_systems"].extra_params = {
                "key": "systems_selections",
                "placeholder": "Choose AI systems..."
            }
            
            systems = form_entries["ai_systems"].to_streamlit()
        
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
    
    report_types = st.session_state.get('report_types', [])
    is_incident = "Real-World Incidents" in report_types or "Security Incident Report" in report_types
    
    if is_incident:
        st.subheader("Incident Description")
        st.markdown("Please provide detailed information about the incident in the following sections:")
        
        incident_detailed = form_entries["incident_description_detailed"].to_streamlit()
        
        combined_incident_description = f"""**Detailed Description:**
        {incident_detailed or ''}
        """
        
    else:
        st.subheader("Flaw Description")
        st.markdown("""
        Describe the following about the flaw:
        * **(1)** a detailed description of the flaw,
        * **(2)** what undesirable outputs, effects, or impacts you observed,
        * **(3)** how specifically to reproduce it (the inputs, actions, and/or links to any code), and
        * **(4)** for probabilistic flaws, have you shown/verified it happens systematically for many inputs or conditions?
        """)
        
        flaw_detailed = form_entries["flaw_description_detailed"].to_streamlit()
        
        combined_flaw_description = f"""**Detailed Description:**
        {flaw_detailed or ''}
        """
    selected_systems = st.session_state.get('systems_selections', [])
    display_policy_links(selected_systems)
    policy_violation = form_entries["policy_violation"].to_streamlit()
    
    # Risks and Impacts section
    st.subheader("Risks and Impacts")
    
    col1, col2 = st.columns(2)
    with col1:
        prevalence = form_entries["prevalence"].to_streamlit()
    with col2:
        if is_incident:
            severity = form_entries["experienced_harm_severity"].to_streamlit()
        else:
            severity = form_entries["severity"].to_streamlit()
    
    col1, col2 = st.columns(2)
    with col1:
        # Conditionally display the appropriate impacts form entry
        if "Real-World Incidents" in report_types:
            impacts = form_entries["experienced_harm_types"].to_streamlit()
            
        elif "Malign Actor" in report_types:
            impacts = form_entries["malign_actor_impacts"].to_streamlit()
            
        else:
            impacts = form_entries["impacts"].to_streamlit()
        
        impacts_other = ""
        if impacts and "Other" in impacts:
            impacts_other = st.text_input(
                "Please specify other impacts/harms:",
                key="impacts_other_specify"
            )
            
    with col2:
        impacted_stakeholders = form_entries["impacted_stakeholders"].to_streamlit()

        impacted_stakeholders_other = ""
        if impacted_stakeholders and "Other" in impacted_stakeholders:
            impacted_stakeholders_other = st.text_input(
                "Please specify other impacted stakeholders:",
                key="impacted_stakeholders_other_specify"
            )
    
    
    # Check if CSAM is selected and handle accordingly
    csam_selected = impacts and "Child sexual-abuse material (CSAM)" in impacts
    
    if csam_selected:
        st.error("""
        ## IMPORTANT: CSAM Reporting Guidelines
        
        **Reports involving CSAM cannot be submitted through this form. Please use the appropriate channels below.**
                
        ### What to do instead:
        1. Report to the **National Center for Missing & Exploited Children (NCMEC)** via their CyberTipline: https://report.cybertip.org/
        2. If outside the US, report to the **Internet Watch Foundation (IWF)**: https://report.iwf.org.uk/
        3. Report directly to the AI model developer through their official channels
        
        **To continue with this form, please deselect CSAM from the impacts list.**
        """)
        
        # Set CSAM flag to prevent submission
        st.session_state['csam_selected'] = True
    else:
        # Clear CSAM flag if not selected
        st.session_state['csam_selected'] = False
    
    # Risk Source
    col1, col2 = st.columns(2)
    risk_sources = form_entries["risk_source"].to_streamlit()
    
    if is_incident:
        description_key = "Incident Description"
        description_value = combined_incident_description
        return {
            description_key: description_value,
            "Incident Description - Detailed": incident_detailed,
            "Policy Violation": policy_violation,
            "Prevalence": prevalence,
            "Severity": severity,
            "Impacts": impacts, 
            "Impacts_Other": impacts_other,
            "Impacted Stakeholder(s)": impacted_stakeholders,
            "Risk Source(s)": risk_sources
        }
    else:
        description_key = "Flaw Description"
        description_value = combined_flaw_description
        return {
            description_key: description_value,
            "Flaw Description - Detailed": flaw_detailed,
            "Policy Violation": policy_violation,
            "Prevalence": prevalence,
            "Severity": severity,
            "Impacts": impacts, 
            "Impacts_Other": impacts_other,
            "Impacted Stakeholder(s)": impacted_stakeholders,
            "Risk Source(s)": risk_sources
        }


def display_real_world_event_fields():
    """Display fields for Real-World Events report type"""
    st.subheader("Real-World Incident Details")
    
    with st.container():
        submitter_relationship = form_entries["submitter_relationship"].to_streamlit()
        submitter_relationship_other = handle_other_option(submitter_relationship, submitter_relationship, 
                                                             "Please specify your relationship:")
            
        event_locations = form_entries["event_locations"].to_streamlit()
    
    harm_narrative = form_entries["harm_narrative"].to_streamlit()
    
    return {
        "Submitter Relationship": submitter_relationship,
        "Submitter_Relationship_Other": submitter_relationship_other,
        "Incident Location(s)": event_locations,
        "Harm Narrative": harm_narrative
    }

def display_malign_actor_fields():
    """Display fields for Malign Actor report type"""
    st.subheader("Malign Actor Details")
    
    tactic_select = form_entries["tactic_select"].to_streamlit()
    tactic_select_other = handle_other_option(tactic_select, tactic_select, "Please specify other tactics:")
        
    return {
        "Tactic Select": tactic_select,
        "Tactic_Select_Other": tactic_select_other,
    }

def display_security_incident_fields():
    """Display fields for Security Incident report type"""
    st.subheader("Security Incident Details")
    
    detection = form_entries["detection"].to_streamlit()
    detection_other = handle_other_option(detection, detection, "Please specify other detection methods:")
    
    return {
        "Detection": detection,
        "Detection_Other": detection_other
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
    """Display reproducibility section with context info, proof of concept, and file upload"""
    st.subheader("Reproducibility")
    st.markdown("Information needed to understand and reproduce the flaw")
    
    # Context Info
    context_info = form_entries["context_info"].to_streamlit()
    
    # Proof-of-Concept (moved from vulnerability section)
    proof_of_concept = form_entries["proof_of_concept"].to_streamlit()
    
    # File Upload
    st.markdown("**Upload Relevant Files**")
    st.caption("Please upload any files that pertain to the reproduction of the flaw being reported (eg. code, screenshots, documentation). Please title them and explain their contents in your written descriptions.")

    uploaded_files = st.file_uploader(
        "", 
        accept_multiple_files=True,
        # help="Please upload any files with instructions for how to exploit the flaw or evidence of the flaw being exploited (e.g., code and documentation). Please title them and refer to them in descriptions."
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.write(f"{len(uploaded_files)} file(s) uploaded")
    
    return {
        "Context Info": context_info,
        "Proof-of-Concept Exploit": proof_of_concept
    }

