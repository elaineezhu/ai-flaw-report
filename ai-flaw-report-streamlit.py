import streamlit as st
import json
from datetime import datetime
import uuid
import os
import psycopg2
from psycopg2.extras import Json
import constants

DB_CONFIG = {
    "dbname": "flaw_reports",
    "user": "USERNAME", # Replace with your own credentials
    "password": "PASSWORD",
    "host": "localhost",
    "port": "5432"
}

def reset_form():
    """Reset all session state variables to their initial values"""
    # Create a special key that will trigger a complete reset on the next run
    st.session_state['_needs_complete_reset'] = True
    
    # Generate a new report ID for the next session
    st.session_state['_new_report_id'] = str(uuid.uuid4())
    
    # Force a rerun to apply the reset
    st.rerun()

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
    
    # Initialize form reset flag
    if 'form_reset' not in st.session_state:
        st.session_state.form_reset = False

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
    """Combine all data and prepare for submission"""
    form_data = st.session_state.form_data.copy()
    
    # Ensure common data is merged in
    form_data.update(st.session_state.common_data)
    
    if "Report ID" not in form_data and "report_id" in st.session_state:
        form_data["Report ID"] = st.session_state.report_id
    
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
    st.segmented_control(
        "Does this flaw report involve a real-world incident, where some form of harm has already occurred?",
        options=["Yes", "No"],
        key="real_world_incident_radio",
        on_change=update_real_world_incident_radio
    )
    st.caption("(e.g., injury or harm to people, disruption to infrastructure, violations of laws or rights, or harm to property, or communities)")
    
    # Question 2: Threat actor - Using radio with empty initial option
    st.segmented_control(
        "Does this flaw report involve a threat actor (i.e. could be exploited with ill intent)?",
        options=["Yes", "No"],
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
    """Display submission results with fixed download functionality"""
    st.success("Report submitted successfully!")

    report_id = form_data.get("Report ID", st.session_state.get("report_id", "unknown"))
    
    form_data["Report ID"] = report_id
    
    machine_readable_output = generate_machine_readable_output(form_data)
    
    report_path = save_to_database(form_data, machine_readable_output)
    
    st.subheader("Download Your Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as JSON using the verified report_id
        json_str = json.dumps(form_data, indent=4)
        st.download_button(
            label="Download Report (JSON)",
            data=json_str,
            file_name=f"ai_flaw_report_{report_id}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Download as JSON-LD using the verified report_id
        json_ld_str = json.dumps(machine_readable_output, indent=4)
        st.download_button(
            label="Download Machine-Readable Report (JSON-LD)",
            data=json_ld_str,
            file_name=f"ai_flaw_report_{report_id}_jsonld.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    st.subheader("Recommended Report Recipients")
    
    recipients = determine_report_recipients(form_data)
    
    if not recipients:
        st.write("No specific recipients determined for this report.")
    else:
        grouped_recipients = {}
        for recipient in recipients:
            recipient_type = recipient.get("type", "Other")
            if recipient_type not in grouped_recipients:
                grouped_recipients[recipient_type] = []
            grouped_recipients[recipient_type].append(recipient)
        
        for recipient_type, recipients_list in grouped_recipients.items():
            st.write(f"**{recipient_type}s:**")
            for recipient in recipients_list:
                st.markdown(f"- [{recipient['name']}]({recipient['contact']})")
        
        if st.button("Send to All Recipients", type="primary"):
            st.success("STUB FOR SENDING TO ALL RECIPIENTS IN ACTUAL IMPLEMENTATION")

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
            
        with col2:
            if disclosure_intent == "Yes":
                disclosure_channels = st.multiselect(
                    "Disclosure channels",
                    options=["Academic paper", "Blog post", "Social media", "Media outlet", "Conference presentation", "Other"],
                    help="Where do you plan to disclose this issue?"
                )
                disclosure_channels_other = handle_other_option(disclosure_channels, disclosure_channels, 
                                                  "Please specify other disclosure channels:")
    
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
        "Disclosure Timeline": disclosure_timeline if disclosure_intent == "Yes" else None,
        "Disclosure Channels": disclosure_channels if disclosure_intent == "Yes" else [],
        "Disclosure_Channels_Other": disclosure_channels_other if disclosure_intent == "Yes" else "",
        "Embargo Request": embargo_request,
    }

def check_csam_harm_selected(harm_types):
    """Check if CSAM is selected as a harm type and show appropriate warning/guidance"""
    if "CSAM" in harm_types:
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
        
        # Force user to acknowledge before proceeding
        csam_acknowledge = st.checkbox("I acknowledge these guidelines and confirm this report does NOT contain illegal media")
        
        return csam_acknowledge
    return True

def generate_machine_readable_output(form_data):
    """Generate machine-readable JSON-LD output following Kevin's template"""
    json_ld = {
        "@context": "https://schema.org",
        "@type": "AIFlawReport",
        "reportId": form_data.get("Report ID"),
        "dateCreated": datetime.now().isoformat(),
        "reportStatus": form_data.get("Report Status"),
        "reportTypes": form_data.get("Report Types", []),
        "basicInformation": {
            "reporterId": form_data.get("Reporter ID"),
            "sessionId": form_data.get("Session ID"),
            "flawTimestampStart": form_data.get("Flaw Timestamp Start"),
            "flawTimestampEnd": form_data.get("Flaw Timestamp End"),
            "systems": form_data.get("Systems", [])
        },
        "commonFields": {
            "contextInfo": form_data.get("Context Info"),
            "flawDescription": form_data.get("Flaw Description"),
            "policyViolation": form_data.get("Policy Violation"),
            "severity": form_data.get("Severity"),
            "prevalence": form_data.get("Prevalence"),
            "impacts": form_data.get("Impacts", []),
            "impactedStakeholders": form_data.get("Impacted Stakeholder(s)", []),
            "riskSource": form_data.get("Risk Source", []),
            "bountyEligibility": form_data.get("Bounty Eligibility")
        },
        "disclosurePlan": {
            "disclosureIntent": form_data.get("Disclosure Intent"),
            "disclosureTimeline": form_data.get("Disclosure Timeline"),
            "disclosureChannels": form_data.get("Disclosure Channels", []),
            "embargoRequest": form_data.get("Embargo Request")
        }
    }
    
    # Report-type specific sections
    if "Real-World Events" in form_data.get("Report Types", []):
        json_ld["realWorldEvent"] = {
            "incidentDescription": form_data.get("Description of the Incident(s)"),
            "implicatedSystems": form_data.get("Implicated Systems"),
            "submitterRelationship": form_data.get("Submitter Relationship"),
            "eventDates": form_data.get("Event Date(s)"),
            "eventLocations": form_data.get("Event Location(s)"),
            "experiencedHarmTypes": form_data.get("Experienced Harm Types", []),
            "experiencedHarmSeverity": form_data.get("Experienced Harm Severity"),
            "harmNarrative": form_data.get("Harm Narrative")
        }
    
    if "Malign Actor" in form_data.get("Report Types", []):
        json_ld["malignActor"] = {
            "tactics": form_data.get("Tactic Select", []),
            "impact": form_data.get("Impact", [])
        }
    
    if "Security Incident Report" in form_data.get("Report Types", []):
        json_ld["securityIncident"] = {
            "threatActorIntent": form_data.get("Threat Actor Intent"),
            "detection": form_data.get("Detection", [])
        }
    
    if "Vulnerability Report" in form_data.get("Report Types", []):
        json_ld["vulnerability"] = {
            "proofOfConcept": form_data.get("Proof-of-Concept Exploit")
        }
    
    if "Hazard Report" in form_data.get("Report Types", []):
        json_ld["hazard"] = {
            "examples": form_data.get("Examples"),
            "replicationPacket": form_data.get("Replication Packet"),
            "statisticalArgument": form_data.get("Statistical Argument")
        }
    
    return json_ld

def create_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Database connection error: {e}")
        return None

def initialize_database():
    """Create necessary tables if they don't exist"""
    conn = create_db_connection()
    if conn is None:
        st.warning("Using local storage fallback since database connection failed.")
        return False
    
    try:
        with conn.cursor() as cur:
            # Create main reports table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flaw_reports (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(50) UNIQUE NOT NULL,
                    report_data JSONB NOT NULL,
                    machine_readable_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create recipients table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS report_recipients (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(50) REFERENCES flaw_reports(report_id),
                    recipient_name VARCHAR(255) NOT NULL,
                    recipient_type VARCHAR(50) NOT NULL,
                    recipient_contact TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create files table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS report_files (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(50) REFERENCES flaw_reports(report_id),
                    file_name VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            return True
    except psycopg2.Error as e:
        st.error(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def save_to_database(form_data, machine_readable_output):
    """Save report to PostgreSQL database"""
    conn = create_db_connection()
    report_id = form_data.get("Report ID")
    
    if conn is None:
        # Fallback to local file storage if database connection fails
        st.warning("Database connection failed. Saving to local file as fallback.")
        return save_to_local_file(form_data, machine_readable_output)
    
    try:
        with conn.cursor() as cur:
            # Insert main report
            cur.execute("""
                INSERT INTO flaw_reports (report_id, report_data, machine_readable_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (report_id) 
                DO UPDATE SET 
                    report_data = EXCLUDED.report_data,
                    machine_readable_data = EXCLUDED.machine_readable_data,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """, (
                report_id,
                Json(form_data),
                Json(machine_readable_output)
            ))
            
            report_db_id = cur.fetchone()[0]
            
            recipients = determine_report_recipients(form_data)
            if recipients:
                cur.execute("""
                    DELETE FROM report_recipients WHERE report_id = %s;
                """, (report_id,))
                
                # Insert new recipients
                for recipient in recipients:
                    cur.execute("""
                        INSERT INTO report_recipients 
                        (report_id, recipient_name, recipient_type, recipient_contact)
                        VALUES (%s, %s, %s, %s);
                    """, (
                        report_id,
                        recipient.get("name"),
                        recipient.get("type"),
                        recipient.get("contact")
                    ))
            
            if "Uploaded File Paths" in form_data:
                cur.execute("""
                    DELETE FROM report_files WHERE report_id = %s;
                """, (report_id,))
                
                # Insert new file records
                for file_path in form_data.get("Uploaded File Paths", []):
                    file_name = os.path.basename(file_path)
                    file_type = os.path.splitext(file_name)[1].lstrip('.')
                    
                    cur.execute("""
                        INSERT INTO report_files 
                        (report_id, file_name, file_path, file_type)
                        VALUES (%s, %s, %s, %s);
                    """, (
                        report_id,
                        file_name,
                        file_path,
                        file_type
                    ))
            
            conn.commit()
            return report_id
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        conn.rollback()
        # Fallback to local file storage
        return save_to_local_file(form_data, machine_readable_output)
    finally:
        conn.close()

def save_to_local_file(form_data, machine_readable_output):
    """Fallback function to save report to a local file"""
    report_id = form_data.get("Report ID")
    
    os.makedirs("reports", exist_ok=True)
    
    file_path = os.path.join("reports", f"report_{report_id}.json")
    with open(file_path, "w") as f:
        json.dump({
            "form_data": form_data,
            "machine_readable": machine_readable_output,
            "timestamp": datetime.now().isoformat()
        }, f, indent=4)
    
    return file_path

def get_report_from_database(report_id):
    """Retrieve a report from the database by its ID"""
    conn = create_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT report_data, machine_readable_data 
                FROM flaw_reports 
                WHERE report_id = %s;
            """, (report_id,))
            
            result = cur.fetchone()
            if not result:
                return None
                
            report_data, machine_readable_data = result
            return {
                "form_data": report_data,
                "machine_readable": machine_readable_data
            }
    except psycopg2.Error as e:
        st.error(f"Database error when retrieving report: {e}")
        return None
    finally:
        conn.close()

def get_report_recipients_from_database(report_id):
    """Retrieve recipients for a report from the database"""
    conn = create_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT recipient_name, recipient_type, recipient_contact, status
                FROM report_recipients 
                WHERE report_id = %s;
            """, (report_id,))
            
            recipients = []
            for row in cur.fetchall():
                recipients.append({
                    "name": row[0],
                    "type": row[1],
                    "contact": row[2],
                    "status": row[3]
                })
                
            return recipients
    except psycopg2.Error as e:
        st.error(f"Database error when retrieving recipients: {e}")
        return []
    finally:
        conn.close()

def update_recipient_status(report_id, recipient_name, status):
    """Update the status of a recipient for a report"""
    conn = create_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE report_recipients
                SET status = %s
                WHERE report_id = %s AND recipient_name = %s;
            """, (status, report_id, recipient_name))
            
            conn.commit()
            return True
    except psycopg2.Error as e:
        st.error(f"Database error when updating recipient status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
def determine_report_recipients(form_data):
    """Determine appropriate recipients for the report based on form data"""
    recipients = []
    
    systems = form_data.get("Systems", [])
    for system in systems:
        if "OpenAI" in system or "GPT" in system:
            recipients.append({
                "name": "OpenAI",
                "type": "Developer",
                "contact": "https://openai.com/security/vulnerability-reporting"
            })
        elif "Anthropic" in system or "Claude" in system:
            recipients.append({
                "name": "Anthropic", 
                "type": "Developer",
                "contact": "https://www.anthropic.com/security"
            })
        elif "Google" in system or "Gemini" in system or "Bard" in system:
            recipients.append({
                "name": "Google", 
                "type": "Developer",
                "contact": "https://bughunters.google.com/"
            })
        elif "Meta" in system or "Llama" in system:
            recipients.append({
                "name": "Meta", 
                "type": "Developer",
                "contact": "https://www.facebook.com/whitehat"
            })
    
    if "CSAM" in form_data.get("Experienced Harm Types", []):
        recipients.append({
            "name": "National Center for Missing & Exploited Children (NCMEC)",
            "type": "Authority",
            "contact": "https://report.cybertip.org/"
        })
        recipients.append({
            "name": "Internet Watch Foundation (IWF)",
            "type": "Authority",
            "contact": "https://report.iwf.org.uk/"
        })
    
    if form_data.get("Severity") in ["Critical", "High"]:
        if "Security Incident Report" in form_data.get("Report Types", []):
            recipients.append({
                "name": "CERT Coordination Center",
                "type": "Authority",
                "contact": "https://www.kb.cert.org/vuls/report/"
            })
            recipients.append({
                "name": "CISA",
                "type": "Authority",
                "contact": "https://www.cisa.gov/report"
            })
    
    if "Real-World Events" in form_data.get("Report Types", []):
        recipients.append({
            "name": "AI Incident Database",
            "type": "Database",
            "contact": "https://incidentdatabase.ai/submit"
        })
    
    return recipients

def display_report_recipients(recipients):
    """Display the recommended recipients for the report with correct pluralization"""
    st.subheader("Recommended Report Recipients")
    
    if not recipients:
        st.write("No specific recipients determined for this report.")
        return
    
    grouped_recipients = {}
    for recipient in recipients:
        recipient_type = recipient.get("type", "Other")
        if recipient_type not in grouped_recipients:
            grouped_recipients[recipient_type] = []
        grouped_recipients[recipient_type].append(recipient)
    
    for recipient_type, recipients_list in grouped_recipients.items():
        if recipient_type == "Authority":
            plural_type = "Authorities"
        elif recipient_type.endswith("y"):
            plural_type = f"{recipient_type[:-1]}ies"  
        elif recipient_type.endswith("s"):
            plural_type = f"{recipient_type}es"
        else:
            plural_type = f"{recipient_type}s"
            
        st.write(f"**{plural_type}:**")
        for recipient in recipients_list:
            st.markdown(f"- [{recipient['name']}]({recipient['contact']})")

def create_app():
    """Main function to create the Streamlit app with database integration"""
    st.set_page_config(page_title="AI Flaw Report Form", layout="wide")
    
    # Initialize database tables
    db_initialized = initialize_database()
    if not db_initialized:
        st.sidebar.warning("Using local storage mode. Database connection not available.")
    else:
        st.sidebar.success("Connected to PostgreSQL database.")
    
    # Handle the complete reset if needed
    if st.session_state.get('_needs_complete_reset', False):
        # Store the new report ID
        new_report_id = st.session_state.get('_new_report_id', str(uuid.uuid4()))
        
        # Clear ALL session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
        # Set the new report ID
        st.session_state.report_id = new_report_id
        
        # Initialize session state with fresh values
        initialize_session_state()
    else:
        # Normal initialization
        initialize_session_state()
    
    # Check if we need to rerun after reset
    if st.session_state.get('form_reset', False):
        st.session_state.form_reset = False
        st.rerun()
    
    # App title and description
    st.title("AI Flaw & Incident Report Form")
    
    st.markdown("""
    This form allows you to report flaws, vulnerabilities, or incidents related to AI systems. 
    The information you provide will help identify, categorize, and address potential issues.
    
    Please fill out the appropriate sections based on the type of report you're submitting.
    """)

    if st.button("Reset Form", type="secondary"):
        reset_form()
    
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
                
                # Check if CSAM is selected as a harm type
                csam_acknowledged = check_csam_harm_selected(real_world_fields.get("Experienced Harm Types", []))
            else:
                csam_acknowledged = True  # No Real-World Events section, so no CSAM check needed
            
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
            
            # Add public disclosure plan fields
            disclosure_plan = display_disclosure_plan()
            st.session_state.form_data.update(disclosure_plan)
            
            # Add "Report Types" to the form data
            st.session_state.form_data["Report Types"] = report_types
            
            # Add visual separation before submit button
            st.markdown("---")
            st.markdown(" ")  # Add extra space
            
            # Submit button with enhanced styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Only allow submission if CSAM acknowledgment is completed (if applicable)
                submit_button = st.button("Submit Report", type="primary", use_container_width=True, disabled=not csam_acknowledged)
                if not csam_acknowledged:
                    st.warning("You must acknowledge the CSAM reporting guidelines before submitting.")
                
                if st.button("Reset Form", type="secondary", use_container_width=True):
                    reset_form()
                
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
                
                # Add disclosure plan required field
                required_fields.append("Disclosure Intent")
                
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