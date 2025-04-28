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