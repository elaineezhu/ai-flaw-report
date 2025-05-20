class ReportRecipient:
    """Class representing a recipient of a flaw report"""
    
    def __init__(self, name, recipient_type, contact, status="pending"):
        """
        Initialize a report recipient
        
        Args:
            name (str): Name of the recipient (e.g., "OpenAI", "NCMEC")
            recipient_type (str): Type of recipient (e.g., "Developer", "Authority")
            contact (str): Contact information or URL
            status (str): Status of sending to this recipient (default: "pending")
        """
        self.name = name
        self.recipient_type = recipient_type
        self.contact = contact
        self.status = status
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "type": self.recipient_type,
            "contact": self.contact,
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
    
    systems = form_data.get("Systems", [])
    for system in systems:
        if "OpenAI" in system or "GPT" in system:
            recipients.append(ReportRecipient(
                name="OpenAI",
                recipient_type="Developer",
                contact="https://openai.com/security/vulnerability-reporting"
            ))
        elif "Anthropic" in system or "Claude" in system:
            recipients.append(ReportRecipient(
                name="Anthropic", 
                recipient_type="Developer",
                contact="https://www.anthropic.com/security"
            ))
        elif "Google" in system or "Gemini" in system or "Bard" in system:
            recipients.append(ReportRecipient(
                name="Google", 
                recipient_type="Developer",
                contact="https://bughunters.google.com/"
            ))
        elif "Meta" in system or "Llama" in system:
            recipients.append(ReportRecipient(
                name="Meta", 
                recipient_type="Developer",
                contact="https://www.facebook.com/whitehat"
            ))
    
    if "CSAM" in form_data.get("Experienced Harm Types", []):
        recipients.append(ReportRecipient(
            name="National Center for Missing & Exploited Children (NCMEC)",
            recipient_type="Authority",
            contact="https://report.cybertip.org/"
        ))
        recipients.append(ReportRecipient(
            name="Internet Watch Foundation (IWF)",
            recipient_type="Authority",
            contact="https://report.iwf.org.uk/"
        ))
    
    if form_data.get("Severity") in ["Critical", "High"]:
        if "Security Incident Report" in form_data.get("Report Types", []):
            recipients.append(ReportRecipient(
                name="CERT Coordination Center",
                recipient_type="Authority",
                contact="https://www.kb.cert.org/vuls/report/"
            ))
            recipients.append(ReportRecipient(
                name="CISA",
                recipient_type="Authority",
                contact="https://www.cisa.gov/report"
            ))
    
    if "Real-World Events" in form_data.get("Report Types", []):
        recipients.append(ReportRecipient(
            name="AI Incident Database",
            recipient_type="Database",
            contact="https://incidentdatabase.ai/submit"
        ))
    
    return recipients