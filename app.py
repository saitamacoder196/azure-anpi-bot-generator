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
    """Main application entry point with updated tab order and export/import functionality"""
    # Initialize session state variables
    initialize_session_state()
    
    # Configure the page
    ui.configure_page()
    
    # Create sidebar
    sidebar_values = ui.create_sidebar()
    st.session_state.sidebar_values = sidebar_values
    
    # Create main tabs - reordered to emphasize APIM first
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Basic Resources", 
        "API Management",  # Moved up in the order
        "Networking", 
        "App Service", 
        "Data & AI", 
        "Teams Integration",
        "Deployment Checklist"
    ])
    
    # Populate the tabs with input fields
    with tab1:
        basic_resources = ui.create_basic_resources_tab()
    
    with tab2:
        api_management = ui.create_api_management_tab()
    
    with tab3:
        networking = ui.create_networking_tab()
    
    with tab4:
        app_service = ui.create_app_service_tab()
    
    with tab5:
        data_ai = ui.create_data_ai_tab()
    
    with tab6:
        teams_integration = ui.create_teams_integration_tab()
    
    with tab7:
        ui.create_deployment_checklist_tab()
    
    # Create a button area with a more prominent design for generating commands
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col2:
        # Generate CLI commands button with custom styling
        st.markdown("""
        <style>
        .generate-cli-button {
            background-color: #107C10; 
            color: white;
            padding: 12px 20px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
            display: block;
            margin: 20px auto;
        }
        .generate-cli-button:hover {
            background-color: #0B5D0B;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Generate CLI commands button
        if st.button("📜 Generate Azure CLI Commands", key="generate_cli_button", use_container_width=True):
            # Make sure we have the latest values from all sources
            sidebar_values = st.session_state.sidebar_values
            jwt_secret = st.session_state.get('jwt_secret_key', '')
            
            # Create a comprehensive params dictionary with all required parameters
            params = {
                # Environment Settings from sidebar
                'env': sidebar_values.get('env', 'dev'),
                'subscription_id': sidebar_values.get('subscription_id', ''),
                'location': sidebar_values.get('location', 'japaneast'),
                
                # Bot Settings from sidebar
                'ms_app_id': sidebar_values.get('ms_app_id', ''),
                'ms_app_password': sidebar_values.get('ms_app_password', ''),
                'ms_app_tenant_id': sidebar_values.get('ms_app_tenant_id', ''),
                
                # JWT Secret Key
                'jwt_secret_key': jwt_secret,
                
                # Settings from all tabs
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
            
            # Show success message with icon
            st.success("✅ Azure CLI commands generated successfully! Scroll down to view.")
    
    # Display output section if scripts have been generated
    ui.display_output_section(sidebar_values['env'])
    
    # Create footer
    ui.create_footer()

if __name__ == "__main__":
    main()