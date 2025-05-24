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
    An improved searchable model selector with better UI elements for dark theme
    
    Args:
        available_models (list): List of available model options to choose from
        key_prefix (str): Prefix for session state keys to avoid conflicts
        max_selections (int): Maximum number of models that can be selected
        help_text (str): Help text to display with the selector
    
    Returns:
        list: List of selected models (including any custom entries)
    """
    
    def on_input_change():
        current_input = st.session_state[f"{key_prefix}_text_input"].strip()
        st.session_state[f"{key_prefix}_current_input"] = current_input
        
        if current_input:
            input_lower = current_input.lower()
            
            exact_matches = [model for model in available_models 
                            if input_lower in model.lower() 
                            and model not in st.session_state[f"{key_prefix}_selections"]]
            
            if not exact_matches:
                close_matches = get_close_matches(current_input, available_models, n=5, cutoff=0.6)
                
                suggestions = [match for match in close_matches 
                              if match not in st.session_state[f"{key_prefix}_selections"]]
            else:
                suggestions = sorted(exact_matches, key=lambda x: (len(x), x))[:5]
            
            st.session_state[f"{key_prefix}_suggestions"] = suggestions
        else:
            st.session_state[f"{key_prefix}_suggestions"] = []
    
    def add_custom_model():
        model_name = st.session_state[f"{key_prefix}_custom_input"].strip()
        if model_name and model_name not in st.session_state[f"{key_prefix}_selections"]:
            if len(st.session_state[f"{key_prefix}_selections"]) < max_selections:
                st.session_state[f"{key_prefix}_selections"].append(model_name)
                st.session_state[f"{key_prefix}_custom_input"] = ""
                st.rerun()
            else:
                st.warning(f"Maximum of {max_selections} models can be selected.")
    
    def add_suggestion(model_name):
        st.session_state[f"{key_prefix}_pending_selection"] = model_name
    
    if f"{key_prefix}_selections" not in st.session_state:
        st.session_state[f"{key_prefix}_selections"] = []
    
    if f"{key_prefix}_current_input" not in st.session_state:
        st.session_state[f"{key_prefix}_current_input"] = ""
    
    if f"{key_prefix}_pending_selection" not in st.session_state:
        st.session_state[f"{key_prefix}_pending_selection"] = None
    
    if f"{key_prefix}_suggestions" not in st.session_state:
        st.session_state[f"{key_prefix}_suggestions"] = []
    
    if st.session_state[f"{key_prefix}_pending_selection"] is not None:
        model_name = st.session_state[f"{key_prefix}_pending_selection"]
        if model_name and model_name not in st.session_state[f"{key_prefix}_selections"]:
            if len(st.session_state[f"{key_prefix}_selections"]) < max_selections:
                st.session_state[f"{key_prefix}_selections"].append(model_name)
            else:
                st.warning(f"Maximum of {max_selections} models can be selected.")
        st.session_state[f"{key_prefix}_pending_selection"] = None
        st.session_state[f"{key_prefix}_current_input"] = ""
        st.rerun()
    
    current_input = st.text_input(
        "",
        key=f"{key_prefix}_text_input",
        value=st.session_state[f"{key_prefix}_current_input"],
        on_change=on_input_change,
        placeholder="Start typing to search...",
        help=help_text
    )
    
    if st.session_state[f"{key_prefix}_selections"]:
        for i, selected in enumerate(st.session_state[f"{key_prefix}_selections"]):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.button(
                    selected,
                    key=f"{key_prefix}_selected_{i}",
                    disabled=True,
                    use_container_width=True
                )
            with col2:
                if st.button("❌", key=f"{key_prefix}_remove_{i}"):
                    st.session_state[f"{key_prefix}_selections"].pop(i)
                    st.rerun()
    
    if len(st.session_state[f"{key_prefix}_selections"]) >= max_selections:
        st.warning(f"Maximum of {max_selections} models can be selected.")
        return st.session_state[f"{key_prefix}_selections"]
    
    suggestions = st.session_state[f"{key_prefix}_suggestions"]
    if suggestions:
        st.caption("Click to add:")
        
        num_cols = min(len(suggestions), 3)
        suggestion_cols = st.columns(num_cols)
        
        for i, suggestion in enumerate(suggestions):
            with suggestion_cols[i % num_cols]:
                if st.button(
                    f"➕ {suggestion}", 
                    key=f"{key_prefix}_suggestion_{i}",
                    use_container_width=True
                ):
                    add_suggestion(suggestion)
    elif current_input and not suggestions:
        st.write("No matching entries found. You can add a custom entry:")
        
        st.text_input(
            "Enter custom entry",
            key=f"{key_prefix}_custom_input",
            on_change=add_custom_model,
            placeholder="Type a custom entry and press Enter"
        )
    
    return st.session_state[f"{key_prefix}_selections"]

def searchable_select_with_other(available_models, key_prefix, title=None, caption=None, help_text=None, max_selections=10):
    """
    A utility function that combines searchable_model_selector with Other option handling
    
    Args:
        available_models (list): List of options to select from
        key_prefix (str): Prefix for session state keys
        title (str, optional): Title to display above the selector
        caption (str, optional): Caption text to display below the title
        help_text (str, optional): Help text to display
        max_selections (int): Maximum number of selections allowed
        
    Returns:
        tuple: (selected_options, other_text)
    """
    import streamlit as st
    
    if title:
        st.write(f"**{title}**")
    if caption:
        st.caption(caption)
    
    options_list = list(available_models)
    
    selected = searchable_model_selector(
        available_models=options_list,
        key_prefix=key_prefix,
        max_selections=max_selections,
        help_text=help_text
    )
    
    other_text = None
    if selected and "Other" in selected:
        other_text = st.text_area(
            f"Please specify other {key_prefix}:",
            key=f"{key_prefix}_other_input"
        )
    
    return selected, other_text

def searchable_dropdown_selector(available_models, key_prefix="model", max_selections=10, help_text=None):
    """
    A searchable dropdown selector where selected models appear as tags in the search bar
    
    Args:
        available_models (list): List of available model options to choose from
        key_prefix (str): Prefix for session state keys to avoid conflicts
        max_selections (int): Maximum number of models that can be selected
        help_text (str): Help text to display with the selector
    
    Returns:
        list: List of selected models
    """
    
    def on_input_change():
        current_input = st.session_state[f"{key_prefix}_text_input"].strip()
        st.session_state[f"{key_prefix}_current_input"] = current_input
        
        if current_input:
            input_lower = current_input.lower()
            
            # Find exact matches first
            exact_matches = [model for model in available_models 
                            if input_lower in model.lower() 
                            and model not in st.session_state[f"{key_prefix}_selections"]]
            
            if not exact_matches:
                # Fall back to close matches if no exact matches
                close_matches = get_close_matches(current_input, available_models, n=10, cutoff=0.4)
                suggestions = [match for match in close_matches 
                              if match not in st.session_state[f"{key_prefix}_selections"]]
            else:
                # Sort exact matches by length (shorter first) and alphabetically
                suggestions = sorted(exact_matches, key=lambda x: (len(x), x))[:10]
            
            st.session_state[f"{key_prefix}_suggestions"] = suggestions
        else:
            # Show popular models when no input
            popular_models = [model for model in available_models[:20] 
                             if model not in st.session_state[f"{key_prefix}_selections"] and model != "Other"]
            st.session_state[f"{key_prefix}_suggestions"] = popular_models
    
    def add_selection(model_name):
        if model_name and model_name not in st.session_state[f"{key_prefix}_selections"]:
            if len(st.session_state[f"{key_prefix}_selections"]) < max_selections:
                st.session_state[f"{key_prefix}_selections"].append(model_name)
                st.session_state[f"{key_prefix}_current_input"] = ""
                st.session_state[f"{key_prefix}_text_input"] = ""
                st.rerun()
            else:
                st.warning(f"Maximum of {max_selections} models can be selected.")
    
    def remove_selection(index):
        if 0 <= index < len(st.session_state[f"{key_prefix}_selections"]):
            st.session_state[f"{key_prefix}_selections"].pop(index)
            st.rerun()
    
    # Initialize session state
    if f"{key_prefix}_selections" not in st.session_state:
        st.session_state[f"{key_prefix}_selections"] = []
    
    if f"{key_prefix}_current_input" not in st.session_state:
        st.session_state[f"{key_prefix}_current_input"] = ""
    
    if f"{key_prefix}_suggestions" not in st.session_state:
        # Show popular models initially
        popular_models = [model for model in available_models[:20] 
                         if model != "Other"]
        st.session_state[f"{key_prefix}_suggestions"] = popular_models
    
    # Display selected models as tags above the search box
    if st.session_state[f"{key_prefix}_selections"]:
        st.write("**Selected:**")
        
        # Create a container for the tags
        tag_container = st.container()
        with tag_container:
            # Display tags in rows of 3
            selections = st.session_state[f"{key_prefix}_selections"]
            for i in range(0, len(selections), 3):
                cols = st.columns(3)
                for j, selection in enumerate(selections[i:i+3]):
                    with cols[j]:
                        # Create a tag-like button with remove functionality
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.button(
                                f"🏷️ {selection}",
                                key=f"{key_prefix}_tag_{i+j}",
                                disabled=True,
                                use_container_width=True
                            )
                        with col2:
                            if st.button("✕", key=f"{key_prefix}_remove_{i+j}", help="Remove"):
                                remove_selection(i+j)
        
        st.markdown("---")
    
    # Search input
    search_placeholder = f"Search AI systems... ({len(st.session_state[f'{key_prefix}_selections'])}/{max_selections} selected)"
    
    current_input = st.text_input(
        "",
        key=f"{key_prefix}_text_input",
        value=st.session_state[f"{key_prefix}_current_input"],
        on_change=on_input_change,
        placeholder=search_placeholder,
        help=help_text,
        disabled=len(st.session_state[f"{key_prefix}_selections"]) >= max_selections
    )
    
    # Show max selections warning
    if len(st.session_state[f"{key_prefix}_selections"]) >= max_selections:
        st.warning(f"Maximum of {max_selections} models selected.")
        return st.session_state[f"{key_prefix}_selections"]
    
    # Display suggestions as dropdown-style options
    suggestions = st.session_state[f"{key_prefix}_suggestions"]
    if suggestions:
        if current_input:
            st.caption(f"Found {len(suggestions)} matches - click to select:")
        else:
            st.caption("Popular AI systems - click to select:")
        
        # Display suggestions in a more compact dropdown-like format
        for i, suggestion in enumerate(suggestions[:8]):  # Limit to 8 suggestions
            if st.button(
                f"➕ {suggestion}", 
                key=f"{key_prefix}_suggestion_{i}",
                use_container_width=True
            ):
                add_selection(suggestion)
    
    elif current_input and not suggestions:
        st.write("No matching models found.")
        
        # Allow custom entry
        if st.button(f"➕ Add '{current_input}' as custom entry", key=f"{key_prefix}_add_custom"):
            add_selection(current_input)
    
    return st.session_state[f"{key_prefix}_selections"]