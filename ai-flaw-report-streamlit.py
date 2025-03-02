import streamlit as st
import json
from datetime import datetime
import uuid
import os

import constants

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'report_id' not in st.session_state:
        st.session_state.report_id = str(uuid.uuid4())
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    if 'report_types' not in st.session_state:
        st.session_state.report_types = []
    
    if 'common_data' not in st.session_state:
        st.session_state.common_data = {}
    
    if 'submission_status' not in st.session_state:
        st.session_state.submission_status = False
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Initialize classification question variables
    if 'involves_real_world_incident' not in st.session_state:
        st.session_state.involves_real_world_incident = None
    
    if 'involves_threat_actor' not in st.session_state:
        st.session_state.involves_threat_actor = None
        
    # Initialize radio button state variables
    if 'real_world_incident_radio' not in st.session_state:
        st.session_state.real_world_incident_radio = None
        
    if 'threat_actor_radio' not in st.session_state:
        st.session_state.threat_actor_radio = None

def determine_report_types():
    """Determine report types based on the answers to key questions"""
    report_types = []
    
    # Only determine report types if both questions have been answered
    if st.session_state.involves_real_world_incident is not None and st.session_state.involves_threat_actor is not None:
        # Determine report types based on answers
        if st.session_state.involves_real_world_incident and st.session_state.involves_threat_actor:
            report_types = ["Real-World Events", "Malign Actor", "Security Incident Report"]
        elif st.session_state.involves_real_world_incident:
            report_types = ["Real-World Events"]
        elif st.session_state.involves_threat_actor:
            report_types = ["Malign Actor", "Vulnerability Report"]
        else:
            report_types = ["Hazard Report"]
    
    return report_types

def validate_required_fields(form_data, required_fields):
    """Validate that all required fields are filled"""
    missing_fields = []
    
    for field in required_fields:
        if field not in form_data or not form_data[field]:
            missing_fields.append(field)
    
    return missing_fields

def generate_recommendations(form_data):
    """Generate recommendations based on form data"""
    recommendations = ["AI System Developer"]
    
    # Add recommendations based on severity
    if form_data.get("Severity") in ["Critical", "High"]:
        recommendations.append("Regulatory Authorities")
    
    # Add recommendations based on impact
    if "Financial" in form_data.get("Impacts", []) or "Financial" in form_data.get("Impacts_Other", ""):
        recommendations.append("Financial Oversight Bodies")
    
    if "Privacy" in form_data.get("Impacts", []) or "Privacy" in form_data.get("Impacts_Other", "") or "Confidentiality breach" in form_data.get("Impact", ""):
        recommendations.append("Data Protection Authority")
    
    if "Users" in form_data.get("Impacted Stakeholder(s)", []) or "Users" in form_data.get("Impacted_Stakeholders_Other", ""):
        recommendations.append("User Community Forums")
    
    # Add recommendations for real-world events
    if "Real-World Events" in form_data.get("Report Types", []):
        recommendations.append("Affected Community Representatives")
        
    # Add security incident specific recommendations
    if "Security Incident Report" in form_data.get("Report Types", []):
        recommendations.append("Computer Emergency Response Team (CERT)")
        
    return recommendations

def handle_submission():
    # Combine all data
    form_data = st.session_state.form_data.copy()
    form_data.update(st.session_state.common_data)
    form_data["Submission Timestamp"] = datetime.now().isoformat()
    
    # Handle uploaded files
    if st.session_state.uploaded_files:
        file_names = [file.name for file in st.session_state.uploaded_files]
        form_data["Uploaded Files"] = file_names
    
    # Store form data in session state
    st.session_state.form_data = form_data
    st.session_state.submission_status = True

def save_uploaded_files(uploaded_files):
    """Save uploaded files and return their paths"""
    file_paths = []
    for file in uploaded_files:
        # Create directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save file
        file_path = os.path.join("uploads", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        
        file_paths.append(file_path)
    
    return file_paths

def update_real_world_incident():
    st.session_state.involves_real_world_incident = st.session_state.real_world_incident

def update_threat_actor():
    st.session_state.involves_threat_actor = st.session_state.threat_actor

def handle_other_option(selection, options_list, label="Please specify other:"):
    """Reusable function to handle "Other" option in any selection component
    
    Args:
        selection: Current selection (list for multiselect, string for selectbox/radio)
        options_list: List of selected options or single selection
        label: Label for the text input field
        
    Returns:
        String with user-specified value if "Other" is selected, empty string otherwise
    """
    # Handle both multiselect (list) and single select (string) cases
    if isinstance(selection, list):
        if "Other" in selection:
            return st.text_area(label)
    else:  # selectbox or radio (string)
        if selection == "Other":
            return st.text_area(label)
    
    return ""

def display_basic_information():
    """Display and gather basic information section"""
    st.subheader("Basic Information")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_id = st.text_input("Reporter ID (anonymous or real identity)", 
                                      help="Required field")
            
            st.text_input("Report ID", st.session_state.report_id, disabled=True)
            
            # Systems moved to Basic Information
            systems = st.multiselect("Systems", options=constants.SYSTEM_OPTIONS)
            systems_other = handle_other_option(systems, systems, "Please specify other systems:")
        
        with col2:
            report_status = st.selectbox("Report Status", options=constants.REPORT_STATUS_OPTIONS)
            session_id = st.text_input("Session ID", help="Optional")
            
            # Timestamps side by side within column 2
            timestamp_col1, timestamp_col2 = st.columns(2)
            with timestamp_col1:
                flaw_timestamp_start = st.date_input("Flaw Timestamp Start", datetime.now())
            with timestamp_col2:
                flaw_timestamp_end = st.date_input("Flaw Timestamp End", datetime.now())
    
    # Store basic information
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
        severity = st.select_slider("Severity", options=constants.SEVERITY_OPTIONS)
    with col2:
        prevalence = st.select_slider("Prevalence", options=constants.PREVALENCE_OPTIONS)
    
    # Impacts and Stakeholders
    col1, col2 = st.columns(2)
    with col1:
        impacts = st.multiselect("Impacts", options=constants.IMPACT_OPTIONS, 
                               help="Required field")
        impacts_other = handle_other_option(impacts, impacts, "Please specify other impacts:")
            
    with col2:
        impacted_stakeholders = st.multiselect("Impacted Stakeholder(s)", options=constants.STAKEHOLDER_OPTIONS, 
                                             help="Required field")
        impacted_stakeholders_other = handle_other_option(impacted_stakeholders, impacted_stakeholders, 
                                                      "Please specify other impacted stakeholders:")
    
    # Risk Source and Bounty Eligibility
    col1, col2 = st.columns(2)
    with col1:
        risk_source = st.multiselect("Risk Source", options=constants.RISK_SOURCE_OPTIONS)
        risk_source_other = handle_other_option(risk_source, risk_source, "Please specify other risk sources:")
            
    with col2:
        bounty_eligibility = st.radio("Bounty Eligibility", options=constants.BOUNTY_OPTIONS)
    
    # Return common fields
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

def display_file_upload():
    """Display file upload section"""
    uploaded_files = st.file_uploader("Upload Relevant Files", accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.write(f"{len(uploaded_files)} file(s) uploaded")

def display_report_type_classification():
    """Display report type classification questions"""
    st.subheader("Report Type Classification")
    st.markdown("Please answer the following questions to determine the appropriate report type:")
    
    # Question 1: Real-world incident - Using radio with empty initial option
    st.radio(
        "Does this flaw report involve a real-world incident, where some form of harm has already occurred?",
        options=["", "Yes", "No"],
        index=0,  # Default to empty option
        key="real_world_incident_radio",
        on_change=update_real_world_incident_radio
    )
    st.caption("(e.g., injury or harm to people, disruption to infrastructure, violations of laws or rights, or harm to property, or communities)")
    
    # Question 2: Threat actor - Using radio with empty initial option
    st.radio(
        "Does this flaw report involve a threat actor (i.e. could be exploited with ill intent)?",
        options=["", "Yes", "No"],
        index=0,  # Default to empty option
        key="threat_actor_radio",
        on_change=update_threat_actor_radio
    )

def update_real_world_incident_radio():
    """Update the session state based on radio button selection"""
    if st.session_state.real_world_incident_radio == "Yes":
        st.session_state.involves_real_world_incident = True
    elif st.session_state.real_world_incident_radio == "No":
        st.session_state.involves_real_world_incident = False
    else:
        st.session_state.involves_real_world_incident = None

def update_threat_actor_radio():
    """Update the session state based on radio button selection"""
    if st.session_state.threat_actor_radio == "Yes":
        st.session_state.involves_threat_actor = True
    elif st.session_state.threat_actor_radio == "No":
        st.session_state.involves_threat_actor = False
    else:
        st.session_state.involves_threat_actor = None

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
                
            event_dates = st.date_input("Event Date(s)", datetime.now())
            event_locations = st.text_input("Event Location(s)", 
                                         help="Required field")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            experienced_harm_types = st.multiselect("Experienced Harm Types", options=constants.HARM_TYPES, 
                                                  help="Required field")
            harm_types_other = handle_other_option(experienced_harm_types, experienced_harm_types, 
                                                "Please specify other harm types:")
        
        with col2:
            experienced_harm_severity = st.select_slider("Experienced Harm Severity", options=constants.HARM_SEVERITY_OPTIONS)
    
    harm_narrative = st.text_area("Harm Narrative (justification of why the event constitutes harm)", 
                               help="Required field")
    
    # Return field data
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
        tactic_select = st.multiselect("Tactic Select (e.g., from MITRE's ATLAS Matrix)", options=constants.TACTIC_OPTIONS, 
                                     help="Required field")
        tactic_select_other = handle_other_option(tactic_select, tactic_select, "Please specify other tactics:")
            
    with col2:
        impact = st.multiselect("Impact", options=constants.IMPACT_TYPE_OPTIONS, 
                              help="Required field")
        impact_other = handle_other_option(impact, impact, "Please specify other impacts:")
    
    # Return field data
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
        threat_actor_intent = st.radio("Threat Actor Intent", options=constants.THREAT_ACTOR_INTENT_OPTIONS)
        threat_actor_intent_other = handle_other_option(threat_actor_intent, threat_actor_intent, 
                                                     "Please specify other threat actor intent:")
            
    with col2:
        detection = st.multiselect("Detection", options=constants.DETECTION_METHODS, 
                                 help="Required field")
        detection_other = handle_other_option(detection, detection, "Please specify other detection methods:")
    
    # Return field data
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
    
    # Return field data
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
    
    # Return field data
    return {
        "Examples": examples,
        "Replication Packet": replication_packet,
        "Statistical Argument": statistical_argument
    }

def show_report_submission_results(form_data):
    """Display submission results and recommendations"""
    # Generate recommendations
    recommendations = generate_recommendations(form_data)
    
    # Display JSON output and recommendations
    st.success("Report submitted successfully!")
    
    st.subheader("Form Data (JSON)")
    st.json(form_data)
    
    st.subheader("Recommended Recipients")
    for rec in recommendations:
        st.write(f"- {rec}")
    
    # Download button
    json_str = json.dumps(form_data, indent=4)
    st.download_button(
        label="Download JSON",
        data=json_str,
        file_name=f"ai_flaw_report_{form_data['Report ID']}.json",
        mime="application/json"
    )

def create_app():
    """Main function to create the Streamlit app"""
    st.set_page_config(page_title="AI Flaw Report Form", layout="wide")
    
    # Initialize session state
    initialize_session_state()
    
    # App title and description
    st.title("AI Flaw & Incident Report Form")
    st.markdown("""
    This form allows you to report flaws, vulnerabilities, or incidents related to AI systems. 
    The information you provide will help identify, categorize, and address potential issues.
    
    Please fill out the appropriate sections based on the type of report you're submitting.
    """)
    
    # Display form sections
    basic_info = display_basic_information()
    common_fields = display_common_fields()
    display_file_upload()
    
    # Store the common data
    st.session_state.common_data = {**basic_info, **common_fields}
    
    # Display report type classification questions
    display_report_type_classification()
    
    # Determine report types based on answers
    report_types = determine_report_types()
    
    # Only display the report type sections if both classification questions have been answered
    if st.session_state.involves_real_world_incident is not None and st.session_state.involves_threat_actor is not None:
        # Display selected report types
        st.subheader("Selected Report Types")
        st.write(", ".join(report_types))
        
        # Store report types in session state
        st.session_state.report_types = report_types
        
        # Now show conditional fields based on determined report types
        if report_types:
            st.session_state.form_data = {}  # Reset form data
            
            # Real-World Events fields
            if "Real-World Events" in report_types:
                real_world_fields = display_real_world_event_fields()
                st.session_state.form_data.update(real_world_fields)
            
            # Malign Actor fields
            if "Malign Actor" in report_types:
                malign_actor_fields = display_malign_actor_fields()
                st.session_state.form_data.update(malign_actor_fields)
            
            # Security Incident Report fields
            if "Security Incident Report" in report_types:
                security_incident_fields = display_security_incident_fields()
                st.session_state.form_data.update(security_incident_fields)
            
            # Vulnerability Report fields
            if "Vulnerability Report" in report_types:
                vulnerability_fields = display_vulnerability_fields()
                st.session_state.form_data.update(vulnerability_fields)
            
            # Hazard Report fields
            if "Hazard Report" in report_types:
                hazard_fields = display_hazard_fields()
                st.session_state.form_data.update(hazard_fields)
            
            # Add "Report Types" to the form data
            st.session_state.form_data["Report Types"] = report_types
            
            # Add visual separation before submit button
            st.markdown("---")
            st.markdown(" ")  # Add extra space
            
            # Submit button with enhanced styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.button("Submit Report", type="primary", use_container_width=True)
                
            if submit_button:
                # Validate all required fields based on selected report types
                required_fields = ["Reporter ID"]
                
                # Add common required fields
                required_fields.extend(["Flaw Description", "Policy Violation", "Impacts", "Impacted Stakeholder(s)"])
                
                # Add type-specific required fields
                if "Real-World Events" in report_types:
                    required_fields.extend([
                        "Description of the Incident(s)", "Implicated Systems", "Event Location(s)",
                        "Experienced Harm Types", "Harm Narrative"
                    ])
                
                if "Malign Actor" in report_types:
                    required_fields.extend(["Tactic Select", "Impact"])
                
                if "Security Incident Report" in report_types:
                    required_fields.append("Detection")
                
                if "Vulnerability Report" in report_types:
                    required_fields.append("Proof-of-Concept Exploit")
                
                if "Hazard Report" in report_types:
                    required_fields.extend(["Examples", "Replication Packet", "Statistical Argument"])
                
                # Combine all data for validation
                all_data = {**st.session_state.common_data, **st.session_state.form_data}
                
                # Validate
                missing_fields = validate_required_fields(all_data, required_fields)
                
                if missing_fields:
                    st.error(f"Please fill out the following required fields: {', '.join(missing_fields)}")
                else:
                    # Save uploaded files
                    if st.session_state.uploaded_files:
                        file_paths = save_uploaded_files(st.session_state.uploaded_files)
                        st.session_state.form_data["Uploaded File Paths"] = file_paths
                    
                    handle_submission()
    
    # Display submission results if form was submitted
    if st.session_state.submission_status:
        show_report_submission_results(st.session_state.form_data)

if __name__ == "__main__":
    create_app()