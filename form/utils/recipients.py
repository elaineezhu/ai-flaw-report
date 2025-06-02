import streamlit as st
class ReportRecipient:
    """Class representing a recipient of a flaw report"""
    
    def __init__(self, name, recipient_type, contact, reason=None, status="pending"):
        """
        Initialize a report recipient
        
        Args:
            name (str): Name of the recipient (e.g., "OpenAI", "NCMEC")
            recipient_type (str): Type of recipient (e.g., "Developer", "Authority")
            contact (str): Contact information or URL
            reason (str, optional): Reason why this recipient is suggested
            status (str): Status of sending to this recipient (default: "pending")
        """
        self.name = name
        self.recipient_type = recipient_type
        self.contact = contact
        self.reason = reason
        self.status = status
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "type": self.recipient_type,
            "contact": self.contact,
            "reason": self.reason,
            "status": self.status
        }
    
    def submit(self, report_data):
        """
        Submit the report to this recipient
        
        Args:
            report_data (dict): The report data to submit
            
        Returns:
            bool: True if submission was successful, False otherwise
        """
        # This is a stub that would be implemented with actual submission logic
        # For now, just return True to indicate success
        return True
    
    @classmethod
    def from_dict(cls, data):
        """Create a ReportRecipient instance from a dictionary"""
        return cls(
            name=data.get("name"),
            recipient_type=data.get("type"),
            contact=data.get("contact"),
            status=data.get("status", "pending")
        )

def determine_report_recipients(form_data):
    """Determine appropriate recipients for the report based on form data"""
    recipients = []
    seen_recipients = set()
    
    systems = form_data.get("Implicated Systems", form_data.get("Systems", []))
    
    for system in systems:
        recipient_info = None
        
        if "OpenAI" in system or "GPT" in system:
            recipient_info = ("OpenAI", "Developer", "https://openai.com/security/vulnerability-reporting")
        elif "Anthropic" in system or "Claude" in system:
            recipient_info = ("Anthropic", "Developer", "https://www.anthropic.com/security")
        elif "Google" in system or "Gemini" in system or "Bard" in system:
            recipient_info = ("Google", "Developer", "https://bughunters.google.com/")
        elif "Meta" in system or "Llama" in system:
            recipient_info = ("Meta", "Developer", "https://www.facebook.com/whitehat")
        
        if recipient_info and recipient_info not in seen_recipients:
            name, recipient_type, contact = recipient_info
            recipients.append(ReportRecipient(
                name=name,
                recipient_type=recipient_type,
                contact=contact,
                reason="This AI developer was selected as an affected system"
            ))
            seen_recipients.add(recipient_info)
    
    if "Child sexual-abuse material (CSAM)" in form_data.get("Experienced Harm Types", []):
        recipients.append(ReportRecipient(
            name="National Center for Missing & Exploited Children (NCMEC)",
            recipient_type="Authority",
            contact="https://report.cybertip.org/",
            reason="This authority should be notified for incidents involving CSAM"
        ))
        recipients.append(ReportRecipient(
            name="Internet Watch Foundation (IWF)",
            recipient_type="Authority",
            contact="https://report.iwf.org.uk/",
            reason="This international authority handles reports of CSAM"
        ))
    
    if form_data.get("Severity") in ["Critical", "High"]:
        if "Security Incident Report" in form_data.get("Report Types", []):
            recipients.append(ReportRecipient(
                name="CERT Coordination Center",
                recipient_type="Authority",
                contact="https://www.kb.cert.org/vuls/report/",
                reason="This authority should be notified of high-severity security incidents"
            ))
            recipients.append(ReportRecipient(
                name="CISA",
                recipient_type="Authority",
                contact="https://www.cisa.gov/report",
                reason="U.S. Cybersecurity & Infrastructure Security Agency handles critical security incidents"
            ))
    
    if "Real-World Incidents" in form_data.get("Report Types", []):
        recipients.append(ReportRecipient(
            name="AI Incident Database",
            recipient_type="Database",
            contact="https://incidentdatabase.ai/submit",
            reason="This database catalogs real-world AI incidents for research purposes"
        ))
    
    return recipients

def display_submission_table(recipients):
    """Display submission options in a table format with checkboxes"""
    if not recipients:
        st.write("No specific recipients determined for this report.")
        return
    
    st.write("### Submit to Report Database")
    
    db_checkbox_key = "submit_to_database"
    if db_checkbox_key not in st.session_state:
        st.session_state[db_checkbox_key] = True
    
    st.checkbox(
        "Submit to AI Flaw Report Database (Recommended)", 
        value=st.session_state[db_checkbox_key],
        key=db_checkbox_key,
        help="Your report will be stored in our database for research and monitoring purposes"
    )
    
    if len(recipients) > 0:
        st.write("### External Recipients")
        
        cols = st.columns([3, 3, 6, 1])
        cols[0].write("**Submit To**")
        cols[1].write("**Contact**")
        cols[2].write("**Reason**")
        cols[3].write("**Select**")
        
        st.markdown("---")
        
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
            
            for i, recipient in enumerate(recipients_list):
                # Create unique key by including index and recipient type
                checkbox_key = f"submit_to_{recipient.name.replace(' ', '_').replace('(', '').replace(')', '')}_{recipient_type}_{i}"
                
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True
                
                cols = st.columns([3, 3, 6, 1])
                
                if recipient.contact.startswith(("http://", "https://")):
                    cols[0].markdown(f"[{recipient.name}]({recipient.contact})")
                else:
                    cols[0].write(recipient.name)
                
                contact_display = recipient.contact
                if contact_display.startswith(("http://", "https://")):
                    contact_display = f"[Submission Form]({recipient.contact})"
                elif "@" in contact_display:
                    contact_display = f"[{contact_display}](mailto:{contact_display})"
                cols[1].markdown(contact_display)
                
                cols[2].write(recipient.reason if hasattr(recipient, 'reason') and recipient.reason else "Relevant to your report type")
                
                cols[3].checkbox("", value=st.session_state[checkbox_key], key=checkbox_key)
                
            st.markdown("---")