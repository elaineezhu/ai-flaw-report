import streamlit as st
import json
from datetime import datetime
import uuid

# Configuration dictionaries for dropdown options
# These can be easily extended or modified
SYSTEM_VERSIONS = ["v1.0", "v1.1", "v2.0", "v3.0", "Other"]
REPORT_STATUS_OPTIONS = ["Submitted", "Under investigation", "Fixed", "Closed", "Rejected"]
SEVERITY_OPTIONS = ["Critical", "High", "Medium", "Low", "Negligible"]
PREVALENCE_OPTIONS = ["Widespread", "Common", "Occasional", "Rare", "Unknown"]
IMPACT_OPTIONS = ["Financial", "Psychological", "Physical", "Privacy", "Civil rights", "Environmental"]
STAKEHOLDER_OPTIONS = ["Users", "Developers", "Administrators", "General Public", "Vulnerable populations", "Organizations"]
RISK_SOURCE_OPTIONS = ["Design flaw", "Implementation error", "Data bias", "Deployment issue", "Integration problem"]
BOUNTY_OPTIONS = ["Yes", "No", "Not sure"]
HARM_TYPES = ["Physical", "Psychological", "Reputational", "Economic/property", "Environmental", "Public interest/critical infrastructure", "Fundamental rights", "Other"]
HARM_SEVERITY_OPTIONS = ["Catastrophic", "Critical", "Significant", "Moderate", "Minor"]
TACTIC_OPTIONS = ["Initial Access", "Execution", "Persistence", "Privilege Escalation", "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement", "Collection", "Command and Control", "Exfiltration", "Impact"]
IMPACT_TYPE_OPTIONS = ["Confidentiality breach", "Integrity violation", "Availability disruption", "Abuse of system"]
THREAT_ACTOR_INTENT_OPTIONS = ["Deliberate", "Unintentional", "Unknown"]
DETECTION_METHODS = ["User observation", "Monitoring", "Testing", "External report", "Automated analysis"]
REPORT_TYPES = ["All Flaw Reports", "Real-World Events", "Malign Actor", "Security Incident Report", "Vulnerability Report", "Hazard Report"]

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

def update_report_types():
    st.session_state.report_types = st.session_state.selected_report_types

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
    if "Financial" in form_data.get("Impacts", []):
        recommendations.append("Financial Oversight Bodies")
    
    if "Privacy" in form_data.get("Impacts", []) or "Confidentiality breach" in form_data.get("Impact", ""):
        recommendations.append("Data Protection Authority")
    
    if "Users" in form_data.get("Impacted Stakeholder(s)", []):
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
    
    # Store form data in session state
    st.session_state.form_data = form_data
    st.session_state.submission_status = True

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
    
    # Common information section (always required)
    st.subheader("Basic Information")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_id = st.text_input("Reporter ID (anonymous or real identity)", 
                                      help="Required field")
            
            st.text_input("Report ID", st.session_state.report_id, disabled=True)
            
            system_versions = st.multiselect("System Version(s)", options=SYSTEM_VERSIONS,
                                          help="Required field")
        
        with col2:
            report_status = st.selectbox("Report Status", options=REPORT_STATUS_OPTIONS)
            session_id = st.text_input("Session ID", help="Optional")
            report_timestamp = st.date_input("Report Timestamp", datetime.now())
    
    # Common fields for All Flaw Reports  
    st.subheader("Common Fields")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            flaw_timestamp = st.date_input("Flaw Timestamp(s)", datetime.now())
            context_info = st.text_area("Context Info (versions of other software/hardware involved)", 
                                     help="Optional")
        
        with col2:
            developer = st.text_input("Developer")
            system = st.text_input("System")
    
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
    with col2:
        impacted_stakeholders = st.multiselect("Impacted Stakeholder(s)", options=STAKEHOLDER_OPTIONS, 
                                             help="Required field")
    
    # Risk Source and Bounty Eligibility
    col1, col2 = st.columns(2)
    with col1:
        risk_source = st.multiselect("Risk Source", options=RISK_SOURCE_OPTIONS)
    with col2:
        bounty_eligibility = st.radio("Bounty Eligibility", options=BOUNTY_OPTIONS)
    
    # Store the common data
    st.session_state.common_data = {
        "Reporter ID": reporter_id,
        "Report ID": st.session_state.report_id,
        "System Version(s)": system_versions,
        "Report Status": report_status,
        "Session ID": session_id,
        "Report Timestamp": report_timestamp.isoformat() if report_timestamp else None,
        "Flaw Timestamp(s)": flaw_timestamp.isoformat() if flaw_timestamp else None,
        "Context Info": context_info,
        "Flaw Description": flaw_description,
        "Policy Violation": policy_violation,
        "Developer": developer,
        "System": system,
        "Severity": severity,
        "Prevalence": prevalence,
        "Impacts": impacts,
        "Impacted Stakeholder(s)": impacted_stakeholders,
        "Risk Source": risk_source,
        "Bounty Eligibility": bounty_eligibility
    }
    
    # Report Type Selection
    st.subheader("Report Type")
    st.markdown("Select all that apply:")
    
    selected_report_types = st.multiselect("Report Types", options=REPORT_TYPES,
                                         key="selected_report_types",
                                         help="Required: Select at least one report type")
    update_report_types()
    
    # Now show conditional fields based on selected report types
    if selected_report_types:
        st.session_state.form_data = {}  # Reset form data
        
        # Real-World Events fields
        if "Real-World Events" in selected_report_types:
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
                    event_dates = st.date_input("Event Date(s)", datetime.now())
                    event_locations = st.text_input("Event Location(s)", 
                                                 help="Required field")
            
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    experienced_harm_types = st.multiselect("Experienced Harm Types", options=HARM_TYPES, 
                                                          help="Required field")
                
                with col2:
                    experienced_harm_severity = st.select_slider("Experienced Harm Severity", options=HARM_SEVERITY_OPTIONS)
            
            harm_narrative = st.text_area("Harm Narrative (justification of why the event constitutes harm)", 
                                       help="Required field")
            
            # Update form data
            st.session_state.form_data.update({
                "Description of the Incident(s)": incident_description,
                "Implicated Systems": implicated_systems,
                "Submitter Relationship": submitter_relationship,
                "Event Date(s)": event_dates.isoformat() if event_dates else None,
                "Event Location(s)": event_locations,
                "Experienced Harm Types": experienced_harm_types,
                "Experienced Harm Severity": experienced_harm_severity,
                "Harm Narrative": harm_narrative
            })
        
        # Malign Actor fields
        if "Malign Actor" in selected_report_types:
            st.subheader("Malign Actor Details")
            
            col1, col2 = st.columns(2)
            with col1:
                tactic_select = st.multiselect("Tactic Select (e.g., from MITRE's ATLAS Matrix)", options=TACTIC_OPTIONS, 
                                             help="Required field")
            with col2:
                impact = st.multiselect("Impact", options=IMPACT_TYPE_OPTIONS, 
                                      help="Required field")
            
            # Update form data
            st.session_state.form_data.update({
                "Tactic Select": tactic_select,
                "Impact": impact
            })
        
        # Security Incident Report fields
        if "Security Incident Report" in selected_report_types:
            st.subheader("Security Incident Details")
            
            col1, col2 = st.columns(2)
            with col1:
                threat_actor_intent = st.radio("Threat Actor Intent", options=THREAT_ACTOR_INTENT_OPTIONS)
            with col2:
                detection = st.multiselect("Detection", options=DETECTION_METHODS, 
                                         help="Required field")
            
            # Update form data
            st.session_state.form_data.update({
                "Threat Actor Intent": threat_actor_intent,
                "Detection": detection
            })
        
        # Vulnerability Report fields
        if "Vulnerability Report" in selected_report_types:
            st.subheader("Vulnerability Details")
            
            proof_of_concept = st.text_area("Proof-of-Concept Exploit", 
                                         help="Required field")
            
            # Update form data
            st.session_state.form_data.update({
                "Proof-of-Concept Exploit": proof_of_concept
            })
        
        # Hazard Report fields
        if "Hazard Report" in selected_report_types:
            st.subheader("Hazard Details")
            
            examples = st.text_area("Examples (list of system inputs/outputs)", 
                                  help="Required field")
            
            replication_packet = st.text_area("Replication Packet (files evidencing the flaw)", 
                                           help="Required field")
            
            statistical_argument = st.text_area("Statistical Argument (supporting evidence of a flaw)", 
                                             help="Required field")
            
            # Update form data
            st.session_state.form_data.update({
                "Examples": examples,
                "Replication Packet": replication_packet,
                "Statistical Argument": statistical_argument
            })
        
        # Add "Report Types" to the form data
        st.session_state.form_data["Report Types"] = selected_report_types
        
        # Submit button - outside any form
        if st.button("Submit Report"):
            # Validate all required fields based on selected report types
            required_fields = ["Reporter ID", "System Version(s)", "Report Types"]
            
            # Add common required fields
            if "All Flaw Reports" in selected_report_types or len(selected_report_types) > 0:
                required_fields.extend(["Flaw Description", "Policy Violation", "Impacts", "Impacted Stakeholder(s)"])
            
            # Add type-specific required fields
            if "Real-World Events" in selected_report_types:
                required_fields.extend([
                    "Description of the Incident(s)", "Implicated Systems", "Event Location(s)",
                    "Experienced Harm Types", "Harm Narrative"
                ])
            
            if "Malign Actor" in selected_report_types:
                required_fields.extend(["Tactic Select", "Impact"])
            
            if "Security Incident Report" in selected_report_types:
                required_fields.append("Detection")
            
            if "Vulnerability Report" in selected_report_types:
                required_fields.append("Proof-of-Concept Exploit")
            
            if "Hazard Report" in selected_report_types:
                required_fields.extend(["Examples", "Replication Packet", "Statistical Argument"])
            
            # Combine all data for validation
            all_data = {**st.session_state.common_data, **st.session_state.form_data}
            
            # Validate
            missing_fields = validate_required_fields(all_data, required_fields)
            
            if missing_fields:
                st.error(f"Please fill out the following required fields: {', '.join(missing_fields)}")
            else:
                handle_submission()
    
    # Display submission results if form was submitted
    if st.session_state.submission_status:
        # Generate recommendations
        recommendations = generate_recommendations(st.session_state.form_data)
        
        # Display JSON output and recommendations
        st.success("Report submitted successfully!")
        
        st.subheader("Form Data (JSON)")
        st.json(st.session_state.form_data)
        
        st.subheader("Recommended Recipients")
        for rec in recommendations:
            st.write(f"- {rec}")
        
        # Download button - now outside any form
        json_str = json.dumps(st.session_state.form_data, indent=4)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"ai_flaw_report_{st.session_state.report_id}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    create_app()