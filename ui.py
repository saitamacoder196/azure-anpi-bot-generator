"""
UI components for the Streamlit application.
"""
from datetime import datetime
import streamlit as st
from utils import get_markdown_download_link, generate_jwt_secret, create_markdown_content, get_settings_download_link, get_yaml_download_link, parse_uploaded_settings, get_full_settings_download_link
from state import update_jwt_secret

def configure_page():
    """Configure the Streamlit page settings with custom CSS"""
    st.set_page_config(page_title="Azure ANPI Bot Infrastructure Generator", layout="wide")
    
    # Load custom CSS from file
    with open('style.css', 'r') as f:
        css = f.read()
    
    # Apply custom styling
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    
    st.title("Azure ANPI Bot Infrastructure Deployment Generator")
    st.markdown("This tool helps you generate Azure CLI commands for deploying the ANPI Bot infrastructure. Fill in the parameters below and copy the generated commands.")
    
    # Add info about export/import functionality
    st.info("""
    💾 **Export/Import Settings**: You can export and import settings from each tab or the entire application.
    - Use the 'Export Tab Settings' button in each tab to save current tab settings
    - Use the 'Import Tab Settings' button to load saved settings for a specific tab
    - Use the sidebar's 'Export/Import Settings' section to save/load all application settings
    """)
    

def create_sidebar():
    """Create and configure the sidebar with environment settings and export/import functionality"""
    with st.sidebar:
        st.header("Environment Settings")
        
        # Add export/import section at the top
        with st.expander("Export/Import Settings", expanded=False):
            # Export all settings (complete application settings)
            if st.button("Export All Settings"):
                from state import get_all_settings
                # Get all settings from session state
                all_settings = get_all_settings()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_full_settings_download_link(
                    all_settings, 
                    f"anpi_full_settings_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("All settings exported successfully!")
            
            # Export just environment settings (legacy support)
            if st.button("Export Environment Settings"):
                if 'sidebar_values' in st.session_state:
                    # Combine environment and bot settings
                    export_settings = {
                        'environment': {
                            'env': st.session_state.sidebar_values.get('env', 'dev'),
                            'subscription_id': st.session_state.sidebar_values.get('subscription_id', ''),
                            'location': st.session_state.sidebar_values.get('location', 'japaneast')
                        },
                        'bot': {
                            'ms_app_id': st.session_state.sidebar_values.get('ms_app_id', ''),
                            'ms_app_password': st.session_state.sidebar_values.get('ms_app_password', ''),
                            'ms_app_tenant_id': st.session_state.sidebar_values.get('ms_app_tenant_id', '')
                        }
                    }
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    download_link = get_settings_download_link(
                        export_settings, 
                        f"anpi_env_settings_{timestamp}.json"
                    )
                    st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("No settings available to export")
            
            # Import settings
            st.write("Import Settings:")
            uploaded_file = st.file_uploader("Choose a settings file", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    if st.button("Apply Imported Settings"):
                        # Detect the settings format
                        if 'sidebar' in settings and 'tabs' in settings:
                            # New format (complete settings)
                            from state import load_all_settings
                            load_all_settings(settings)
                            st.success("All settings imported successfully!")
                            st.rerun()
                        elif 'environment' in settings or 'bot' in settings:
                            # Old format (just environment settings)
                            # Create sidebar_values if it doesn't exist
                            if 'sidebar_values' not in st.session_state:
                                st.session_state.sidebar_values = {}
                            
                            # Update environment settings
                            if 'environment' in settings:
                                env_settings = settings['environment']
                                st.session_state.sidebar_values['env'] = env_settings.get('env', 'dev')
                                st.session_state.sidebar_values['subscription_id'] = env_settings.get('subscription_id', '')
                                st.session_state.sidebar_values['location'] = env_settings.get('location', 'japaneast')
                            
                            # Update bot settings
                            if 'bot' in settings:
                                bot_settings = settings['bot']
                                st.session_state.sidebar_values['ms_app_id'] = bot_settings.get('ms_app_id', '')
                                st.session_state.sidebar_values['ms_app_password'] = bot_settings.get('ms_app_password', '')
                                st.session_state.sidebar_values['ms_app_tenant_id'] = bot_settings.get('ms_app_tenant_id', '')
                            
                            st.success("Environment settings imported successfully!")
                            st.rerun()
                        else:
                            st.error("Unknown settings format. Please use a valid settings file.")
                else:
                    st.error("Failed to parse the uploaded file. Please ensure it's a valid JSON file.")
        
        # Regular sidebar inputs
        env = st.selectbox("Environment", ["dev", "test", "preprd", "prod"], 
                          index=["dev", "test", "preprd", "prod"].index(
                              st.session_state.sidebar_values.get('env', 'dev')) if 'sidebar_values' in st.session_state else 0)
        
        subscription_id = st.text_input(
            "Azure Subscription ID", 
            value=st.session_state.sidebar_values.get('subscription_id', 'your-subscription-id') if 'sidebar_values' in st.session_state else 'your-subscription-id')
        
        location = st.selectbox(
            "Azure Region", 
            ["japaneast", "eastus", "westus", "northeurope", "southeastasia"],
            index=["japaneast", "eastus", "westus", "northeurope", "southeastasia"].index(
                st.session_state.sidebar_values.get('location', 'japaneast')) if 'sidebar_values' in st.session_state else 0)
        
        st.header("Bot Settings")
        ms_app_id = st.text_input(
            "Bot App ID", 
            value=st.session_state.sidebar_values.get('ms_app_id', 'your-bot-app-id') if 'sidebar_values' in st.session_state else 'your-bot-app-id')
        
        ms_app_password = st.text_input(
            "Bot App Password", 
            value=st.session_state.sidebar_values.get('ms_app_password', 'your-bot-app-password') if 'sidebar_values' in st.session_state else 'your-bot-app-password', 
            type="password")
        
        ms_app_tenant_id = st.text_input(
            "Tenant ID", 
            value=st.session_state.sidebar_values.get('ms_app_tenant_id', 'your-tenant-id') if 'sidebar_values' in st.session_state else 'your-tenant-id')
        
        # Save values to sidebar_values dictionary
        sidebar_values = {
            'env': env,
            'subscription_id': subscription_id, 
            'location': location,
            'ms_app_id': ms_app_id,
            'ms_app_password': ms_app_password,
            'ms_app_tenant_id': ms_app_tenant_id
        }
        
        return sidebar_values
    
def create_basic_resources_tab():
    """Create the Basic Resources tab with export/import functionality"""
    st.header("Resource Group and Basic Settings")
    env = st.session_state.sidebar_values['env']
    
    # Add export/import functionality for this tab
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Export Tab Settings", key="export_basic"):
            # Get the current tab settings from session state or default values
            from state import load_tab_settings
            tab_settings = load_tab_settings('basic_resources')
            if not tab_settings:
                st.warning("No settings saved for this tab yet.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_settings_download_link(
                    tab_settings, 
                    f"anpi_basic_resources_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("Basic resources settings exported!")
    
    with col2:
        if st.button("Import Tab Settings", key="import_basic_button"):
            st.session_state['show_basic_uploader'] = True
    
    with col3:
        if st.session_state.get('show_basic_uploader', False):
            uploaded_file = st.file_uploader("Choose a settings file", key="basic_uploader", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    # Apply the imported settings to session state
                    from state import save_tab_settings
                    save_tab_settings('basic_resources', settings)
                    st.success("Basic resources settings imported!")
                    st.rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('basic_resources')
    
    # Set default values, using saved settings if available
    default_rg_name = saved_settings.get('rg_name', f"itz-{env}-jpe-001")
    default_anpi_tag = saved_settings.get('anpi_tag', f"Project=AnpiBot Environment={env.capitalize()}")
    default_shared_tag = saved_settings.get('shared_tag', f"Environment={env.capitalize()} Project=ITZ-Chatbot")
    default_api_base_url = saved_settings.get('api_base_url', "https://api-test.fjpservice.net")
    default_timeout_minutes = saved_settings.get('timeout_minutes', 30)
    default_jwt_issuer = saved_settings.get('jwt_issuer', "https://api.botframework.com")
    default_jwt_expiry_minutes = saved_settings.get('jwt_expiry_minutes', 60)
    
    # Create input fields with default values
    rg_name = st.text_input("Resource Group Name", value=default_rg_name)
    anpi_tag = st.text_input("ANPI Tags", value=default_anpi_tag)
    shared_tag = st.text_input("Shared Tags", value=default_shared_tag)
    api_base_url = st.text_input("API Base URL", value=default_api_base_url)
    timeout_minutes = st.number_input("Timeout Minutes", value=default_timeout_minutes, min_value=1, max_value=60)
    jwt_issuer = st.text_input("JWT Issuer", value=default_jwt_issuer)
    
    # JWT Secret Key with generate button
    col1, col2 = st.columns([3, 1])
    with col1:
        # Link the text input to session state variable
        jwt_secret_key = st.text_input("JWT Secret Key", 
                                      value=st.session_state['jwt_secret_key'], 
                                      type="password",
                                      key="jwt_key_input")
        # Update the session state when input changes
        st.session_state['jwt_secret_key'] = jwt_secret_key
        
    with col2:
        if st.button("Generate JWT Key"):
            # Update the session state
            new_key = generate_jwt_secret()
            update_jwt_secret(new_key)
            # Force rerun
            st.rerun()
    
    jwt_expiry_minutes = st.number_input("JWT Expiry Minutes", value=default_jwt_expiry_minutes, min_value=1, max_value=1440)
    
    # Create a dictionary with the current settings
    current_settings = {
        'rg_name': rg_name,
        'anpi_tag': anpi_tag,
        'shared_tag': shared_tag,
        'api_base_url': api_base_url,
        'timeout_minutes': timeout_minutes,
        'jwt_issuer': jwt_issuer,
        'jwt_secret_key': jwt_secret_key,
        'jwt_expiry_minutes': jwt_expiry_minutes
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('basic_resources', current_settings)
    
    return current_settings

def create_networking_tab():
    """Create the Networking tab with export/import functionality"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Networking Configuration")
    
    # Add export/import functionality for this tab
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Export Tab Settings", key="export_networking"):
            # Get the current tab settings from session state or default values
            from state import load_tab_settings
            tab_settings = load_tab_settings('networking')
            if not tab_settings:
                st.warning("No settings saved for this tab yet.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_settings_download_link(
                    tab_settings, 
                    f"anpi_networking_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("Networking settings exported!")
    
    with col2:
        if st.button("Import Tab Settings", key="import_networking_button"):
            st.session_state['show_networking_uploader'] = True
    
    with col3:
        if st.session_state.get('show_networking_uploader', False):
            uploaded_file = st.file_uploader("Choose a settings file", key="networking_uploader", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    # Apply the imported settings to session state
                    from state import save_tab_settings
                    save_tab_settings('networking', settings)
                    st.success("Networking settings imported!")
                    st.rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('networking')
    
    # Set default values, using saved settings if available
    default_vnet_name = saved_settings.get('vnet_name', f"vnet-itz-{env}-jpe-001")
    default_vnet_address_prefix = saved_settings.get('vnet_address_prefix', "10.0.0.0/16")
    default_subnet_name = saved_settings.get('subnet_name', f"snet-itz-{env}-jpe-001")
    default_subnet_prefix = saved_settings.get('subnet_prefix', "10.0.1.0/24")
    default_pip_name = saved_settings.get('pip_name', f"pip-itz-anpi-{env}-jpe-001")
    default_agw_name = saved_settings.get('agw_name', f"agw-itz-{env}-jpe-001")
    default_waf_name = saved_settings.get('waf_name', f"waf-itz-{env}-jpe-001")
    
    # Create input fields with default values
    vnet_name = st.text_input("Virtual Network Name", value=default_vnet_name)
    vnet_address_prefix = st.text_input("VNet Address Prefix", value=default_vnet_address_prefix)
    
    st.subheader("Subnets")
    subnet_name = st.text_input("Subnet Name", value=default_subnet_name)
    subnet_prefix = st.text_input("Subnet Address Prefix", value=default_subnet_prefix)
    
    st.subheader("Application Gateway")
    pip_name = st.text_input("Public IP Name", value=default_pip_name)
    agw_name = st.text_input("Application Gateway Name", value=default_agw_name)
    waf_name = st.text_input("WAF Policy Name", value=default_waf_name)
    
    # Create a dictionary with the current settings
    current_settings = {
        'vnet_name': vnet_name,
        'vnet_address_prefix': vnet_address_prefix,
        'subnet_name': subnet_name,
        'subnet_prefix': subnet_prefix,
        'pip_name': pip_name,
        'agw_name': agw_name,
        'waf_name': waf_name
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('networking', current_settings)
    
    return current_settings

def create_app_service_tab():
    """Create the App Service tab with export/import functionality"""
    env = st.session_state.sidebar_values['env']
    
    st.header("App Service Configuration")
    
    # Add export/import functionality for this tab
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Export Tab Settings", key="export_app_service"):
            # Get the current tab settings from session state or default values
            from state import load_tab_settings
            tab_settings = load_tab_settings('app_service')
            if not tab_settings:
                st.warning("No settings saved for this tab yet.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_settings_download_link(
                    tab_settings, 
                    f"anpi_app_service_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("App Service settings exported!")
    
    with col2:
        if st.button("Import Tab Settings", key="import_app_service_button"):
            st.session_state['show_app_service_uploader'] = True
    
    with col3:
        if st.session_state.get('show_app_service_uploader', False):
            uploaded_file = st.file_uploader("Choose a settings file", key="app_service_uploader", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    # Apply the imported settings to session state
                    from state import save_tab_settings
                    save_tab_settings('app_service', settings)
                    st.success("App Service settings imported!")
                    st.rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('app_service')
    
    # Set default values, using saved settings if available
    default_asp_name = saved_settings.get('asp_name', f"asp-itz-{env}-001")
    default_asp_sku = saved_settings.get('asp_sku', "B1")
    default_app_name = saved_settings.get('app_name', f"app-itz-anpi-{env}-001")
    default_app_runtime = saved_settings.get('app_runtime', "DOTNETCORE|6.0")
    default_appinsights_name = saved_settings.get('appinsights_name', f"appi-itz-anpi-{env}-jpe-001")
    default_bot_name = saved_settings.get('bot_name', f"bot-itz-anpi-{env}")
    
    # Create input fields with default values
    asp_name = st.text_input("App Service Plan Name", value=default_asp_name)
    asp_sku = st.selectbox("App Service Plan SKU", ["B1", "S1", "P1V2", "P2V2", "P3V2"], 
                           index=["B1", "S1", "P1V2", "P2V2", "P3V2"].index(default_asp_sku) if default_asp_sku in ["B1", "S1", "P1V2", "P2V2", "P3V2"] else 0)
    
    app_name = st.text_input("Web App Name", value=default_app_name)
    runtime_options = ["DOTNETCORE|6.0", "DOTNETCORE|7.0", "DOTNETCORE|8.0", "NODE|14-lts", "NODE|16-lts"]
    app_runtime = st.selectbox("App Runtime", runtime_options,
                              index=runtime_options.index(default_app_runtime) if default_app_runtime in runtime_options else 0)
    
    st.subheader("Application Insights")
    appinsights_name = st.text_input("Application Insights Name", value=default_appinsights_name)
    
    bot_name = st.text_input("Bot Service Name", value=default_bot_name)
    
    # Create a dictionary with the current settings
    current_settings = {
        'asp_name': asp_name,
        'asp_sku': asp_sku,
        'app_name': app_name,
        'app_runtime': app_runtime,
        'appinsights_name': appinsights_name,
        'bot_name': bot_name
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('app_service', current_settings)
    
    return current_settings

def create_data_ai_tab():
    """Create the Data and AI Services tab with export/import functionality"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Data and AI Services")
    
    # Add export/import functionality for this tab
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Export Tab Settings", key="export_data_ai"):
            # Get the current tab settings from session state or default values
            from state import load_tab_settings
            tab_settings = load_tab_settings('data_ai')
            if not tab_settings:
                st.warning("No settings saved for this tab yet.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_settings_download_link(
                    tab_settings, 
                    f"anpi_data_ai_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("Data & AI settings exported!")
    
    with col2:
        if st.button("Import Tab Settings", key="import_data_ai_button"):
            st.session_state['show_data_ai_uploader'] = True
    
    with col3:
        if st.session_state.get('show_data_ai_uploader', False):
            uploaded_file = st.file_uploader("Choose a settings file", key="data_ai_uploader", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    # Apply the imported settings to session state
                    from state import save_tab_settings
                    save_tab_settings('data_ai', settings)
                    st.success("Data & AI settings imported!")
                    st.rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('data_ai')
    
    # Set default values, using saved settings if available
    default_kv_name = saved_settings.get('kv_name', f"kv-itz-{env}-jpe-001")
    default_cosmos_name = saved_settings.get('cosmos_name', f"cosmos-itz-{env}")
    default_cosmos_db_name = saved_settings.get('cosmos_db_name', "AnpiDb")
    default_openai_name = saved_settings.get('openai_name', f"oai-itz-{env}")
    default_openai_model = saved_settings.get('openai_model', "gpt-4o-mini")
    default_model_version = saved_settings.get('model_version', "2024-07-18")
    default_embedding_model = saved_settings.get('embedding_model', "text-embedding-ada-002")
    default_embedding_model_version = saved_settings.get('embedding_model_version', 2)
    default_search_name = saved_settings.get('search_name', f"srch-itz-{env}")
    default_search_sku = saved_settings.get('search_sku', "Basic")
    default_search_index_name = saved_settings.get('search_index_name', "anpi-knowledge")
    default_semantic_config_name = saved_settings.get('semantic_config_name', "my-semantic-config")
    
    # Create input fields with default values
    st.subheader("Key Vault")
    kv_name = st.text_input("Key Vault Name", value=default_kv_name)
    
    st.subheader("Cosmos DB")
    cosmos_name = st.text_input("Cosmos DB Account Name", value=default_cosmos_name)
    cosmos_db_name = st.text_input("Cosmos DB Database Name", value=default_cosmos_db_name)
    
    st.subheader("Azure OpenAI")
    openai_name = st.text_input("OpenAI Service Name", value=default_openai_name)
    openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-35-turbo", "gpt-4"]
    openai_model = st.selectbox("OpenAI Model", openai_models,
                               index=openai_models.index(default_openai_model) if default_openai_model in openai_models else 0)
    model_version = st.text_input("Model Version", value=default_model_version)
    embedding_model = st.text_input("Embedding Model", value=default_embedding_model)
    embedding_model_version = st.number_input("Embedding Model Version", value=default_embedding_model_version, min_value=1)
    
    st.subheader("Azure Search")
    search_name = st.text_input("Search Service Name", value=default_search_name)
    search_skus = ["Basic", "Standard", "Standard2", "Standard3"]
    search_sku = st.selectbox("Search SKU", search_skus,
                             index=search_skus.index(default_search_sku) if default_search_sku in search_skus else 0)
    search_index_name = st.text_input("Search Index Name", value=default_search_index_name)
    semantic_config_name = st.text_input("Semantic Config Name", value=default_semantic_config_name)
    
    # Create a dictionary with the current settings
    current_settings = {
        'kv_name': kv_name,
        'cosmos_name': cosmos_name,
        'cosmos_db_name': cosmos_db_name,
        'openai_name': openai_name,
        'openai_model': openai_model,
        'model_version': model_version,
        'embedding_model': embedding_model,
        'embedding_model_version': embedding_model_version,
        'search_name': search_name,
        'search_sku': search_sku,
        'search_index_name': search_index_name,
        'semantic_config_name': semantic_config_name
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('data_ai', current_settings)
    
    return current_settings

def create_api_management_tab():
    """Create the API Management tab with fields from ARM template and export/import functionality"""
    st.header("API Management")
    
    # Add export/import functionality for this tab
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Export Tab Settings", key="export_api_mgmt"):
            # Get the current tab settings from session state or default values
            from state import load_tab_settings
            tab_settings = load_tab_settings('api_management')
            if not tab_settings:
                st.warning("No settings saved for this tab yet.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_settings_download_link(
                    tab_settings, 
                    f"anpi_api_management_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("API Management settings exported!")
    
    with col2:
        if st.button("Import Tab Settings", key="import_api_mgmt_button"):
            st.session_state['show_api_mgmt_uploader'] = True
    
    with col3:
        if st.session_state.get('show_api_mgmt_uploader', False):
            uploaded_file = st.file_uploader("Choose a settings file", key="api_mgmt_uploader", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    # Apply the imported settings to session state
                    from state import save_tab_settings
                    save_tab_settings('api_management', settings)
                    st.success("API Management settings imported!")
                    st.rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('api_management')
    
    # Set default values, using saved settings if available
    default_apim_name = saved_settings.get('apim_name', "apim-itz")
    default_apim_sku = saved_settings.get('apim_sku', "Consumption")
    default_apim_publisher_email = saved_settings.get('apim_publisher_email', "tuyendhq@fpt.com")
    default_apim_publisher_name = saved_settings.get('apim_publisher_name', "FJP Japan Holding")
    default_api_id = saved_settings.get('api_id', "anpi-bot-api")
    default_api_path = saved_settings.get('api_path', "anpi")
    default_api_display_name = saved_settings.get('api_display_name', "ANPI Bot API")
    default_allowed_origins = saved_settings.get('allowed_origins', '["https://*.fjpservice.net","https://localhost:4200"]')
    
    # Create input fields with default values
    apim_name = st.text_input("API Management Name", value=default_apim_name)
    
    # Updated SKU options to include Consumption per ARM template
    sku_options = ["Consumption", "Developer", "Basic", "Standard", "Premium"]
    apim_sku = st.selectbox("API Management SKU", sku_options,
                           index=sku_options.index(default_apim_sku) if default_apim_sku in sku_options else 0)
    
    # Updated with publisher details from the ARM template
    apim_publisher_email = st.text_input("Publisher Email", value=default_apim_publisher_email)
    apim_publisher_name = st.text_input("Publisher Name", value=default_apim_publisher_name)
    
    api_id = st.text_input("API ID", value=default_api_id)
    api_path = st.text_input("API Path", value=default_api_path)
    api_display_name = st.text_input("API Display Name", value=default_api_display_name)
    
    allowed_origins = st.text_area("Allowed Origins (JSON array)", value=default_allowed_origins)
    
    # Save to session state for yaml generation
    st.session_state['apim_name'] = apim_name
    st.session_state['api_path'] = api_path
    st.session_state['api_id'] = api_id
    st.session_state['api_display_name'] = api_display_name
    
    # Create a dictionary with the current settings
    current_settings = {
        'apim_name': apim_name,
        'apim_sku': apim_sku,
        'apim_publisher_email': apim_publisher_email,
        'apim_publisher_name': apim_publisher_name,
        'api_id': api_id,
        'api_path': api_path,
        'api_display_name': api_display_name,
        'allowed_origins': allowed_origins
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('api_management', current_settings)
    
    return current_settings
    
def create_teams_integration_tab():
    """Create the Teams Integration tab with export/import functionality"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Teams Integration")
    
    # Add export/import functionality for this tab
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Export Tab Settings", key="export_teams"):
            # Get the current tab settings from session state or default values
            from state import load_tab_settings
            tab_settings = load_tab_settings('teams_integration')
            if not tab_settings:
                st.warning("No settings saved for this tab yet.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_link = get_settings_download_link(
                    tab_settings, 
                    f"anpi_teams_integration_{timestamp}.json"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("Teams integration settings exported!")
    
    with col2:
        if st.button("Import Tab Settings", key="import_teams_button"):
            st.session_state['show_teams_uploader'] = True
    
    with col3:
        if st.session_state.get('show_teams_uploader', False):
            uploaded_file = st.file_uploader("Choose a settings file", key="teams_uploader", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    # Apply the imported settings to session state
                    from state import save_tab_settings
                    save_tab_settings('teams_integration', settings)
                    st.success("Teams integration settings imported!")
                    st.rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('teams_integration')
    
    # Set default values, using saved settings if available
    default_teams_app_name = saved_settings.get('teams_app_name', f"ANPI Teams Bot {env.capitalize()}")
    default_teams_redirect_uri = saved_settings.get('teams_redirect_uri', "https://token.botframework.com/.auth/web/redirect")
    
    # Create input fields with default values
    teams_app_name = st.text_input("Teams App Name", value=default_teams_app_name)
    teams_redirect_uri = st.text_input("Teams Redirect URI", value=default_teams_redirect_uri)
    
    # Create a dictionary with the current settings
    current_settings = {
        'teams_app_name': teams_app_name,
        'teams_redirect_uri': teams_redirect_uri
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('teams_integration', current_settings)
    
    return current_settings

def create_deployment_checklist_tab():
    """Create the Deployment Checklist tab with updated order"""
    st.header("Deployment Checklist")
    
    st.subheader("1. Initial Setup")
    if "setup_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["setup_checks"] = [False, False, False]
    
    setup_checks = st.session_state.checklist_state["setup_checks"]
    setup_checks[0] = st.checkbox("☐ Install Azure CLI", value=setup_checks[0], key="check_install_cli")
    setup_checks[1] = st.checkbox("☐ Login to Azure CLI (`az login`)", value=setup_checks[1], key="check_login_cli")
    setup_checks[2] = st.checkbox("☐ Set correct subscription (`az account set --subscription \"$SUBSCRIPTION_ID\"`)", value=setup_checks[2], key="check_set_sub")
    
    st.subheader("2. Resource Group Deployment")
    if "rg_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["rg_checks"] = [False]
    
    rg_checks = st.session_state.checklist_state["rg_checks"]
    rg_checks[0] = st.checkbox("☐ Create Resource Group", value=rg_checks[0], key="check_create_rg")
    
    st.subheader("3. API Management Deployment")
    if "api_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["api_checks"] = [False, False]
    
    api_checks = st.session_state.checklist_state["api_checks"]
    api_checks[0] = st.checkbox("☐ Create API Management Service", value=api_checks[0], key="check_create_apim")
    api_checks[1] = st.checkbox("☐ Configure API in APIM", value=api_checks[1], key="check_config_apim")
    
    st.subheader("4. Networking Deployment")
    if "net_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["net_checks"] = [False, False, False]
    
    net_checks = st.session_state.checklist_state["net_checks"]
    net_checks[0] = st.checkbox("☐ Create Virtual Network and Subnet", value=net_checks[0], key="check_create_vnet")
    net_checks[1] = st.checkbox("☐ Create Public IP Address", value=net_checks[1], key="check_create_pip")
    net_checks[2] = st.checkbox("☐ Create Application Gateway with WAF (pointing to APIM backend)", value=net_checks[2], key="check_create_agw")
    
    st.subheader("5. App Service Deployment")
    if "app_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["app_checks"] = [False, False]
    
    app_checks = st.session_state.checklist_state["app_checks"]
    app_checks[0] = st.checkbox("☐ Create App Service Plan", value=app_checks[0], key="check_create_asp")
    app_checks[1] = st.checkbox("☐ Create Application Insights", value=app_checks[1], key="check_create_appins")
    
    st.subheader("6. Data & AI Services Deployment")
    if "data_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["data_checks"] = [False, False, False, False, False]
    
    data_checks = st.session_state.checklist_state["data_checks"]
    data_checks[0] = st.checkbox("☐ Create Key Vault", value=data_checks[0], key="check_create_kv")
    data_checks[1] = st.checkbox("☐ Create Cosmos DB and Containers", value=data_checks[1], key="check_create_cosmos")
    data_checks[2] = st.checkbox("☐ Create Azure OpenAI Service", value=data_checks[2], key="check_create_openai")
    data_checks[3] = st.checkbox("☐ Deploy OpenAI Models", value=data_checks[3], key="check_deploy_models")
    data_checks[4] = st.checkbox("☐ Create Azure Search Service and Index", value=data_checks[4], key="check_create_search")
    
    # Remove the duplicate API Management section (it was already at position 3)
    
    st.subheader("7. Web App and Bot Service Deployment")
    if "web_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["web_checks"] = [False, False, False, False]
    
    web_checks = st.session_state.checklist_state["web_checks"]
    web_checks[0] = st.checkbox("☐ Create Web App", value=web_checks[0], key="check_create_webapp")
    web_checks[1] = st.checkbox("☐ Store Secrets in Key Vault", value=web_checks[1], key="check_store_secrets")
    web_checks[2] = st.checkbox("☐ Configure Web App Settings", value=web_checks[2], key="check_config_webapp")
    web_checks[3] = st.checkbox("☐ Create Bot Service", value=web_checks[3], key="check_create_bot")
    
    st.subheader("8. Teams Integration")
    if "teams_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["teams_checks"] = [False, False]
    
    teams_checks = st.session_state.checklist_state["teams_checks"]
    teams_checks[0] = st.checkbox("☐ Register Teams App", value=teams_checks[0], key="check_register_teams")
    teams_checks[1] = st.checkbox("☐ Store Teams App Credentials", value=teams_checks[1], key="check_teams_creds")
    
    st.subheader("9. Final Verification")
    if "final_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["final_checks"] = [False, False, False]
    
    final_checks = st.session_state.checklist_state["final_checks"]
    final_checks[0] = st.checkbox("☐ Verify Bot Service Endpoint", value=final_checks[0], key="check_verify_bot")
    final_checks[1] = st.checkbox("☐ Test API Through APIM", value=final_checks[1], key="check_test_api")
    final_checks[2] = st.checkbox("☐ Verify Teams Integration", value=final_checks[2], key="check_verify_teams")
    
    st.subheader("10. Network and Connectivity Verification")
    if "connect_checks" not in st.session_state.checklist_state:
        st.session_state.checklist_state["connect_checks"] = [False, False, False, False, False]
    
    connect_checks = st.session_state.checklist_state["connect_checks"]
    connect_checks[0] = st.checkbox("☐ Verify App Service can access Key Vault", value=connect_checks[0], key="check_verify_kv")
    connect_checks[1] = st.checkbox("☐ Verify App Service can access Cosmos DB", value=connect_checks[1], key="check_verify_cosmos")
    connect_checks[2] = st.checkbox("☐ Verify App Service can access OpenAI Service", value=connect_checks[2], key="check_verify_openai")
    connect_checks[3] = st.checkbox("☐ Verify API Management can reach App Service", value=connect_checks[3], key="check_verify_apim")
    connect_checks[4] = st.checkbox("☐ Verify Application Gateway can route traffic to API Management", value=connect_checks[4], key="check_verify_agw")

def display_output_section(env):
    """Display the output section with the selected script"""
    if not st.session_state.script_generated:
        return
    
    st.markdown("---")
    st.header("Generated CLI Commands")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Updated order of script sections
        selected_section = st.radio(
            "Script Sections", 
            ["Complete Script", "Environment Variables", "Resource Group", "API Management", "Networking", "App Service", 
             "Data & AI", "Web App", "Bot Service", "Teams Integration", "Network Verification"],
            key="section_selector"
        )
        st.session_state.selected_section = selected_section
        
        # Add option to download everything as JSON
        if st.button("Export All Settings"):
            # Use the get_all_settings function to get structured settings
            from state import get_all_settings
            all_settings = get_all_settings()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_link = get_full_settings_download_link(
                all_settings, 
                f"anpi_full_settings_{timestamp}.json"
            )
            st.markdown(download_link, unsafe_allow_html=True)
            st.success("All settings exported successfully!")
    
    with col2:
        show_selected_section(env)

def show_selected_section(env):
    """Display the selected script section"""
    if not st.session_state.script_generated:
        st.warning("Please generate the CLI commands first.")
        return
    
    selected_section = st.session_state.selected_section
    scripts = st.session_state.generated_scripts
    
    if selected_section == "Complete Script":
        st.code(scripts["complete_script"], language="bash")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Complete Script",
                data=scripts["complete_script"],
                file_name=f"azure-anpi-bot-deploy-{env}.sh",
                mime="text/plain"
            )
        
        with col2:
            # Create markdown content
            markdown_content = create_markdown_content(scripts, env)
            st.markdown(
                get_markdown_download_link(markdown_content, f"azure-anpi-bot-deploy-{env}.md"),
                unsafe_allow_html=True
            )
    
    elif selected_section == "Environment Variables":
        st.code(scripts["environment_vars"], language="bash")
    elif selected_section == "Resource Group":
        st.code(scripts["resource_group"], language="bash")
    elif selected_section == "Networking":
        st.code(scripts["networking"], language="bash")
    elif selected_section == "App Service":
        st.code(scripts["app_service"], language="bash")
    elif selected_section == "Data & AI":
        st.code(scripts["data_ai_services"], language="bash")
    elif selected_section == "API Management":
        st.code(scripts["api_management"], language="bash")
        
        # Add YAML download button for API Management
        st.markdown("### API Configuration YAML")
        st.markdown("Tải xuống tệp YAML mẫu cho việc cấu hình API. Bạn có thể chỉnh sửa tệp này và nhập vào Azure Portal.")
        
        # Get APIM details from session state
        apim_name = st.session_state.sidebar_values.get('apim_name', 'apim-itz')
        api_path = st.session_state.sidebar_values.get('api_path', 'anpi')
        api_id = st.session_state.sidebar_values.get('api_id', 'anpi-bot-api')
        api_display_name = st.session_state.sidebar_values.get('api_display_name', 'ANPI Bot API')
        app_name = st.session_state.sidebar_values.get('app_name', f'app-itz-anpi-{env}-001')
        
        # Create download link
        yaml_download_link = get_yaml_download_link(api_display_name, env, app_name)
        st.markdown(yaml_download_link, unsafe_allow_html=True)
    
    elif selected_section == "Web App":
        st.code(scripts["web_app"], language="bash")
    elif selected_section == "Bot Service":
        st.code(scripts["bot_service"], language="bash")
    elif selected_section == "Teams Integration":
        st.code(scripts["teams_integration"], language="bash")
    elif selected_section == "Network Verification":
        st.code(scripts["network_verification"], language="bash")

def create_footer():
    """Create footer with info text"""
    st.sidebar.markdown("---")
    st.sidebar.info("""
    This tool generates Azure CLI commands to deploy the ANPI Bot infrastructure.
    Make sure to review the generated commands before executing them in your Azure environment.

    Follow the deployment checklist tab to ensure you complete all steps in the correct order.
    """)