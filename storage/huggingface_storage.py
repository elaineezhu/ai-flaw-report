import os
import json
from datetime import datetime
import tempfile
from storage.storage_interface import StorageProvider, LocalStorageProvider

class HuggingFaceStorageProvider(StorageProvider):
    """Provider that stores reports using Hugging Face Datasets"""
    
    def __init__(self, hf_token=None, repo_id=None):
        """
        Initialize HuggingFace storage provider
        
        Args:
            hf_token (str): Hugging Face API token (default: from environment variable)
            repo_id (str): Repository ID for dataset (default: from environment variable)
        """
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        self.repo_id = repo_id or os.environ.get("HF_REPO_ID", "default-user/ai-flaw-reports")
        self.dataset = None
        self.initialized = False
        self.parquet_file = "reports.parquet"
        self.local_cache_dir = os.path.join(tempfile.gettempdir(), "hf_dataset_cache")
    
    def initialize(self):
        """Initialize connection to Hugging Face Datasets"""
        import streamlit as st
        
        try:
            try:
                import datasets
                import duckdb
                import pandas as pd
            except ImportError:
                st.sidebar.error("Required packages not installed. Please install: datasets, duckdb, pandas")
                return False
            
            if not self.hf_token:
                st.sidebar.error("Hugging Face token not found. Please set the HF_TOKEN environment variable.")
                st.sidebar.info("You can get a token from https://huggingface.co/settings/tokens")
                return False
            
            if not self.repo_id or self.repo_id == "default-user/ai-flaw-reports":
                st.sidebar.error("Invalid Hugging Face repository ID. Please set the HF_REPO_ID environment variable.")
                st.sidebar.info("Format should be 'username/dataset-name' or 'organization/dataset-name'")
                return False
            
            os.environ["HF_TOKEN"] = self.hf_token
            
            try:
                self.dataset = datasets.load_dataset(
                    self.repo_id, 
                    token=self.hf_token,
                    cache_dir=self.local_cache_dir
                )
                st.sidebar.success(f"Connected to Hugging Face dataset: {self.repo_id}")
                self.initialized = True
                return True
            except Exception as e:
                st.sidebar.warning(f"Dataset connection issue: {e}")
                # Initialization when dataset doesn't exist or is empty
                if ("doesn't contain any data files" in str(e) or 
                    "404" in str(e) or 
                    "not found" in str(e).lower()): # I'll make sure that this is an extensive enough check of errors
                    
                    st.sidebar.info(f"Creating initial dataset structure for {self.repo_id}...")
                    
                    initial_data = {
                        "report_id": ["placeholder"],
                        "report_status": ["Placeholder"],
                        "report_types": [["Placeholder"]],
                        "reporter_id": ["System"],
                        "submission_timestamp": [datetime.now().isoformat()],
                        "form_data": [json.dumps({"Placeholder": True})],
                        "machine_readable": [json.dumps({"@context": "https://schema.org", "@type": "Placeholder"})]
                    }
                    
                    df = pd.DataFrame(initial_data)
                    initial_dataset = datasets.Dataset.from_pandas(df)
                    
                    # Push to Hub to create the initial structure
                    try:
                        initial_dataset.push_to_hub(
                            self.repo_id,
                            token=self.hf_token,
                            private=True
                        )
                        st.sidebar.success(f"Successfully created initial dataset: {self.repo_id}")
                        self.initialized = True
                        self.dataset = initial_dataset
                        return True
                    except Exception as init_error:
                        st.sidebar.error(f"Failed to create initial dataset: {init_error}")
                        return False
                else:
                    st.sidebar.warning(f"Failed to connect to Hugging Face dataset: {e}")
                    return False
                
        except Exception as e:
            st.sidebar.error(f"Error initializing Hugging Face storage: {e}")
            return False
    
    def save_report(self, form_data):
        """Save report to Hugging Face dataset using parquet format"""
        import streamlit as st
        
        report_id = form_data.get("Report ID")
        
        # DEBUGGING INFO (Will delete later)
        st.sidebar.info(f"Attempting to save report with ID: {report_id}")
        
        from form.data.schema import generate_machine_readable_output
        machine_readable_output = generate_machine_readable_output(form_data)
        
        if not self.initialized:
            st.sidebar.warning("HuggingFace storage not initialized. Attempting to initialize...")
            self.initialize()
            
        if not self.initialized:
            st.sidebar.warning("HuggingFace storage initialization failed. Using local storage.")
            from storage.storage_interface import LocalStorageProvider
            local_provider = LocalStorageProvider()
            return local_provider.save_report(form_data)
        
        try:
            import datasets
            import pandas as pd
            
            # Save locally as backup -> will delete this later once we I can confirm that HF always works
            local_path = os.path.join("reports", f"report_{report_id}.json")
            os.makedirs("reports", exist_ok=True)
            
            report_data = {
                "report_id": report_id,
                "report_status": form_data.get("Report Status", "Submitted"),
                "report_types": form_data.get("Report Types", []),
                "reporter_id": form_data.get("Reporter ID", "Anonymous"),
                "submission_timestamp": datetime.now().isoformat(),
                "form_data": json.dumps(form_data),
                "machine_readable": json.dumps(machine_readable_output)
            }
            
            st.sidebar.info(f"Report data prepared with status: {report_data['report_status']}")
            
            with open(local_path, "w") as f:
                json.dump({
                    "form_data": form_data,
                    "machine_readable": machine_readable_output,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=4)
                
            st.sidebar.success(f"Report saved locally to: {local_path}")
            
            df = pd.DataFrame([report_data])
            
            st.sidebar.info(f"Created DataFrame with {len(df)} rows. Columns: {', '.join(df.columns)}")
            
            if "Uploaded File Paths" in form_data:
                st.sidebar.info(f"Uploading {len(form_data['Uploaded File Paths'])} files to Hugging Face...")
                try:
                    from form.utils.file_handling import upload_files_to_huggingface
                    uploaded_urls = upload_files_to_huggingface(report_id, self.repo_id, self.hf_token)
                    
                    if uploaded_urls:
                        st.sidebar.success(f"Successfully uploaded {len(uploaded_urls)} files to Hugging Face")
                        form_data["Uploaded File URLs"] = uploaded_urls
                        report_data["form_data"] = json.dumps(form_data)
                        machine_readable_output["files"] = uploaded_urls
                        df = pd.DataFrame([report_data])
                except Exception as e:
                    st.sidebar.warning(f"Error uploading files to Hugging Face: {e}")
                    st.sidebar.info("Files are still saved locally and referenced in the report.")
            
            try:
                st.sidebar.info(f"Attempting to load existing dataset from {self.repo_id}...")
                
                existing_dataset = datasets.load_dataset(
                    self.repo_id, 
                    token=self.hf_token,
                    cache_dir=self.local_cache_dir
                )
                
                st.sidebar.success(f"Successfully loaded dataset. Found {len(existing_dataset['train'])} existing records.")
                
                existing_df = existing_dataset["train"].to_pandas()
                
                st.sidebar.info(f"Existing dataset has {len(existing_df)} rows")
                
                # Remove placeholder row if present
                placeholder_count = len(existing_df[existing_df["report_id"] == "placeholder"])
                if placeholder_count > 0:
                    st.sidebar.info(f"Removing {placeholder_count} placeholder records")
                    existing_df = existing_df[existing_df["report_id"] != "placeholder"]
                
                # Remove previous version of this report if it exists
                duplicate_count = len(existing_df[existing_df["report_id"] == report_id])
                if duplicate_count > 0:
                    st.sidebar.info(f"Removing {duplicate_count} previous versions of this report")
                    existing_df = existing_df[existing_df["report_id"] != report_id]
                
                updated_df = pd.concat([existing_df, df], ignore_index=True)
                st.sidebar.info(f"Combined dataset now has {len(updated_df)} rows")
                
                updated_dataset = datasets.Dataset.from_pandas(updated_df)
                
            except Exception as e:
                st.sidebar.warning(f"Error handling existing dataset: {e}")
                st.sidebar.info("Creating new dataset from scratch")
                # Dataset doesn't exist yet so create new one
                updated_dataset = datasets.Dataset.from_pandas(df)
            
            # Push to Hub
            st.sidebar.info(f"Pushing dataset to Hugging Face Hub: {self.repo_id}...")
            
            # Before pushing, verify dataset structure
            st.sidebar.info(f"Dataset structure: {updated_dataset}")
            
            # Push to Hub with detailed feedback
            try:
                push_result = updated_dataset.push_to_hub(
                    self.repo_id,
                    token=self.hf_token,
                    private=True
                )
                st.sidebar.success(f"Successfully pushed to Hub. Result: {push_result}")
            except Exception as push_error:
                st.sidebar.error(f"Error pushing to Hub: {push_error}")
                # Try to create it first if there's an error
                try:
                    st.sidebar.info("Attempting to create dataset repo first...")
                    from huggingface_hub import create_repo
                    create_repo(
                        self.repo_id, 
                        token=self.hf_token, 
                        private=True,
                        repo_type="dataset"
                    )
                    push_result = updated_dataset.push_to_hub(
                        self.repo_id,
                        token=self.hf_token,
                        private=True
                    )
                    st.sidebar.success(f"Successfully created repo and pushed dataset: {push_result}")
                except Exception as create_error:
                    st.sidebar.error(f"Failed to create repo: {create_error}")
                    raise
            
            return f"huggingface:{self.repo_id}/{report_id}", machine_readable_output
            
        except Exception as e:
            st.sidebar.error(f"Error saving to Hugging Face: {str(e)}")
            st.sidebar.exception(e)
            return local_path, machine_readable_output
    
    def get_report(self, report_id):
        """Retrieve a report from Hugging Face dataset"""
        import streamlit as st
        
        if not self.initialized:
            local_provider = LocalStorageProvider()
            return local_provider.get_report(report_id)
        
        try:
            import datasets
            import duckdb
            import pandas as pd
            
            dataset = datasets.load_dataset(
                self.repo_id, 
                token=self.hf_token, 
                cache_dir=self.local_cache_dir
            )
            
            df = dataset["train"].to_pandas()
            
            report_row = df[df["report_id"] == report_id]
            
            if len(report_row) > 0:
                row = report_row.iloc[0]
                
                form_data = json.loads(row["form_data"])
                machine_readable = json.loads(row["machine_readable"])
                
                return {
                    "form_data": form_data,
                    "machine_readable": machine_readable,
                    "timestamp": row["submission_timestamp"]
                }
            
            # If not found, try local storage -> will delete this later once we I can confirm that HF always works
            st.warning(f"Report {report_id} not found in Hugging Face dataset. Trying local storage.")
            local_provider = LocalStorageProvider()
            return local_provider.get_report(report_id)
                
        except Exception as e:
            st.error(f"Error retrieving from Hugging Face: {e}")
            local_provider = LocalStorageProvider()
            return local_provider.get_report(report_id)
    
    def update_report(self, report_id, form_data):
        """Update an existing report in Hugging Face dataset"""
        # For the HF implementation, this is essentially the same as saving a new report as we're replacing the entire document
        _, machine_readable_output = self.save_report(form_data)
        return True
    
    def list_reports(self, limit=100):
        """List reports in the dataset"""
        import streamlit as st
        
        if not self.initialized:
            return []
        
        try:
            import datasets
            import pandas as pd
            
            dataset = datasets.load_dataset(
                self.repo_id, 
                token=self.hf_token,
                cache_dir=self.local_cache_dir
            )
            
            df = dataset["train"].to_pandas()
            
            df = df[df["report_id"] != "placeholder"]
            
            report_list = []
            for _, row in df.head(limit).iterrows():
                report_list.append({
                    "report_id": row["report_id"],
                    "report_status": row["report_status"],
                    "report_types": row["report_types"],
                    "reporter_id": row["reporter_id"],
                    "submission_timestamp": row["submission_timestamp"]
                })
            
            return report_list
                
        except Exception as e:
            st.error(f"Error listing reports from Hugging Face: {e}")
            return []
    
    def query_reports(self, query):
        """
        Query reports using DuckDB SQL syntax
        
        Args:
            query (str): SQL query to execute against the dataset
            
        Returns:
            pandas.DataFrame: Query results
        """
        import streamlit as st
        
        if not self.initialized:
            st.warning("Hugging Face storage not initialized. Cannot run query.")
            return None
        
        try:
            import duckdb
            import datasets
            
            parquet_url = f"https://huggingface.co/datasets/{self.repo_id}/resolve/main/data/train.parquet"
            
            result = duckdb.query(f"""
                SELECT * FROM read_parquet('{parquet_url}')
                WHERE {query}
            """).df()
            
            return result
                
        except Exception as e:
            st.error(f"Error querying reports: {e}")
            return None
            
    def get_file_url(self, filename):
        """
        Get the URL for a file in the Hugging Face repository
        
        Args:
            filename (str): The filename to get the URL for
            
        Returns:
            str: The URL to the file
        """
        return f"https://huggingface.co/datasets/{self.repo_id}/resolve/main/uploads/{filename}"
        
    def list_uploaded_files(self):
        """
        List all files in the 'uploads' directory of the Hugging Face repository
        
        Returns:
            list: List of filenames
        """
        try:
            import requests
            
            url = f"https://huggingface.co/api/datasets/{self.repo_id}/tree/main/uploads"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return [item["path"].replace("uploads/", "") for item in response.json()]
            elif response.status_code == 404:
                # Directory doesn't exist yet
                return []
            else:
                import streamlit as st
                st.warning(f"Failed to list files: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            import streamlit as st
            st.error(f"Error listing uploaded files: {e}")
            return []