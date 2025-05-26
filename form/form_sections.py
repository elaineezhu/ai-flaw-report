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
    
    # Flaw Description
    report_types = st.session_state.get('report_types', [])
    is_incident = "Real-World Incidents" in report_types or "Security Incident Report" in report_types
    
    if is_incident:
        flaw_description = form_entries["incident_description"].to_streamlit()
    else:
        flaw_description = form_entries["flaw_description"].to_streamlit()
    
    # Policy Violation
    st.markdown("**Policy Violation (how expectations of the system are violated)** <span style='color:red'>*</span>", unsafe_allow_html=True)
    st.caption("Pointer to relevant policies, documentation, etc. showing that the flaw violates them")
    
    selected_systems = st.session_state.get('systems_selections', [])
    display_policy_links(selected_systems)
    
    policy_violation = st.text_area(
        label="",
        help="Provide evidence that the identified flaw is undesirable, or has violated expectations of the AI system. Ideally, point to a documented system policy, acceptable usage policy, or terms that indicate this is undesirable. Explain your reasoning. (Required)",
        key="policy_violation"
    )
    
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
        impact_options = []
        impact_label = "Impacts"
        impact_help = "Choose impacts that affected stakeholders may experience if the flaw is not addressed."
        
        if "Real-World Incidents" in report_types:
            impact_options = EXPERIENCED_HARM_OPTIONS
            impact_label = "Experienced Harm Types"
            impact_help = "Choose the types of harm that were experienced in this incident."
            
        elif "Malign Actor" in report_types:
            impact_options = MALIGN_ACTOR_IMPACT_OPTIONS
            impact_label = "Malign Actor Impacts"
            impact_help = "Choose the types of impacts from malign actor activities."
            
        else:
            impact_options = IMPACT_OPTIONS
        
        st.markdown(f"**{impact_label}** <span style='color:red'>*</span>", unsafe_allow_html=True)
        impacts = st.multiselect(
            label="",
            options=impact_options,
            default=None,
            help=f"{impact_help} (Required)",
            key="unified_impacts_select"
        )
        
        # Handle "Other" option if selected
        impacts_other = ""
        if impacts and "Other" in impacts:
            impacts_other = st.text_input(
                "Please specify other impacts/harms:",
                key="impacts_other_specify"
            )
            
    with col2:
        st.markdown("**Impacted Stakeholder(s)** <span style='color:red'>*</span>", unsafe_allow_html=True)
        impacted_stakeholders = st.multiselect(
                label="",
                options=STAKEHOLDER_OPTIONS,
                default=None,
                help="Choose stakeholders who may suffer if the flaw is not addressed. (Required)",
                key="stakeholders_select"
            )
    
    # Handle CSAM warning if selected
    if impacts and "Child sexual-abuse material (CSAM)" in impacts:
        st.error("""
        ## IMPORTANT: CSAM Reporting Guidelines
        
        **Possession and distribution of CSAM and AI-generated CSAM is illegal. Do not include illegal media in this report.**
        
        ### What to do instead:
        1. Report to the **National Center for Missing & Exploited Children (NCMEC)** via their CyberTipline: https://report.cybertip.org/
        2. If outside the US, report to the **Internet Watch Foundation (IWF)**: https://report.iwf.org.uk/
        3. Report directly to the AI model developer through their official channels
        
        Only share information about the nature of the issue, WITHOUT including illegal content, prompts that could generate illegal content, or specific details that could enable others to recreate the issue.
        
        This report will be restricted to appropriate stakeholders on a need-to-know basis.
        """)
        
        # Store CSAM acknowledgment state in session state
        csam_acknowledge = st.checkbox("I acknowledge these guidelines and confirm this report does NOT contain illegal media", key="csam_acknowledge_unified")
        st.session_state['csam_acknowledged'] = csam_acknowledge
    else:
        # If CSAM is not selected, set acknowledgment to True
        st.session_state['csam_acknowledged'] = True
    
    # Risk Source
    col1, col2 = st.columns(2)
    st.markdown("**Risk Source(s)**", unsafe_allow_html=True)
    risk_sources = st.multiselect(
            label="",
            options=RISK_SOURCE_OPTIONS,
            default=None,
            help="Choose presumed sources of the flaw.",
            key="risk_sources_select"
        )
    
    description_key = "Incident Description" if is_incident else "Flaw Description"
    
    return {
        description_key: flaw_description,
        "Policy Violation": policy_violation,
        "Prevalence": prevalence,
        "Severity": severity,
        "Impacts": impacts, 
        "Impacts_Other": impacts_other,
        "Impacted Stakeholder(s)": impacted_stakeholders,
        "Risk Source(s)": risk_sources
    }

def display_real_world_event_fields():
    """Display fields for Real-World Events report type - REMOVED experienced_harm_types"""
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
    """Display fields for Malign Actor report type - REMOVED impact field"""
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
