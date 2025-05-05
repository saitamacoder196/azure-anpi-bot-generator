"""
State management for the Streamlit application.
This module initializes and manages the application's session state.
"""
import streamlit as st

def initialize_session_state():
    """Initialize all required session state variables"""
    
    # Main script storage
    if 'generated_scripts' not in st.session_state:
        st.session_state['generated_scripts'] = {
            "environment_vars": "",
            "resource_group": "",
            "networking": "",
            "app_service": "",
            "data_ai_services": "",
            "api_management": "",
            "web_app": "",
            "bot_service": "",
            "teams_integration": "",
            "network_verification": "",
            "complete_script": ""
        }

    # UI state
    if 'selected_section' not in st.session_state:
        st.session_state['selected_section'] = "Complete Script"

    if 'script_generated' not in st.session_state:
        st.session_state['script_generated'] = False

    if 'checklist_state' not in st.session_state:
        st.session_state['checklist_state'] = {}
        
    # JWT key state
    if 'jwt_secret_key' not in st.session_state:
        st.session_state['jwt_secret_key'] = "Ch-GrTBdux']sl|Jspf]C8;#Hn\\o~3[~gyMQ[t!R"
    
    # Make sure sidebar_values is initialized
    if 'sidebar_values' not in st.session_state:
        st.session_state['sidebar_values'] = {
            'env': 'dev',
            'subscription_id': 'your-subscription-id',
            'location': 'japaneast',
            'ms_app_id': 'your-bot-app-id',
            'ms_app_password': 'your-bot-app-password',
            'ms_app_tenant_id': 'your-tenant-id'
        }
    
    # Initialize tab settings storage
    if 'tab_settings' not in st.session_state:
        st.session_state['tab_settings'] = {
            'basic_resources': {},
            'networking': {},
            'app_service': {},
            'data_ai': {},
            'api_management': {},
            'teams_integration': {},
            'cicd': {}  # Add this line
        }


        
    # Initialize state for file upload visibility
    for tab in ['basic', 'networking', 'app_service', 'data_ai', 'api_mgmt', 'teams']:
        uploader_key = f'show_{tab}_uploader'
        if uploader_key not in st.session_state:
            st.session_state[uploader_key] = False

def update_generated_scripts(scripts_dict):
    """Update the generated scripts in session state"""
    st.session_state.generated_scripts = scripts_dict
    st.session_state.script_generated = True

def update_jwt_secret(new_secret):
    """Update the JWT secret key in session state"""
    st.session_state['jwt_secret_key'] = new_secret

def update_sidebar_values(values_dict):
    """Update the sidebar values in session state"""
    st.session_state['sidebar_values'] = values_dict
    
def save_tab_settings(tab_name, settings_dict):
    """
    Save settings for a specific tab to session state
    
    Args:
        tab_name (str): The name of the tab (e.g., 'basic_resources', 'networking')
        settings_dict (dict): Dictionary containing the tab's settings
    """
    if 'tab_settings' not in st.session_state:
        st.session_state['tab_settings'] = {}
    
    st.session_state['tab_settings'][tab_name] = settings_dict
    
def load_tab_settings(tab_name):
    """
    Load settings for a specific tab from session state
    
    Args:
        tab_name (str): The name of the tab to load settings for
        
    Returns:
        dict: The saved settings for the tab or an empty dict if none exist
    """
    if 'tab_settings' not in st.session_state or tab_name not in st.session_state['tab_settings']:
        return {}
    
    return st.session_state['tab_settings'][tab_name]
    
def get_all_settings():
    """
    Get all settings from all tabs and the sidebar
    
    Returns:
        dict: Complete settings dictionary with all tabs' settings
    """
    if 'tab_settings' not in st.session_state:
        st.session_state['tab_settings'] = {}
        
    # Combine all settings
    all_settings = {
        'sidebar': st.session_state.get('sidebar_values', {}),
        'tabs': st.session_state['tab_settings']
    }
    
    return all_settings
    
def load_all_settings(settings_dict):
    """
    Load complete settings into session state
    
    Args:
        settings_dict (dict): Dictionary containing all settings
    """
    # Update sidebar values
    if 'sidebar' in settings_dict:
        st.session_state['sidebar_values'] = settings_dict['sidebar']
        
    # Update tab settings
    if 'tabs' in settings_dict:
        st.session_state['tab_settings'] = settings_dict['tabs']