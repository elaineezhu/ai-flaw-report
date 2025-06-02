import os
import streamlit as st
import shutil
import sys

def save_uploaded_files(uploaded_files, report_id=None):
    """
    Save uploaded files and return their paths
    
    Args:
        uploaded_files (list): List of uploaded files from st.file_uploader
        report_id (str, optional): Report ID to include in filenames
    
    Returns:
        dict: Dictionary with original filenames as keys and saved paths as values
    """
    file_paths = {}
    
    # Create directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # st.sidebar.info(f"Saving {len(uploaded_files)} uploaded files with report ID: {report_id}")
    
    for file in uploaded_files:
        # Generate filename with report_id if provided
        if report_id:
            original_name, extension = os.path.splitext(file.name)
            filename = f"{report_id}_{original_name}{extension}"
        else:
            filename = file.name
        
        # Full path where the file will be saved
        file_path = os.path.join("uploads", filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        
        # st.sidebar.success(f"Saved file: {filename}")
        
        # Store original filename -> path mapping
        file_paths[file.name] = file_path
    
    return file_paths

def get_uploaded_files_for_report(report_id):
    """
    Get all files associated with a specific report ID
    
    Args:
        report_id (str): The report ID to search for
    
    Returns:
        list: List of file paths associated with the report
    """
    if not os.path.exists("uploads"):
        return []
    
    # Find all files that start with the report ID
    files = [os.path.join("uploads", f) for f in os.listdir("uploads") 
             if f.startswith(f"{report_id}_")]
    
    return files

def delete_uploaded_files_for_report(report_id):
    """
    Delete all files associated with a specific report ID
    
    Args:
        report_id (str): The report ID whose files should be deleted
    
    Returns:
        int: Number of files deleted
    """
    files = get_uploaded_files_for_report(report_id)
    
    count = 0
    for file_path in files:
        try:
            os.remove(file_path)
            count += 1
        except Exception as e:
            st.warning(f"Failed to delete file {file_path}: {e}")
    
    return count

def upload_files_to_huggingface(report_id, repo_id, token):
    """
    Upload files associated with a report to Hugging Face repository
    
    Args:
        report_id (str): The report ID whose files to upload
        repo_id (str): Hugging Face repository ID
        token (str): Hugging Face token
        
    Returns:
        list: URLs of uploaded files
    """
    import streamlit as st
    # st.sidebar.info(f"Uploading files for report {report_id} to Hugging Face repo {repo_id}")
    
    try:
        # Get files associated with the report
        files = get_uploaded_files_for_report(report_id)
        # st.sidebar.info(f"Found {len(files)} files to upload: {files}")
        
        if not files:
            # st.sidebar.warning("No files found to upload")
            return []
        
        # Import huggingface_hub
        try:
            from huggingface_hub import HfApi, HfFolder
            from huggingface_hub.utils import RepositoryNotFoundError
        except ImportError:
            # st.sidebar.error("huggingface_hub package not installed. Installing now...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
            from huggingface_hub import HfApi, HfFolder
        
        # Set up the API
        api = HfApi(token=token)
        HfFolder.save_token(token)  # Save token to use with command-line tools
        
        # Create the repository if it doesn't exist
        try:
            # st.sidebar.info(f"Checking if repository {repo_id} exists...")
            api.repo_info(repo_id=repo_id, repo_type="dataset")
            # st.sidebar.success(f"Repository {repo_id} exists")
        except RepositoryNotFoundError:
            # st.sidebar.warning(f"Repository {repo_id} not found. Creating repository...")
            api.create_repo(repo_id=repo_id, repo_type="dataset", private=True)
            # st.sidebar.success(f"Repository {repo_id} created")
        except Exception as e:
            # st.sidebar.error(f"Error checking/creating repository: {e}")
            api.create_repo(repo_id=repo_id, repo_type="dataset", private=True, exist_ok=True)

        
        # Create uploads directory if it doesn't exist
        # st.sidebar.info("Creating uploads directory if it doesn't exist...")
        # We'll try to create the directory by uploading a small README file
        readme_content = f"# Uploads for {repo_id}\n\nThis directory contains files uploaded with reports."
            
        # Let's create a temporary file for the README
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".md") as tmp:
            tmp.write(readme_content)
            tmp_path = tmp.name
            
        # Upload the README to create the directory
        api.upload_file(
            path_or_fileobj=tmp_path,
            path_in_repo="uploads/README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Initialize uploads directory"
        )
            
        # Clean up the temporary file
        os.unlink(tmp_path)
            
        # st.sidebar.success("Uploads directory created or verified")
            
        # Upload each file
        uploaded_urls = []
        for file_path in files:
            filename = os.path.basename(file_path)
            remote_path = f"uploads/{filename}"
            
            #st.sidebar.info(f"Uploading {filename}...")
            
            response = api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=remote_path,
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Upload file for report {report_id}"
            )
                
            file_url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/uploads/{filename}"
            uploaded_urls.append(file_url)
            # st.sidebar.success(f"Successfully uploaded {filename}")
            
        # st.sidebar.success(f"Uploaded {len(uploaded_urls)} out of {len(files)} files")
        return uploaded_urls
        
    except Exception as e:
        # st.sidebar.error(f"Error in upload_files_to_huggingface: {e}")
        # Show full traceback for debugging
        import traceback
        # st.sidebar.error(f"Traceback: {traceback.format_exc()}")
        return []

