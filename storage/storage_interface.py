from abc import ABC, abstractmethod
import streamlit as st
import os
import json
import tempfile
from datetime import datetime
from form.data.schema import generate_machine_readable_output

class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    def initialize(self):
        """Initialize the storage provider"""
        pass
    
    @abstractmethod
    def save_report(self, form_data):
        """
        Save a report to storage
        
        Args:
            form_data (dict): The form data to save
            
        Returns:
            tuple: (report_path, machine_readable_output)
        """
        pass
    
    @abstractmethod
    def get_report(self, report_id):
        """
        Retrieve a report from storage
        
        Args:
            report_id (str): The ID of the report to retrieve
            
        Returns:
            dict: The retrieved report data or None if not found
        """
        pass
    
    @abstractmethod
    def update_report(self, report_id, form_data):
        """
        Update an existing report
        
        Args:
            report_id (str): The ID of the report to update
            form_data (dict): The updated form data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        pass

class LocalStorageProvider(StorageProvider):
    """Provider that stores reports as local files in a temporary directory"""
    
    def __init__(self):
        """Initialize with a temp directory that's writable"""
        self.report_dir = os.path.join(tempfile.gettempdir(), "ai_flaw_reports")
        self.initialized = False
    
    def initialize(self):
        """Initialize local storage using a temporary directory"""
        try:
            os.makedirs(self.report_dir, exist_ok=True)
            st.sidebar.success(f"Using local file storage in temporary directory: {self.report_dir}")
            self.initialized = True
            return True
        except Exception as e:
            st.sidebar.error(f"Error initializing local storage: {str(e)}")
            return False
    
    def save_report(self, form_data):
        """Save report to a local file in the temp directory"""
        if not self.initialized:
            self.initialize()
            
        report_id = form_data.get("Report ID")
        machine_readable_output = generate_machine_readable_output(form_data)
        
        file_path = os.path.join(self.report_dir, f"report_{report_id}.json")
        try:
            with open(file_path, "w") as f:
                json.dump({
                    "form_data": form_data,
                    "machine_readable": machine_readable_output,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=4)
            
            st.sidebar.success(f"Report saved to: {file_path}")
            return file_path, machine_readable_output
        except Exception as e:
            st.sidebar.error(f"Error saving report: {str(e)}")
            st.session_state[f"report_{report_id}"] = {
                "form_data": form_data,
                "machine_readable": machine_readable_output,
                "timestamp": datetime.now().isoformat()
            }
            st.sidebar.info(f"Fallback: Report stored in session state")
            return f"session_state:report_{report_id}", machine_readable_output
    
    def get_report(self, report_id):
        """Retrieve a report from local storage or session state fallback"""
        if not self.initialized:
            self.initialize()
            
        session_key = f"report_{report_id}"
        if session_key in st.session_state:
            st.sidebar.info(f"Retrieved report {report_id} from session state")
            return st.session_state[session_key]
        
        file_path = os.path.join(self.report_dir, f"report_{report_id}.json")
        if not os.path.exists(file_path):
            st.sidebar.warning(f"Report {report_id} not found")
            return None
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            st.sidebar.success(f"Retrieved report from: {file_path}")
            return data
        except Exception as e:
            st.sidebar.error(f"Error reading report file: {str(e)}")
            return None
    
    def update_report(self, report_id, form_data):
        """Update an existing report in local storage"""
        self.save_report(form_data)
        return True
    
    def list_reports(self, limit=100):
        """List all reports in local storage and session state"""
        if not self.initialized:
            self.initialize()
            
        reports = []
        
        if os.path.exists(self.report_dir):
            try:
                report_files = [f for f in os.listdir(self.report_dir) if f.endswith(".json")]
                
                # Sort by most recent first
                try:
                    report_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.report_dir, f)), reverse=True)
                except:
                    pass
                
                report_files = report_files[:limit]
                
                for file_name in report_files:
                    try:
                        with open(os.path.join(self.report_dir, file_name), "r") as f:
                            data = json.load(f)
                        
                        # Extract report ID from filename (report_ID.json)
                        report_id = file_name.replace("report_", "").replace(".json", "")
                        
                        form_data = data.get("form_data", {})
                        
                        reports.append({
                            "report_id": report_id,
                            "report_status": form_data.get("Report Status", "Unknown"),
                            "report_types": form_data.get("Report Types", []),
                            "reporter_id": form_data.get("Reporter ID", "Unknown"),
                            "submission_timestamp": data.get("timestamp", "Unknown")
                        })
                    except Exception as e:
                        st.sidebar.error(f"Error reading report file {file_name}: {e}")
            except Exception as e:
                st.sidebar.error(f"Error listing reports from directory: {str(e)}")
        
        for key in st.session_state:
            if key.startswith("report_"):
                try:
                    report_id = key.replace("report_", "")
                    if any(r["report_id"] == report_id for r in reports):
                        continue 
                        
                    data = st.session_state[key]
                    form_data = data.get("form_data", {})
                    
                    reports.append({
                        "report_id": report_id,
                        "report_status": form_data.get("Report Status", "Unknown"),
                        "report_types": form_data.get("Report Types", []),
                        "reporter_id": form_data.get("Reporter ID", "Unknown"),
                        "submission_timestamp": data.get("timestamp", "Unknown")
                    })
                except Exception as e:
                    st.sidebar.error(f"Error processing session state report {key}: {str(e)}")
        
        return reports[:limit]

def get_storage_provider():
    """Get the configured storage provider"""
    provider_name = os.environ.get("STORAGE_PROVIDER", "huggingface").lower()
    
    if provider_name == "local":
        return LocalStorageProvider()
    else:
        from storage.huggingface_storage import HuggingFaceStorageProvider
        return HuggingFaceStorageProvider()