import streamlit as st
import uuid
from datetime import datetime
import os
import json

from form.form_entry import FormEntry, InputType
from form.report_type_logic import determine_report_types
from form import form_sections
from form.data.validation import validate_required_fields
from form.data.constants import *
from form.utils.file_handling import save_uploaded_files
from form.utils.recipients import determine_report_recipients
from storage.storage_interface import get_storage_provider
from form.utils.recipients import display_submission_table

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'report_id' not in st.session_state:
        st.session_state.report_id = str(uuid.uuid4())
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    if 'report_types' not in st.session_state:
        st.session_state.report_types = []
    
    if 'welcome_screen_acknowledged' not in st.session_state:
        st.session_state.welcome_screen_acknowledged = False
    
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

def display_welcome_screen():
    """Display welcome instructions as a popup-like screen that works in both light and dark mode"""
    st.markdown("# Instructions Before You Begin")
    
    with st.container():
        with st.expander("About This Form", expanded=True):
            st.markdown("""
            You are welcome to report any broadly-scoped flaw, vulnerability, or incident relating to an AI system or model. 
            We encourage reports with demonstrable risks, harms, or systematic concerns related to general-purpose AI systems.
            
            **This form will:**
            * Help you generate a comprehensive, machine-readable report, informed by security best practices.
            * Elicit details that will make it easier to review and triage.
            * Provide the option to automatically submit your report to a list of the venues relevant for your flaw.
            
            This form creates a form *for you*. Reports are handled in **strict confidence**, and **will not be saved or sent unless you choose to submit them**.
            
            Please feel free to contact us at _____ for questions or information.
            """)
        
        st.markdown("")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Continue to Form", type="primary", use_container_width=True):
                st.session_state.welcome_screen_acknowledged = True
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
    if "Child sexual-abuse material (CSAM)" in harm_types:
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
    st.sidebar.info(f"Report Types: {form_data.get('Report Types', [])}")
    
    if st.session_state.uploaded_files:
        file_names = [file.name for file in st.session_state.uploaded_files]
        form_data["Uploaded Files"] = file_names
    
    st.session_state.form_data = form_data
    st.session_state.submission_status = True

def show_report_submission_results(form_data):
    """Redesigned to separate Created vs Submitted states"""
    st.success("Report successfully created!")

    report_id = form_data.get("Report ID", st.session_state.get("report_id", "unknown"))
    form_data["Report ID"] = report_id
    
    st.info(f"Here is the Report ID you can save for your reference in the future: **{report_id}**")
    
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
    
    st.subheader("Your Report Has Been Created")
    st.write("Your report has been saved and is available for download in the following formats:")
    
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
    
    st.subheader("Submit Your Report")
    st.write("You can automatically submit your report to the following recommended recipients:")
    
    recipients = determine_report_recipients(form_data)
    
    display_submission_table(recipients)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if len(recipients) > 0 and st.button("Submit to Selected Recipients", type="primary", use_container_width=True):
            selected_recipients = []
            for recipient in recipients:
                safe_key = f"submit_to_{recipient.name.replace(' ', '_').replace('(', '').replace(')', '')}"
                if st.session_state.get(safe_key, True):
                    selected_recipients.append(recipient)
            
            db_selected = st.session_state.get("submit_to_database", True)
            
            if selected_recipients or db_selected:
                total_submissions = len(selected_recipients) + (1 if db_selected else 0)
                st.success(f"Report submitted to {total_submissions} recipient(s)")
                
                st.write("**Submitted to:**")
                if db_selected:
                    st.write("- AI Flaw Report Database")
                for recipient in selected_recipients:
                    st.write(f"- {recipient.name}")
                    
                # FOR FUTURE IMPL: Call recipient.submit(form_data) for each recipient
            else:
                st.warning("No recipients were selected. Please select at least one recipient or download the report manually.")

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
    uploaded_files = st.file_uploader("Upload Relevant Files: Any files that pertain to the reproducibility or documentation of the flaw. Please title them and refer to them in descriptions.", accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.write(f"{len(uploaded_files)} file(s) uploaded")

def display_report_type_classification():
    """Display report type classification questions"""
    st.subheader("Report Classification")
    st.markdown("Please answer the following questions to determine the appropriate report type:")

    # Question 1
    real_world_incident_field = FormEntry(
        name="real_world_incident_radio",
        title="Does this flaw report involve a real-world incident, where some form of harm has already occurred?",
        input_type=InputType.SEGMENTED_CONTROL,
        options=["Yes", "No"],
        help_text="(e.g., injury or harm to people, disruption to infrastructure, violations of laws or rights, or harm to property, or communities)",
        extra_params={"key": "real_world_incident_radio", "on_change": update_real_world_incident_radio}
    )
    real_world_incident_field.to_streamlit()
    
    # Question 2
    threat_actor_field = FormEntry(
        name="threat_actor_radio",
        title="Does this flaw report involve a threat actor (i.e. could be exploited with ill intent)?",
        input_type=InputType.SEGMENTED_CONTROL,
        options=["Yes", "No"],
        extra_params={"key": "threat_actor_radio", "on_change": update_threat_actor_radio}
    )
    threat_actor_field.to_streamlit()

def create_app():
    """Main function to create the Streamlit app with database integration"""
    st.set_page_config(page_title="AI Flaw Report Form", layout="wide")

    initialize_session_state()

    if not st.session_state.welcome_screen_acknowledged:
        display_welcome_screen()
        return 
    
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
    
    
    st.title("AI Flaw & Incident Report Form")
    
    st.markdown("""
    This form allows you to report flaws, vulnerabilities, or incidents related to AI systems. 
    The information you provide will help identify, categorize, and address potential issues.
    
    Please fill out the appropriate sections based on the type of report you're submitting.
    """)
    
    basic_info = form_sections.display_basic_information()
    common_fields = form_sections.display_common_fields()
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
            if "Real-World Incidents" in report_types:
                real_world_fields = form_sections.display_real_world_event_fields()
                st.session_state.form_data.update(real_world_fields)
                
                csam_acknowledged = check_csam_harm_selected(real_world_fields.get("Experienced Harm Types", []))
            else:
                csam_acknowledged = True
            
            # Malign Actor fields
            if "Malign Actor" in report_types:
                malign_actor_fields = form_sections.display_malign_actor_fields()
                st.session_state.form_data.update(malign_actor_fields)
            
            # Security Incident Report fields
            if "Security Incident Report" in report_types:
                security_incident_fields = form_sections.display_security_incident_fields()
                st.session_state.form_data.update(security_incident_fields)
            
            # Vulnerability Report fields
            if "Vulnerability Report" in report_types:
                vulnerability_fields = form_sections.display_vulnerability_fields()
                st.session_state.form_data.update(vulnerability_fields)
            
            # Hazard Report fields
            if "Hazard Report" in report_types:
                hazard_fields = form_sections.display_hazard_fields()
                st.session_state.form_data.update(hazard_fields)
            
            # Add public disclosure plan fields
            disclosure_plan = form_sections.display_disclosure_plan()
            st.session_state.form_data.update(disclosure_plan)
            
            st.session_state.form_data["Report Types"] = report_types
            
            st.markdown("---")
            st.markdown(" ")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.button("Submit Report", type="primary", use_container_width=True, disabled=not csam_acknowledged)
                if not csam_acknowledged:
                    st.warning("You must acknowledge the CSAM reporting guidelines before submitting.")
                
            if submit_button:
                required_fields = []
                
                required_fields.extend(["Flaw Description", "Policy Violation", "Impacts", "Impacted Stakeholder(s)"])
                
                # Add type-specific required fields
                if "Real-World Incidents" in report_types:
                    required_fields.extend([
                        "Description of the Incident(s)", "Implicated Systems", "Incident Location(s)",
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