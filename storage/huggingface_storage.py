import os
import json
import io
import tempfile
from datetime import datetime
import streamlit as st
import pandas as pd
from huggingface_hub import HfApi, create_repo, hf_hub_download, list_repo_files
from storage.storage_interface import StorageProvider

class HuggingFaceStorageProvider(StorageProvider):
    """
    A storage provider that works directly with Hugging Face Hub API
    (without using the datasets library or local caching)
    """
    
    def __init__(self, hf_token=None, repo_id=None):
        """Initialize the provider with token and repo_id"""
        self.hf_token = hf_token or self._get_token()
        self.repo_id = repo_id or self._get_repo_id()
        self.initialized = False
        self.api = None
        self.parquet_file = "reports.parquet"
    
    def _get_token(self):
        """Get HF token from environment variables, secrets, or a fallback method"""
        token = None
        
        token = os.getenv("HF_TOKEN")
        if token:
            # st.sidebar.success("Successfully loaded HF token from environment variable")
            return token
        
        for secret_name in ["hf_token", "HF_TOKEN", "Hf_Token"]:
                if secret_name in st.secrets:
                    token = st.secrets[secret_name]
                    # st.sidebar.success(f"Successfully loaded HF token from Streamlit secrets using key '{secret_name}'")
                    return token
            
        if os.getenv("SPACE_ID"):
            token = os.getenv("HF_TOKEN_READ")
            if token:
                # st.sidebar.success("Successfully loaded HF read token from Spaces environment")
                return token
        
        # If we got here, no token was found
        # st.sidebar.warning("No HF token found in any location")
        return token
    
    def _get_repo_id(self):
        """Get repo ID from environment variables, secrets, or construct from space name"""
        repo_id = None
        
        repo_id = os.getenv("HF_REPO_ID")
        if repo_id:
            # st.sidebar.success(f"Successfully loaded repo ID from environment variable: {repo_id}")
            return repo_id
        
        for secret_name in ["hf_repo_id", "HF_REPO_ID", "Hf_Repo_Id"]:
                if secret_name in st.secrets:
                    repo_id = st.secrets[secret_name]
                    # st.sidebar.success(f"Successfully loaded repo ID from Streamlit secrets using key '{secret_name}': {repo_id}")
                    return repo_id

            
        if os.getenv("SPACE_ID"):
            space_id = os.getenv("SPACE_ID")
            if space_id:
                username = space_id.split("/")[0]
                constructed_repo_id = f"{username}/ai-flaw-reports"
                # st.sidebar.info(f"Constructed repo ID from Space ID: {constructed_repo_id}")
                return constructed_repo_id
        
        # If we got here, no repo ID was found
        # st.sidebar.warning("No repo ID found in any location")
        return repo_id
    
    def initialize(self):
        """Initialize the Hugging Face API client"""
        try:
            if not self.hf_token:
                # st.sidebar.error("Hugging Face token not found. Please set the HF_TOKEN environment variable.")
                # st.sidebar.info("You can get a token from https://huggingface.co/settings/tokens")
                return False
            
            if not self.repo_id or self.repo_id == "default-user/ai-flaw-reports":
                # st.sidebar.error("Invalid Hugging Face repository ID. Please set the HF_REPO_ID environment variable.")
                # st.sidebar.info("Format should be 'username/dataset-name' or 'organization/dataset-name'")
                return False
            
            self.api = HfApi(token=self.hf_token)
            # st.sidebar.success("Successfully initialized Hugging Face API client")
            
            try:
                self.api.repo_info(
                    repo_id=self.repo_id, 
                    repo_type="dataset"
                )
                # st.sidebar.success(f"Connected to existing dataset repository: {self.repo_id}")
            except Exception as repo_error:
                # st.sidebar.warning(f"Repository does not exist yet: {str(repo_error)}")
                try:
                    create_repo(
                        repo_id=self.repo_id,
                        token=self.hf_token,
                        repo_type="dataset",
                        private=True
                    )
                    # st.sidebar.success(f"Created new dataset repository: {self.repo_id}")
                except Exception as create_error:
                    return False
            
            self.initialized = True
            return True
            
        except Exception as e:
            # st.sidebar.error(f"Error initializing Hugging Face provider: {str(e)}")
            return False
    
    def save_report(self, form_data):
        """Save a report to the Hugging Face repository"""
        # Generate a report ID if not provided
        report_id = form_data.get("Report ID")
        if not report_id:
            report_id = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            form_data["Report ID"] = report_id
        
        # st.sidebar.info(f"Attempting to save report with ID: {report_id}")
        
        if not self.initialized:
            # st.sidebar.warning("Storage provider not initialized. Initializing now...")
            if not self.initialize():
                # Store in session state as fallback
                session_key = f"report_{report_id}"
                st.session_state[session_key] = {
                    "form_data": form_data,
                    "timestamp": datetime.now().isoformat()
                }
                # st.sidebar.warning(f"Fallback: Report stored in session state due to initialization failure.")
                return f"session_state:{session_key}", None
        
        try:
            # Generate machine readable output
            machine_readable_output = None
            from form.data.schema import generate_machine_readable_output
            machine_readable_output = generate_machine_readable_output(form_data)
            
            report_data = {
                "form_data": form_data,
                "machine_readable": machine_readable_output,
                "timestamp": datetime.now().isoformat()
            }
            
            report_json = json.dumps(report_data, indent=2)
            
            report_path = f"reports/{report_id}.json"
            
            files = list_repo_files(
                    repo_id=self.repo_id,
                    repo_type="dataset",
                    token=self.hf_token
                )
                
            if not any(f.startswith("reports/") for f in files):
                    self.api.upload_file(
                        path_or_fileobj=io.BytesIO(b""),
                        path_in_repo="reports/.gitkeep",
                        repo_id=self.repo_id,
                        repo_type="dataset",
                        commit_message="Create reports directory"
                    )
                    # st.sidebar.info("Created reports directory in repository")
            
            self.api.upload_file(
                path_or_fileobj=io.BytesIO(report_json.encode()),
                path_in_repo=report_path,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=f"Add/update report {report_id}"
            )
            
            # st.sidebar.success(f"Successfully saved JSON report to {self.repo_id}/{report_path}")
            
            self._update_index_file(report_id, form_data)
            
            self._update_parquet_file(report_id, form_data, machine_readable_output)

            
            return f"huggingface:{self.repo_id}/{report_path}", machine_readable_output
            
        except Exception as e:
            # st.sidebar.error(f"Error saving report to Hugging Face: {str(e)}")
            
            # Store in session state as fallback
            session_key = f"report_{report_id}"
            st.session_state[session_key] = {
                "form_data": form_data,
                "timestamp": datetime.now().isoformat(),
                "machine_readable": machine_readable_output
            }
            # st.sidebar.warning(f"Fallback: Report stored in session state due to error.")
            
            return f"session_state:{session_key}", machine_readable_output
    
    def _update_index_file(self, report_id, form_data):
        """Update the index file with the new report information"""
        index_path = "reports_index.json"
        
        index_data = []
        existing_index = hf_hub_download(
                    repo_id=self.repo_id,
                    filename=index_path,
                    repo_type="dataset",
                    token=self.hf_token
                )
                
        with open(existing_index, "r") as f:
                    index_data = json.load(f)
                
                # st.sidebar.info(f"Downloaded existing index with {len(index_data)} reports")
            
        index_data = [r for r in index_data if r.get("report_id") != report_id]
            
        index_data.append({
                "report_id": report_id,
                "report_status": form_data.get("Report Status", "Unknown"),
                "report_types": form_data.get("Report Types", []),
                "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                "submission_timestamp": datetime.now().isoformat(),
                "file_path": f"reports/{report_id}.json"
            })
            
            # Sort by newest first
        index_data.sort(key=lambda x: x.get("submission_timestamp", ""), reverse=True)
            
        index_json = json.dumps(index_data, indent=2)
        self.api.upload_file(
                path_or_fileobj=io.BytesIO(index_json.encode()),
                path_in_repo=index_path,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=f"Update index with report {report_id}"
            )
            
            # st.sidebar.success(f"Updated index file with {len(index_data)} reports")
    
    def _update_parquet_file(self, report_id, form_data, machine_readable_output):
        """Update the Parquet file with the new report data"""
        try:
            report_row = {
                "report_id": report_id,
                "report_status": form_data.get("Report Status", "Unknown"),
                "report_types": json.dumps(form_data.get("Report Types", [])),
                "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                "submission_timestamp": datetime.now().isoformat(),
                "form_data": json.dumps(form_data),
                "machine_readable": json.dumps(machine_readable_output) if machine_readable_output else ""
            }
            
            new_df = pd.DataFrame([report_row])
            # st.sidebar.info(f"Prepared new row for Parquet file for report {report_id}")
            
            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    parquet_path = os.path.join(tmp_dir, self.parquet_file)
                    
                    try:
                        downloaded_file = hf_hub_download(
                            repo_id=self.repo_id,
                            filename=self.parquet_file,
                            repo_type="dataset",
                            token=self.hf_token,
                            local_dir=tmp_dir,
                            local_dir_use_symlinks=False
                        )
                        
                        existing_df = pd.read_parquet(downloaded_file)
                        # st.sidebar.success(f"Downloaded existing Parquet file with {len(existing_df)} rows")
                        
                        existing_df = existing_df[existing_df["report_id"] != report_id]
                        
                        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                        
                    except Exception as e:
                        # st.sidebar.info(f"No existing Parquet file found, creating new one: {str(e)}")
                        updated_df = new_df
                    
                    updated_df.to_parquet(parquet_path, index=False)
                    
                    with open(parquet_path, "rb") as f:
                        self.api.upload_file(
                            path_or_fileobj=f,
                            path_in_repo=self.parquet_file,
                            repo_id=self.repo_id,
                            repo_type="dataset",
                            commit_message=f"Update Parquet file with report {report_id}"
                        )
                    
                    # st.sidebar.success(f"Updated Parquet file with {len(updated_df)} reports")
            
            except Exception as download_error:
                # st.sidebar.warning(f"Error handling Parquet file: {str(download_error)}")
                
                with tempfile.TemporaryDirectory() as tmp_dir:
                    parquet_path = os.path.join(tmp_dir, self.parquet_file)
                    new_df.to_parquet(parquet_path, index=False)
                    
                    with open(parquet_path, "rb") as f:
                        self.api.upload_file(
                            path_or_fileobj=f,
                            path_in_repo=self.parquet_file,
                            repo_id=self.repo_id,
                            repo_type="dataset",
                            commit_message=f"Create new Parquet file with report {report_id}"
                        )
                    
                    # st.sidebar.success(f"Created new Parquet file with report {report_id}")
        
        except Exception as e:
            # st.sidebar.error(f"Error updating Parquet file: {str(e)}")
            raise
    
    def get_report(self, report_id):
        """Retrieve a report from the Hugging Face repository"""
        if not self.initialized:
            if not self.initialize():
                session_key = f"report_{report_id}"
                if session_key in st.session_state:
                    return st.session_state[session_key]
                return None
        
        try:
            report_path = f"reports/{report_id}.json"
            
            downloaded_file = hf_hub_download(
                repo_id=self.repo_id,
                filename=report_path,
                repo_type="dataset",
                token=self.hf_token
            )
            
            with open(downloaded_file, "r") as f:
                report_data = json.load(f)
            
            # st.sidebar.success(f"Successfully retrieved report {report_id}")
            return report_data
            
        except Exception as e:
            # st.sidebar.warning(f"Could not retrieve report from Hugging Face: {str(e)}")
            
            session_key = f"report_{report_id}"
            if session_key in st.session_state:
                # st.sidebar.info(f"Retrieved report {report_id} from session state")
                return st.session_state[session_key]
            
            return None
    
    def update_report(self, report_id, form_data):
        """Update an existing report"""
        # Just use save_report since it will overwrite the existing file
        result, _ = self.save_report(form_data)
        return result.startswith("huggingface:")
    
    def list_reports(self, limit=100):
        """List all reports in the repository"""
        reports = []
        
        if not self.initialized:
            if not self.initialize():
                for key in st.session_state:
                    if key.startswith("report_"):
                            report_id = key.replace("report_", "")
                            data = st.session_state[key]
                            form_data = data.get("form_data", {})
                            
                            reports.append({
                                "report_id": report_id,
                                "report_status": form_data.get("Report Status", "Unknown"),
                                "report_types": form_data.get("Report Types", []),
                                "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                                "submission_timestamp": data.get("timestamp", "Unknown")
                            })
                
                return reports[:limit]
        
        try:
            try:
                index_path = "reports_index.json"
                
                # Download the index
                downloaded_index = hf_hub_download(
                    repo_id=self.repo_id,
                    filename=index_path,
                    repo_type="dataset",
                    token=self.hf_token
                )
                
                with open(downloaded_index, "r") as f:
                    reports = json.load(f)
                
                # st.sidebar.success(f"Retrieved {len(reports)} reports from index file")
                
            except Exception as index_error:
                # st.sidebar.info(f"Could not use index file, trying Parquet file: {str(index_error)}")
                
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        try:
                            downloaded_file = hf_hub_download(
                                repo_id=self.repo_id,
                                filename=self.parquet_file,
                                repo_type="dataset",
                                token=self.hf_token,
                                local_dir=tmp_dir,
                                local_dir_use_symlinks=False
                            )
                            
                            df = pd.read_parquet(downloaded_file)
                            # st.sidebar.success(f"Retrieved {len(df)} reports from Parquet file")
                            
                            for _, row in df.iterrows():
                                    if isinstance(row["report_types"], str):
                                        report_types = json.loads(row["report_types"])
                                    else:
                                        report_types = row["report_types"]
                                        
                                    reports.append({
                                        "report_id": row["report_id"],
                                        "report_status": row["report_status"],
                                        "report_types": report_types,
                                        "reporter_id": row["reporter_id"],
                                        "submission_timestamp": row["submission_timestamp"]
                                    })
                            
                        except Exception as parquet_error:
                            # st.sidebar.info(f"Could not use Parquet file, scanning repository: {str(parquet_error)}")
                            raise
                        
                except Exception:
                    # st.sidebar.info("Scanning repository for report files")
                    
                    files = list_repo_files(
                        repo_id=self.repo_id,
                        repo_type="dataset",
                        token=self.hf_token
                    )
                    
                    report_files = [f for f in files if f.startswith("reports/") and f.endswith(".json")]
                    
                    # st.sidebar.info(f"Found {len(report_files)} report files in repository")
                    
                    for file_path in report_files[:limit]:
                            report_id = file_path.replace("reports/", "").replace(".json", "")
                            
                            downloaded_file = hf_hub_download(
                                repo_id=self.repo_id,
                                filename=file_path,
                                repo_type="dataset",
                                token=self.hf_token
                            )
                            
                            with open(downloaded_file, "r") as f:
                                report_data = json.load(f)
                            
                            form_data = report_data.get("form_data", {})
                            
                            reports.append({
                                "report_id": report_id,
                                "report_status": form_data.get("Report Status", "Unknown"),
                                "report_types": form_data.get("Report Types", []),
                                "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                                "submission_timestamp": report_data.get("timestamp", "Unknown")
                            })
            
            # Add any reports from session state that aren't already in the list
            for key in st.session_state:
                if key.startswith("report_"):
                        report_id = key.replace("report_", "")
                        
                        # Skip if this report is already in the list
                        if any(r.get("report_id") == report_id for r in reports):
                            continue
                            
                        data = st.session_state[key]
                        form_data = data.get("form_data", {})
                        
                        reports.append({
                            "report_id": report_id,
                            "report_status": form_data.get("Report Status", "Unknown"),
                            "report_types": form_data.get("Report Types", []),
                            "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                            "submission_timestamp": data.get("timestamp", "Unknown")
                        })
            
            # Sort by newest first
            reports.sort(key=lambda x: x.get("submission_timestamp", ""), reverse=True)
            
            return reports[:limit]
            
        except Exception as e:
            # st.sidebar.error(f"Error listing reports: {str(e)}")
            
            # Fall back to session state reports
            for key in st.session_state:
                if key.startswith("report_"):
                        report_id = key.replace("report_", "")
                        data = st.session_state[key]
                        form_data = data.get("form_data", {})
                        
                        reports.append({
                            "report_id": report_id,
                            "report_status": form_data.get("Report Status", "Unknown"),
                            "report_types": form_data.get("Report Types", []),
                            "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                            "submission_timestamp": data.get("timestamp", "Unknown")
                        })
            
            return reports[:limit]
            
    def query_reports(self, query):
        """
        Query reports (simplified implementation)
        
        Args:
            query (str): Query string to filter reports
            
        Returns:
            list: List of reports (without filtering for now)
        """
        # st.sidebar.warning("Direct SQL querying is not supported in the simplified implementation")

        all_reports = self.list_reports(limit=1000)
        return all_reports