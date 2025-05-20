import requests
import streamlit as st
from form.data.constants import PRIORITY_MODELS

@st.cache_data(ttl=3600)  # Cache results for 1 hour
def fetch_top_huggingface_models(limit=400, include_priority=True):
    """
    Fetch the top models from Hugging Face based on downloads,
    with priority models at the top of the list.
    
    Args:
        limit (int): Number of models to fetch (default: 400)
        include_priority (bool): Whether to include priority models at the top
    
    Returns:
        list: List of model names with priority models at the top, 
             followed by top downloads from Hugging Face
    """
    if include_priority:
        result_models = PRIORITY_MODELS.copy()
    else:
        result_models = []
    
    try:
        api_url = "https://huggingface.co/api/models"
        
        params = {
            "sort": "downloads",
            "direction": "-1",
            "limit": limit
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            models_data = response.json()
            
            hf_model_names = [model["modelId"] for model in models_data]
            
            # Add models from Hugging Face that aren't already in priority list
            for model in hf_model_names:
                if model not in result_models:
                    result_models.append(model)
            
            return result_models
        else:
            st.warning(f"Failed to fetch models from Hugging Face API. Status code: {response.status_code}")
            # Return priority models + default message in case of API failure
            if include_priority:
                return result_models + ["Failed to load additional models", "Other"]
            else:
                return ["Failed to load models", "Other"]
    
    except Exception as e:
        st.error(f"Error fetching models from Hugging Face: {str(e)}")
        # Return priority models + error message in case of exception
        if include_priority:
            return result_models + ["Error loading additional models", "Other"]
        else:
            return ["Error loading models", "Other"]

def get_systems_options(use_api=True, include_priority=True):
    """
    Get the systems options either from Hugging Face API or fallback to constants.
    
    Args:
        use_api (bool): Whether to use the API or fallback to constants
        include_priority (bool): Whether to include priority models at the top
    
    Returns:
        list: List of system options
    """
    if use_api:
        models = fetch_top_huggingface_models(include_priority=include_priority)
        if models and len(models) > 2:
            return models
    
    # If API is disabled or failed, fall back to constants
    # But still include priority models at the top if requested
    if include_priority:
        from form.data.constants import SYSTEM_OPTIONS
        existing_options = set(PRIORITY_MODELS)
        combined_options = PRIORITY_MODELS.copy()
        for option in SYSTEM_OPTIONS:
            if option not in existing_options and option != "Other":
                combined_options.append(option)
        combined_options.append("Other")
        return combined_options
    else:
        from form.data.constants import SYSTEM_OPTIONS
        return SYSTEM_OPTIONS