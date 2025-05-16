import streamlit as st
import uuid
from datetime import datetime

from form.report_type_logic import determine_report_types
from form.data.validation import validate_required_fields
from form.data.constants import *
from form.utils.file_handling import save_uploaded_files
from form.utils.recipients import determine_report_recipients
from storage.storage_interface import get_storage_provider

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
    
    if 'involves_real_world_incident' not in st.session_state:
        st.session_state.involves_real_world_incident = None
    
    if 'involves_threat_actor' not in st.session_state:
        st.session_state.involves_threat_actor = None
        
    if 'real_world_incident_radio' not in st.session_state:
        st.session_state.real_world_incident_radio = None
        
    if 'threat_actor_radio' not in st.session_state:
        st.session_state.threat_actor_radio = None
    
    if 'form_reset' not in st.session_state:
        st.session_state.form_reset = False

def reset_form():
    """Reset all session state variables to their initial values"""
    st.session_state['_needs_complete_reset'] = True
    
    st.session_state['_new_report_id'] = str(uuid.uuid4())
    
    st.rerun()

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

def handle_submission():
    """Combine all data and prepare for submission"""
    form_data = st.session_state.form_data.copy()
    
    form_data.update(st.session_state.common_data)
    
    if "Report ID" not in form_data and "report_id" in st.session_state:
        form_data["Report ID"] = st.session_state.report_id
    
    form_data["Submission Timestamp"] = datetime.now().isoformat()
    
    # DEBUGGING INFO (Will delete later)
    st.sidebar.info(f"Submitting form with Report ID: {form_data.get('Report ID')}")
    st.sidebar.info(f"Report Status: {form_data.get('Report Status')}")
    st.sidebar.info(f"Report Types: {form_data.get('Report Types', [])}")
    
    if st.session_state.uploaded_files:
        file_names = [file.name for file in st.session_state.uploaded_files]
        form_data["Uploaded Files"] = file_names
    
    st.session_state.form_data = form_data
    st.session_state.submission_status = True

def show_report_submission_results(form_data):
    """Display submission results with fixed download functionality"""
    st.success("Report submitted successfully!")

    report_id = form_data.get("Report ID", st.session_state.get("report_id", "unknown"))
    form_data["Report ID"] = report_id
    
    storage_provider = get_storage_provider()
    
    # Make sure the provider is initialized before saving
    if not hasattr(storage_provider, 'initialized') or not storage_provider.initialized:
        st.sidebar.warning("Storage provider not initialized. Re-initializing...")
        initialized = storage_provider.initialize()
        if initialized:
            st.sidebar.success("Successfully re-initialized storage provider.")
        else:
            st.sidebar.error("Failed to initialize storage provider. Using local fallback.")
    
    report_path, machine_readable_output = storage_provider.save_report(form_data)
    
    st.subheader("Download Your Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as JSON using the verified report_id
        import json
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
    display_report_recipients(recipients)
    
    if len(recipients) > 0 and st.button("Send to All Recipients", type="primary"):
        st.success("STUB FOR SENDING TO ALL RECIPIENTS IN ACTUAL IMPLEMENTATION")

def display_report_recipients(recipients):
    """Display the recommended recipients for the report with correct pluralization"""
    if not recipients:
        st.write("No specific recipients determined for this report.")
        return
    
    grouped_recipients = {}
    for recipient in recipients:
        recipient_type = recipient.recipient_type
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
            st.markdown(f"- [{recipient.name}]({recipient.contact})")

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

    # Question 1
    st.segmented_control(
        "Does this flaw report involve a real-world incident, where some form of harm has already occurred?",
        options=["Yes", "No"],
        key="real_world_incident_radio",
        on_change=update_real_world_incident_radio
    )
    st.caption("(e.g., injury or harm to people, disruption to infrastructure, violations of laws or rights, or harm to property, or communities)")
    
    # Question 2
    st.segmented_control(
        "Does this flaw report involve a threat actor (i.e. could be exploited with ill intent)?",
        options=["Yes", "No"],
        key="threat_actor_radio",
        on_change=update_threat_actor_radio
    )

def create_app():
    """Main function to create the Streamlit app with database integration"""
    st.set_page_config(page_title="AI Flaw Report Form", layout="wide")
    
    storage_provider = get_storage_provider()
    initialized = storage_provider.initialize()
    
    if initialized:
        st.sidebar.success(f"Connected to storage provider: {storage_provider.__class__.__name__}")
    else:
        st.sidebar.warning("Failed to initialize storage provider. Using local storage fallback.")
        from storage.storage_interface import LocalStorageProvider
        storage_provider = LocalStorageProvider()
        storage_provider.initialize()
    
    # Store the provider in session state so it persists between reruns
    st.session_state['storage_provider'] = storage_provider
    
    if st.session_state.get('_needs_complete_reset', False):
        new_report_id = st.session_state.get('_new_report_id', str(uuid.uuid4()))
        
        current_provider = st.session_state.get('storage_provider')
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
        st.session_state.report_id = new_report_id
        
        st.session_state['storage_provider'] = current_provider
        
        initialize_session_state()
    else:
        initialize_session_state()
    
    if st.session_state.get('form_reset', False):
        st.session_state.form_reset = False
        st.rerun()
    
    st.title("AI Flaw & Incident Report Form")
    
    st.markdown("""
    This form allows you to report flaws, vulnerabilities, or incidents related to AI systems. 
    The information you provide will help identify, categorize, and address potential issues.
    
    Please fill out the appropriate sections based on the type of report you're submitting.
    """)

    if st.button("Reset Form", type="secondary"):
        reset_form()
    
    from form.form_sections import (
        display_basic_information, 
        display_common_fields,
        display_real_world_event_fields,
        display_malign_actor_fields,
        display_security_incident_fields,
        display_vulnerability_fields,
        display_hazard_fields,
        display_disclosure_plan
    )
    
    basic_info = display_basic_information()
    common_fields = display_common_fields()
    display_file_upload()
    
    st.session_state.common_data = {**basic_info, **common_fields}
    
    display_report_type_classification()
    
    report_types = determine_report_types(
        st.session_state.involves_real_world_incident, 
        st.session_state.involves_threat_actor
    )
    
    if st.session_state.involves_real_world_incident is not None and st.session_state.involves_threat_actor is not None:
        st.subheader("Selected Report Types")
        st.write(", ".join(report_types))
        
        st.session_state.report_types = report_types
        
        if report_types:
            st.session_state.form_data = {} 
            
            # Real-World Events fields
            if "Real-World Events" in report_types:
                real_world_fields = display_real_world_event_fields()
                st.session_state.form_data.update(real_world_fields)
                
                csam_acknowledged = check_csam_harm_selected(real_world_fields.get("Experienced Harm Types", []))
            else:
                csam_acknowledged = True # No Real-World Events section, so no CSAM check needed
            
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
            
            st.session_state.form_data["Report Types"] = report_types
            
            st.markdown("---")
            st.markdown(" ")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.button("Submit Report", type="primary", use_container_width=True, disabled=not csam_acknowledged)
                if not csam_acknowledged:
                    st.warning("You must acknowledge the CSAM reporting guidelines before submitting.")
                
                if st.button("Reset Form", type="secondary", use_container_width=True):
                    reset_form()
                
            if submit_button:
                required_fields = ["Reporter ID"]
                
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
                
                missing_fields = validate_required_fields(all_data, required_fields)
                
                if missing_fields:
                    st.error(f"Please fill out the following required fields: {', '.join(missing_fields)}")
                else:
                    if st.session_state.uploaded_files:
                        st.sidebar.info(f"Processing {len(st.session_state.uploaded_files)} uploaded files")
                        file_paths = save_uploaded_files(st.session_state.uploaded_files, report_id=all_data.get("Report ID"))
                        st.session_state.form_data["Uploaded Files"] = list(file_paths.keys()) 
                        st.session_state.form_data["Uploaded File Paths"] = list(file_paths.values())
                        
                        # DEBUGGING INFO (Will delete later)
                        st.sidebar.success(f"Saved {len(file_paths)} files locally")
                        st.sidebar.info(f"Uploaded files: {st.session_state.form_data['Uploaded Files']}")
                        st.sidebar.info(f"File paths: {st.session_state.form_data['Uploaded File Paths']}")
                    else:
                        st.sidebar.info("No files uploaded")
                    
                    handle_submission()
    
    if st.session_state.submission_status:
        show_report_submission_results(st.session_state.form_data)