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

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'report_id' not in st.session_state:
        st.session_state.report_id = str(uuid.uuid4())
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    if 'report_types' not in st.session_state:
        st.session_state.report_types = {
            "All Flaw Reports": False,
            "Real-World Events": False,
            "Malign Actor": False,
            "Security Incident Report": False, 
            "Vulnerability Report": False,
            "Hazard Report": False
        }

def update_report_types():
    """Update the report types based on user selection"""
    for report_type in st.session_state.report_types:
        st.session_state.report_types[report_type] = st.session_state.get(f"checkbox_{report_type}", False)

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
    if form_data.get("Report Type") and "Real-World Events" in form_data.get("Report Type"):
        recommendations.append("Affected Community Representatives")
        
    # Add security incident specific recommendations
    if form_data.get("Report Type") and "Security Incident Report" in form_data.get("Report Type"):
        recommendations.append("Computer Emergency Response Team (CERT)")
        
    return recommendations

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
    
    # Create form
    with st.form("ai_flaw_report_form"):
        # Common fields (apply to all flaws)
        st.subheader("Common Information")
        
        col1, col2 = st.columns(2)
        with col1:
            reporter_id = st.text_input("Reporter ID (anonymous or real identity)")
        with col2:
            st.text_input("Report ID", st.session_state.report_id, disabled=True)
        
        system_versions = st.multiselect("System Version(s)", options=SYSTEM_VERSIONS)
        report_status = st.selectbox("Report Status", options=REPORT_STATUS_OPTIONS)
        
        # Report Type Selection
        st.subheader("Report Type")
        st.markdown("Select all that apply:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.checkbox("All Flaw Reports", key="checkbox_All Flaw Reports", on_change=update_report_types)
            st.checkbox("Real-World Events", key="checkbox_Real-World Events", on_change=update_report_types)
        with col2:
            st.checkbox("Malign Actor", key="checkbox_Malign Actor", on_change=update_report_types)
            st.checkbox("Security Incident Report", key="checkbox_Security Incident Report", on_change=update_report_types)
        with col3:
            st.checkbox("Vulnerability Report", key="checkbox_Vulnerability Report", on_change=update_report_types)
            st.checkbox("Hazard Report", key="checkbox_Hazard Report", on_change=update_report_types)
        
        # Conditionally show fields based on report type
        
        # All Flaw Reports fields
        if st.session_state.report_types["All Flaw Reports"]:
            st.subheader("Flaw Report Details")
            
            session_id = st.text_input("Session ID")
            report_timestamp = st.date_input("Report Timestamp", datetime.now())
            flaw_timestamp = st.date_input("Flaw Timestamp(s)", datetime.now())
            
            context_info = st.text_area("Context Info (versions of other software/hardware involved)")
            flaw_description = st.text_area("Flaw Description (identification, reproduction, how it violates system policies)")
            policy_violation = st.text_area("Policy Violation (how expectations of the system are violated)")
            
            col1, col2 = st.columns(2)
            with col1:
                developer = st.text_input("Developer")
            with col2:
                system = st.text_input("System")
            
            severity = st.select_slider("Severity", options=SEVERITY_OPTIONS)
            prevalence = st.select_slider("Prevalence", options=PREVALENCE_OPTIONS)
            impacts = st.multiselect("Impacts", options=IMPACT_OPTIONS)
            impacted_stakeholders = st.multiselect("Impacted Stakeholder(s)", options=STAKEHOLDER_OPTIONS)
            risk_source = st.multiselect("Risk Source", options=RISK_SOURCE_OPTIONS)
            bounty_eligibility = st.radio("Bounty Eligibility", options=BOUNTY_OPTIONS)
        
        # Real-World Events fields
        if st.session_state.report_types["Real-World Events"]:
            st.subheader("Real-World Event Details")
            
            incident_description = st.text_area("Description of the Incident(s)")
            implicated_systems = st.text_area("Implicated Systems")
            
            submitter_relationship = st.selectbox("Submitter Relationship", 
                                               options=["Affected stakeholder", "Independent observer", "System developer", "Other"])
            
            event_dates = st.date_input("Event Date(s)", datetime.now())
            event_locations = st.text_input("Event Location(s)")
            
            experienced_harm_types = st.multiselect("Experienced Harm Types", options=HARM_TYPES)
            experienced_harm_severity = st.select_slider("Experienced Harm Severity", options=HARM_SEVERITY_OPTIONS)
            harm_narrative = st.text_area("Harm Narrative (justification of why the event constitutes harm)")
        
        # Malign Actor fields
        if st.session_state.report_types["Malign Actor"]:
            st.subheader("Malign Actor Details")
            
            tactic_select = st.multiselect("Tactic Select (e.g., from MITRE's ATLAS Matrix)", options=TACTIC_OPTIONS)
            impact = st.multiselect("Impact", options=IMPACT_TYPE_OPTIONS)
        
        # Security Incident Report fields
        if st.session_state.report_types["Security Incident Report"]:
            st.subheader("Security Incident Details")
            
            threat_actor_intent = st.radio("Threat Actor Intent", options=THREAT_ACTOR_INTENT_OPTIONS)
            detection = st.multiselect("Detection", options=DETECTION_METHODS)
        
        # Vulnerability Report fields
        if st.session_state.report_types["Vulnerability Report"]:
            st.subheader("Vulnerability Details")
            
            proof_of_concept = st.text_area("Proof-of-Concept Exploit")
        
        # Hazard Report fields
        if st.session_state.report_types["Hazard Report"]:
            st.subheader("Hazard Details")
            
            examples = st.text_area("Examples (list of system inputs/outputs)")
            replication_packet = st.text_area("Replication Packet (files evidencing the flaw)")
            statistical_argument = st.text_area("Statistical Argument (supporting evidence of a flaw)")
        
        # Submit button
        submitted = st.form_submit_button("Submit Report")
        
        if submitted:
            # Collect form data
            form_data = {
                "Report ID": st.session_state.report_id,
                "Reporter ID": reporter_id,
                "System Version(s)": system_versions,
                "Report Status": report_status,
                "Report Type": [k for k, v in st.session_state.report_types.items() if v],
                "Submission Timestamp": datetime.now().isoformat()
            }
            
            # Add conditional fields based on report type
            if st.session_state.report_types["All Flaw Reports"]:
                form_data.update({
                    "Session ID": session_id,
                    "Report Timestamp": report_timestamp.isoformat(),
                    "Flaw Timestamp(s)": flaw_timestamp.isoformat(),
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
                })
            
            if st.session_state.report_types["Real-World Events"]:
                form_data.update({
                    "Description of the Incident(s)": incident_description,
                    "Implicated Systems": implicated_systems,
                    "Submitter Relationship": submitter_relationship,
                    "Event Date(s)": event_dates.isoformat(),
                    "Event Location(s)": event_locations,
                    "Experienced Harm Types": experienced_harm_types,
                    "Experienced Harm Severity": experienced_harm_severity,
                    "Harm Narrative": harm_narrative
                })
            
            if st.session_state.report_types["Malign Actor"]:
                form_data.update({
                    "Tactic Select": tactic_select,
                    "Impact": impact
                })
            
            if st.session_state.report_types["Security Incident Report"]:
                form_data.update({
                    "Threat Actor Intent": threat_actor_intent,
                    "Detection": detection
                })
            
            if st.session_state.report_types["Vulnerability Report"]:
                form_data.update({
                    "Proof-of-Concept Exploit": proof_of_concept
                })
            
            if st.session_state.report_types["Hazard Report"]:
                form_data.update({
                    "Examples": examples,
                    "Replication Packet": replication_packet,
                    "Statistical Argument": statistical_argument
                })
            
            # Store form data in session state
            st.session_state.form_data = form_data
            
            # Generate recommendations
            recommendations = generate_recommendations(form_data)
            
            # Display JSON output and recommendations
            st.success("Report submitted successfully!")
            
            st.subheader("Form Data (JSON)")
            st.json(form_data)
            
            st.subheader("Recommended Recipients")
            for rec in recommendations:
                st.write(f"- {rec}")
            
            # Option to download the JSON
            json_str = json.dumps(form_data, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"ai_flaw_report_{st.session_state.report_id}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    create_app()