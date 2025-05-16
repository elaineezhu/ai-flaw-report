from abc import ABC, abstractmethod
import streamlit as st
import os
import json
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
    """Provider that stores reports as local files"""
    
    def initialize(self):
        """Initialize local storage"""
        os.makedirs("reports", exist_ok=True)
        st.sidebar.success("Using local file storage.")
        return True
    
    def save_report(self, form_data):
        """Save report to a local file"""
        report_id = form_data.get("Report ID")
        machine_readable_output = generate_machine_readable_output(form_data)
        
        file_path = os.path.join("reports", f"report_{report_id}.json")
        with open(file_path, "w") as f:
            json.dump({
                "form_data": form_data,
                "machine_readable": machine_readable_output,
                "timestamp": datetime.now().isoformat()
            }, f, indent=4)
        
        return file_path, machine_readable_output
    
    def get_report(self, report_id):
        """Retrieve a report from local storage"""
        file_path = os.path.join("reports", f"report_{report_id}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        return data
    
    def update_report(self, report_id, form_data):
        """Update an existing report in local storage"""
        # For local storage, this is the same as saving a new report
        self.save_report(form_data)
        return True
    
    def list_reports(self, limit=100):
        """List all reports in local storage"""
        reports = []
        report_dir = "reports"
        
        if not os.path.exists(report_dir):
            return reports
        
        # Get all JSON files in the reports directory
        report_files = [f for f in os.listdir(report_dir) if f.endswith(".json")]
        
        # Sort by most recent first
        report_files.sort(key=lambda f: os.path.getmtime(os.path.join(report_dir, f)), reverse=True)
        
        # Limit the number of files
        report_files = report_files[:limit]
        
        for file_name in report_files:
            try:
                with open(os.path.join(report_dir, file_name), "r") as f:
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
                st.error(f"Error reading report file {file_name}: {e}")
        
        return reports

# Factory function to get the appropriate storage provider
def get_storage_provider():
    """Get the configured storage provider"""
    # Default is HF storage
    provider_name = os.environ.get("STORAGE_PROVIDER", "huggingface").lower()
    
    if provider_name == "local":
        return LocalStorageProvider()
    else:
        from storage.huggingface_storage import HuggingFaceStorageProvider
        return HuggingFaceStorageProvider()