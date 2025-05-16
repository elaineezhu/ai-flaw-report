import streamlit as st

def handle_other_option(selection, options_list, label="Please specify other:"):
    """Reusable function to handle "Other" option in any selection component
    
    Args:
        selection: Current selection (list for multiselect, string for selectbox/radio)
        options_list: List of selected options or single selection
        label: Label for the text input field
        
    Returns:
        String with user-specified value if "Other" is selected, empty string otherwise
    """
    if isinstance(selection, list):
        if "Other" in selection:
            return st.text_area(label)
    else: # selectbox or radio (string)
        if selection == "Other":
            return st.text_area(label)
    
    return ""