"""
Azure ANPI Bot Infrastructure Generator - Main Application
This Streamlit application generates Azure CLI commands for deploying ANPI Bot infrastructure.
"""
import streamlit as st
from state import initialize_session_state, update_generated_scripts
from utils import generate_jwt_secret
from generators import generate_all_scripts
import ui

def main():
    """Main application entry point"""
    # Initialize session state variables
    initialize_session_state()
    
    # Configure the page
    ui.configure_page()
    
    # Create sidebar
    sidebar_values = ui.create_sidebar()
    st.session_state.sidebar_values = sidebar_values
    
    # Create main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Basic Resources", 
        "Networking", 
        "App Service", 
        "Data & AI", 
        "API Management", 
        "Teams Integration",
        "Deployment Checklist"
    ])
    
    # Populate the tabs with input fields
    with tab1:
        basic_resources = ui.create_basic_resources_tab()
    
    with tab2:
        networking = ui.create_networking_tab()
    
    with tab3:
        app_service = ui.create_app_service_tab()
    
    with tab4:
        data_ai = ui.create_data_ai_tab()
    
    with tab5:
        api_management = ui.create_api_management_tab()
    
    with tab6:
        teams_integration = ui.create_teams_integration_tab()
    
    with tab7:
        ui.create_deployment_checklist_tab()
    
    # Generate CLI commands button
    if st.button("Generate CLI Commands"):
        # Combine all parameters
        params = {
            **sidebar_values,
            **basic_resources,
            **networking,
            **app_service,
            **data_ai,
            **api_management,
            **teams_integration
        }
        
        # Generate all scripts
        generated_scripts = generate_all_scripts(params)
        
        # Update session state
        update_generated_scripts(generated_scripts)
    
    # Display output section if scripts have been generated
    ui.display_output_section(sidebar_values['env'])
    
    # Create footer
    ui.create_footer()

if __name__ == "__main__":
    main()