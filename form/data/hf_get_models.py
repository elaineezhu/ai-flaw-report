import requests
import streamlit as st
from form.data.constants import PRIORITY_MODELS
from difflib import get_close_matches

@st.cache_data(ttl=3600) # Cache results for 1 hour
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
            
            result_models.append("Other")
            
            return result_models
        else:
            st.warning(f"Failed to fetch models from Hugging Face API. Status code: {response.status_code}")
            # Return priority models + default message in case of API failure
            if include_priority:
                result_models.append("Other")
                return result_models
            else:
                return ["Failed to load models", "Other"]
    
    except Exception as e:
        st.error(f"Error fetching models from Hugging Face: {str(e)}")
        # Return priority models + error message in case of exception
        if include_priority:
            result_models.append("Other")
            return result_models
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
        if "Other" in combined_options:
            combined_options.remove("Other")
        combined_options.append("Other")
        return combined_options
    else:
        from form.data.constants import SYSTEM_OPTIONS
        return SYSTEM_OPTIONS
    
def searchable_model_selector(available_models, key_prefix="model", max_selections=10, help_text=None):
    """
    A searchable model selector that supports free text input with autocomplete suggestions.
    
    Args:
        available_models (list): List of available model options to choose from
        key_prefix (str): Prefix for session state keys to avoid conflicts
        max_selections (int): Maximum number of models that can be selected
        help_text (str): Help text to display with the selector
    
    Returns:
        list: List of selected models (including any custom entries)
    """
    if f"{key_prefix}_selections" not in st.session_state:
        st.session_state[f"{key_prefix}_selections"] = []
    
    if f"{key_prefix}_current_input" not in st.session_state:
        st.session_state[f"{key_prefix}_current_input"] = ""
    
    if f"{key_prefix}_pending_selection" not in st.session_state:
        st.session_state[f"{key_prefix}_pending_selection"] = None
    
    if st.session_state[f"{key_prefix}_pending_selection"] is not None:
        model_name = st.session_state[f"{key_prefix}_pending_selection"]
        if model_name and model_name not in st.session_state[f"{key_prefix}_selections"]:
            st.session_state[f"{key_prefix}_selections"].append(model_name)
        st.session_state[f"{key_prefix}_pending_selection"] = None
        st.session_state[f"{key_prefix}_current_input"] = ""
        st.rerun()
    
    if st.session_state[f"{key_prefix}_selections"]:
        st.write("Selected models:")
        cols = st.columns([0.9, 0.1])
        for i, selected in enumerate(st.session_state[f"{key_prefix}_selections"]):
            with cols[0]:
                st.text(f"• {selected}")
            with cols[1]:
                if st.button("❌", key=f"{key_prefix}_remove_{i}"):
                    st.session_state[f"{key_prefix}_selections"].pop(i)
                    st.rerun()
    
    if len(st.session_state[f"{key_prefix}_selections"]) >= max_selections:
        st.warning(f"Maximum of {max_selections} models can be selected.")
        return st.session_state[f"{key_prefix}_selections"]
    
    def on_input_change():
        st.session_state[f"{key_prefix}_current_input"] = st.session_state[f"{key_prefix}_text_input"]
    
    def add_custom_model():
        model_name = st.session_state[f"{key_prefix}_custom_input"].strip()
        if model_name and model_name not in st.session_state[f"{key_prefix}_selections"]:
            st.session_state[f"{key_prefix}_selections"].append(model_name)
            st.session_state[f"{key_prefix}_custom_input"] = ""
            st.rerun()
    
    def add_suggestion(model_name):
        st.session_state[f"{key_prefix}_pending_selection"] = model_name
    
    current_input = st.text_input(
        "Search for a model",
        key=f"{key_prefix}_text_input",
        value=st.session_state[f"{key_prefix}_current_input"],
        on_change=on_input_change,
        help=help_text
    )
    
    if current_input:
        input_lower = current_input.lower()
        
        # First try exact matches
        exact_matches = [model for model in available_models 
                         if input_lower in model.lower() 
                         and model not in st.session_state[f"{key_prefix}_selections"]]
        
        if not exact_matches:
            # If not, use difflib to find close matches
            close_matches = get_close_matches(current_input, available_models, n=5, cutoff=0.6)
            
            suggestions = [match for match in close_matches 
                          if match not in st.session_state[f"{key_prefix}_selections"]]
        else:
            suggestions = sorted(exact_matches, key=lambda x: (len(x), x))[:5]
        
        if suggestions:
            st.write("Suggestions:")
            cols = st.columns(min(len(suggestions), 3))
            for i, suggestion in enumerate(suggestions[:5]):
                with cols[i % 3]:
                    if st.button(suggestion, key=f"{key_prefix}_suggestion_{i}"):
                        add_suggestion(suggestion)
        else:
            st.write("No matching models found. You can add a custom entry:")
            
            st.text_input(
                "Enter custom model name",
                key=f"{key_prefix}_custom_input",
                on_change=add_custom_model
            )
    
    return st.session_state[f"{key_prefix}_selections"]