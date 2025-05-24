import streamlit as st
from typing import List

def get_policy_links_for_systems(selected_systems: List[str]) -> str:
    """Generate policy links for selected AI systems"""
    if not selected_systems:
        return ""
    
    links = []
    processed_companies = set()
    
    for system in selected_systems:
        if system == "Other":
            continue
            
        if '/' in system:
            hf_url = f"https://huggingface.co/{system}"
            links.append(f"• [{system} Model Card]({hf_url})")
            
            company = extract_company_from_model_name(system)
            if company and company not in processed_companies:
                company_links = get_company_policy_links(company)
                if company_links:
                    links.extend(company_links)
                    processed_companies.add(company)
        else:
            company = extract_company_from_model_name(system)
            if company and company not in processed_companies:
                company_links = get_company_policy_links(company)
                if company_links:
                    links.extend(company_links)
                    processed_companies.add(company)
    
    return "\n".join(links) if links else ""

def extract_company_from_model_name(model_name: str) -> str:
    """Extract company name from model name"""
    model_lower = model_name.lower()
    
    if '/' in model_name:
        username = model_name.split('/')[0].lower()
        username_mapping = {
            'openai': 'OpenAI',
            'google': 'Google', 
            'microsoft': 'Microsoft',
            'meta-llama': 'Meta',
            'facebook': 'Meta',
            'anthropic': 'Anthropic'
        }
        if username in username_mapping:
            return username_mapping[username]
    
    if any(term in model_lower for term in ['gpt', 'dall-e', 'whisper', "o1", "o3"]):
        return "OpenAI"
    elif any(term in model_lower for term in ['claude']):
        return "Anthropic"
    elif any(term in model_lower for term in ['gemini', 'palm', 'bard']):
        return "Google"
    elif any(term in model_lower for term in ['copilot']):
        return "Microsoft"
    elif any(term in model_lower for term in ['llama']):
        return "Meta"
    
    return None

def get_company_policy_links(company: str) -> List[str]:
    """Get policy links for a specific company"""
    company_policies = {
        "OpenAI": [
            "• [OpenAI Usage Policies](https://openai.com/policies/usage-policies/)",
            "• [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/)"
        ],
        "Anthropic": [
            "• [Anthropic Usage Policy](https://www.anthropic.com/usage-policy)",
            "• [Anthropic Terms of Service](https://www.anthropic.com/terms)"
        ],
        "Google": [
            "• [Google AI Use Policy](https://policies.google.com/terms/generative-ai/use-policy)",
            "• [Google Terms of Service](https://policies.google.com/terms)"
        ],
        "Microsoft": [
            "• [Microsoft Responsible AI](https://www.microsoft.com/en-us/ai/responsible-ai)",
            "• [Microsoft Services Agreement](https://www.microsoft.com/en-us/servicesagreement)"
        ],
        "Meta": [
            "• [Meta AI Responsible Use](https://ai.meta.com/static-resource/responsible-use-guide/)",
            "• [Meta Terms of Service](https://www.facebook.com/terms/)"
        ]
    }
    
    return company_policies.get(company, [])

def display_policy_links(selected_systems: List[str]):
    """Display policy links for selected systems"""
    if not selected_systems or selected_systems == ["Other"]:
        return
    
    policy_links = get_policy_links_for_systems(selected_systems)
    
    if policy_links:
        st.markdown("**See list of model's policies here:**")
        formatted_links = policy_links.replace("\n", "  \n")
        st.markdown(formatted_links)