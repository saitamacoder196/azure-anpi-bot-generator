"""
UI components for the Streamlit application.
"""
from datetime import datetime
import streamlit as st
from utils import generate_azure_pipeline_yaml, get_apim_policy_xml, get_initial_knowledge_json, get_json_download_link, get_markdown_download_link, generate_jwt_secret, create_markdown_content, get_search_datasource_json, get_search_index_json, get_search_indexer_json, get_settings_download_link, get_teams_app_manifest_download_link, get_xml_download_link, get_yaml_download_link, parse_uploaded_settings, get_full_settings_download_link
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
            if st.button("Export All Settings", key="export_all_settings_sidebar"):
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
                            st.experimental_rerun()
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
                            st.experimental_rerun()
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
                    st.experimental_rerun()
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
            # Force experimental_rerun
            st.experimental_rerun()
    
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
                    st.experimental_rerun()
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
    
    # Create input fields with default values and unique keys
    vnet_name = st.text_input("Virtual Network Name", value=default_vnet_name, key="net_vnet_name")
    vnet_address_prefix = st.text_input("VNet Address Prefix", value=default_vnet_address_prefix, key="net_vnet_prefix")
    
    st.subheader("Subnets")
    subnet_name = st.text_input("Subnet Name", value=default_subnet_name, key="net_subnet_name")
    subnet_prefix = st.text_input("Subnet Address Prefix", value=default_subnet_prefix, key="net_subnet_prefix")
    
    st.subheader("Application Gateway")
    pip_name = st.text_input("Public IP Name", value=default_pip_name, key="net_pip_name")
    agw_name = st.text_input("Application Gateway Name", value=default_agw_name, key="net_agw_name")
    waf_name = st.text_input("WAF Policy Name", value=default_waf_name, key="net_waf_name")
    
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
                    st.experimental_rerun()
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
    default_openai_region = saved_settings.get('openai_region', "eastus")
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
    
    # Add region selection specifically for OpenAI
    openai_regions = ["japaneast", "eastus", "southeastasia"]
    openai_region = st.selectbox(
        "OpenAI Region", 
        openai_regions,
        index=openai_regions.index(default_openai_region) if default_openai_region in openai_regions else 0,
        help="Azure OpenAI is only available in select regions. Choose one that supports the models you need."
    )
    
    openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-35-turbo", "gpt-4"]
    openai_model = st.selectbox(
        "OpenAI Model", 
        openai_models,
        index=openai_models.index(default_openai_model) if default_openai_model in openai_models else 0
    )
    
    # Add a note about model availability in regions
    st.info("Note: Not all models are available in all regions. GPT-4o models might only be available in East US.")
    
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
    
    # Add download buttons for search index and indexer JSON
    st.markdown("### Search Index Configuration")
    st.info("Instead of creating the index through CLI, download these JSON files and import them through the Azure Portal.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download Index JSON"):
            index_json = get_search_index_json(search_index_name, semantic_config_name)
            index_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_link = get_json_download_link(
                index_json,
                f"anpi_search_index_{env}_{index_timestamp}.json"
            )
            st.markdown(download_link, unsafe_allow_html=True)
    
    with col2:
        if st.button("Download Indexer JSON"):
            indexer_json = get_search_indexer_json(search_index_name)
            indexer_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_link = get_json_download_link(
                indexer_json,
                f"anpi_search_indexer_{env}_{indexer_timestamp}.json"
            )
            st.markdown(download_link, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)    
    with col1:
        if st.button("Download Data Source JSON"):
            datasource_json = get_search_datasource_json(cosmos_name, cosmos_db_name, search_index_name)
            datasource_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_link = get_json_download_link(
                datasource_json,
                f"anpi_search_datasource_{env}_{datasource_timestamp}.json"
            )
            st.markdown(download_link, unsafe_allow_html=True)
    
    with col2:
        if st.button("Download Knowledge Init JSON"):
            knowledge_json = get_initial_knowledge_json()
            knowledge_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_link = get_json_download_link(
                knowledge_json,
                f"anpi_initial_knowledge_{env}_{knowledge_timestamp}.json"
            )
            st.markdown(download_link, unsafe_allow_html=True)
    
    # Add guidance for using the knowledge init data
    st.info("""
    The Knowledge Init JSON file contains sample knowledge entries for the ANPI system.
    You can use this file to populate your Cosmos DB knowledge container using the Azure Data Factory or 
    import it directly through the Azure Portal Cosmos DB Data Explorer.
    """)


    # Add import instructions
    # Add import instructions
    with st.expander("How to Import Index, Indexer, and Sample Knowledge", expanded=False):
        st.markdown("""
        ### Importing Search Index, Indexer & Data Source in Azure Portal
        
        1. **Create Data Source First:**
        - Navigate to your Azure AI Search service in Azure Portal
        - Select "Data sources" from the left menu
        - Click "Add data source"
        - Select "Cosmos DB" as the source
        - Fill in the connection details to your Cosmos DB account
        - Name it "cosmos-anpi-knowledge"
        - Select the Cosmos DB collection that contains your knowledge base documents
        - **Alternatively**: Click "Import" and upload the downloaded data source JSON file
        - **Important**: You'll need to update the AccountKey in the connection string with your actual Cosmos DB key
        
        2. **Import the Index:**
        - In your Azure AI Search service, select "Indexes" from the left menu
        - Click "Import index"
        - Upload the downloaded index JSON file
        - Review settings and click "Create"
        
        3. **Import the Indexer:**
        - Select "Indexers" from the left menu
        - Click "Import indexer"
        - Upload the downloaded indexer JSON file
        - Make sure the data source name matches "cosmos-anpi-knowledge"
        - Review settings and click "Create"
        - Click "Run" to start the indexer
        
        ### Importing Sample Knowledge to Cosmos DB
        
        1. **Using Azure Portal Data Explorer:**
        - Navigate to your Cosmos DB account in Azure Portal
        - Select "Data Explorer" from the left menu
        - Find the "knowledge" container in your database
        - Click "Items" and then "New Item"
        - Paste each JSON object from the downloaded knowledge init file (one at a time)
        - Click "Save" for each item
        
        2. **Using Azure Data Factory (for bulk import):**
        - Create a new Azure Data Factory pipeline
        - Add a "Copy Data" activity
        - Configure the source as Azure Blob Storage and upload the knowledge JSON file
        - Configure the sink as Cosmos DB
        - Run the pipeline to import all knowledge entries at once
        
        3. **Using the Azure CLI:**
        ```bash
        # For each item in the knowledge JSON file
        az cosmosdb sql container create-item \\
            --account-name [cosmos-account-name] \\
            --database-name [database-name] \\
            --container-name knowledge \\
            --resource-group $RG_NAME \\
            --value @item.json
        ```
        
        ### Alternative CLI Commands for Semantic Configuration
        
        You can also use these CLI commands to create the semantic configuration:
        
        ```bash
        # Create the semantic configuration using REST API
        cat > /tmp/semantic-config.json << EOF
        {
        "name": "${semantic_config_name}",
        "prioritizedFields": {
            "titleField": {"fieldName": "title"},
            "prioritizedContentFields": [{"fieldName": "content"}],
            "prioritizedKeywordsFields": [
            {"fieldName": "category"},
            {"fieldName": "tags"}
            ]
        }
        }
        EOF
        
        # Apply the semantic configuration
        az rest --method put \\
        --uri "https://${search_name}.search.windows.net/indexes/${search_index_name}/semantic-configurations/${semantic_config_name}?api-version=2023-07-01-Preview" \\
        --headers "Content-Type=application/json" "api-key=${AZURE_SEARCH_KEY}" \\
        --body @/tmp/semantic-config.json
        ```
        """)
    
    # Create a dictionary with the current settings
    current_settings = {
        'kv_name': kv_name,
        'cosmos_name': cosmos_name,
        'cosmos_db_name': cosmos_db_name,
        'openai_name': openai_name,
        'openai_region': openai_region,
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
                    st.experimental_rerun()
                else:
                    st.error("Failed to parse the uploaded file.")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('api_management')
    
    # Set default values, using saved settings if available
    default_apim_name = saved_settings.get('apim_name', "apim-itz-fjp")
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
    
    st.subheader("API Management Policy")
    st.info("You can download a sample policy XML file to configure your API in the Azure Portal.")
    
    if st.button("Download APIM Policy XML"):
        policy_xml = get_apim_policy_xml(allowed_origins)
        policy_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_link = get_xml_download_link(
            policy_xml,
            f"apim_policy_{policy_timestamp}.xml"
        )
        st.markdown(download_link, unsafe_allow_html=True)
    
    # Add guidance for using the policy XML
    with st.expander("How to Apply the Policy XML in Azure Portal", expanded=False):
        st.markdown("""
        ### Applying the API Policy in Azure Portal
        
        1. **Navigate to your API Management service**:
           - Go to the Azure Portal
           - Find your API Management service
           - Click on "APIs" in the left menu
           - Select your API (the one with the ID you configured above)
        
        2. **Access the Policy Editor**:
           - Click on "All operations" to apply the policy to all operations
           - Click on the "Policies" button (the </> icon)
        
        3. **Apply the XML Policy**:
           - In the policy editor, select "Code view" if not already selected
           - Delete the existing policy content
           - Paste the downloaded XML policy
           - Click "Save"
           
        4. **Test the API**:
           - After applying the policy, test an API operation to ensure the backend connection works
           - Verify that CORS is properly configured by testing from your client application
        """)
    return current_settings
    
def create_cicd_tab():
    """Create the CI/CD Configuration tab for Azure DevOps pipelines"""
    st.header("Azure DevOps CI/CD Pipeline Configuration")
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('cicd')
    
    # Set default values, using saved settings if available
    default_project_url = saved_settings.get('project_url', "https://dev.azure.com/FJPFST/ANPI%20Teams%20Bot")
    default_repo_url = saved_settings.get('repo_url', "https://FJPFST@dev.azure.com/FJPFST/ANPI%20Teams%20Bot/_git/ANPI%20Teams%20Bot")
    default_service_conn_name = saved_settings.get('service_conn_name', "ANPI-Azure-Connection")
    
    # Project settings
    st.subheader("Azure DevOps Project Settings")
    project_url = st.text_input("Project URL", value=default_project_url)
    repo_url = st.text_input("Repository URL", value=default_repo_url)
    
    # Service connection settings
    st.subheader("Service Connections")
    st.info("Configure service connections for deploying to different environments")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        service_conn_name = st.text_input("Base Service Connection Name", value=default_service_conn_name)
        
    # Branch environments
    st.subheader("Branch Environments")
    env_dev = st.checkbox("Development Environment", value=True)
    env_test = st.checkbox("Test Environment", value=True)
    env_prod = st.checkbox("Production Environment", value=True)
    
    # Generate button
    if st.button("Generate Azure Pipelines YAML"):
        pipeline_yaml = generate_azure_pipeline_yaml(service_conn_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_link = get_yaml_download_link(
            pipeline_yaml,
            f"azure-pipelines_{timestamp}.yml"
        )
        st.markdown(download_link, unsafe_allow_html=True)
        
        # Show instructions
        st.success("Azure Pipelines YAML file generated successfully!")
        
        with st.expander("How to Set Up CI/CD Pipeline in Azure DevOps", expanded=True):
            st.markdown(f"""
            ### Setting Up CI/CD Pipeline in Azure DevOps
            
            #### 1. Create Service Connections
            
            You'll need to create service connections for each environment (Dev, Test, Prod):
            
            1. Go to your Azure DevOps project: [{project_url}]({project_url})
            2. Navigate to Project Settings > Service Connections
            3. Click "New service connection" and select "Azure Resource Manager"
            4. Choose "Service principal (automatic)" authentication
            5. Fill in the details:
               - Scope level: Subscription
               - Subscription: Select your subscription
               - Resource Group: Select your resource group for each environment
               - Service connection name: 
                  - {service_conn_name}-Dev (for Development)
                  - {service_conn_name}-Test (for Test)
                  - {service_conn_name}-Prod (for Production)
            6. Make sure "Grant access permission to all pipelines" is checked
            7. Click "Save"
            
            #### 2. Create the Pipeline
            
            1. In your Azure DevOps project, go to Pipelines
            2. Click "New pipeline"
            3. Select "Azure Repos Git" as the code location
            4. Select your repository: "ANPI Teams Bot"
            5. Select "Existing Azure Pipelines YAML file"
            6. Select the branch where you've committed the YAML file and the path to the file
            7. Review the pipeline and click "Run"
            
            #### 3. Set Up Branch Policies (Optional but Recommended)
            
            1. Go to Repos > Branches
            2. Select the branch you want to protect (e.g., main, develop)
            3. Click on the "..." menu and select "Branch policies"
            4. Enable "Require a minimum number of reviewers"
            5. Enable "Check for linked work items"
            6. Under "Build validation", add your pipeline to run whenever changes are pushed
            
            #### 4. Create Variable Groups (Optional)
            
            For storing environment-specific variables:
            
            1. Go to Pipelines > Library
            2. Click "+ Variable group"
            3. Create groups for each environment (e.g., "anpi-dev-variables", "anpi-test-variables", "anpi-prod-variables")
            4. Add variables needed for each environment
            """)
    
    # Create a dictionary with the current settings
    current_settings = {
        'project_url': project_url,
        'repo_url': repo_url,
        'service_conn_name': service_conn_name,
        'env_dev': env_dev,
        'env_test': env_test,
        'env_prod': env_prod
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('cicd', current_settings)
    
    return current_settings

def create_teams_integration_tab():
    """Create the Teams Integration tab with export/import functionality and channel setup guidance"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Teams Integration")
    
    # Add export/import functionality for this tab
    # (Existing export/import code)
    
    # Load any saved settings
    from state import load_tab_settings
    saved_settings = load_tab_settings('teams_integration')
    
    # Set default values, using saved settings if available
    default_teams_app_name = saved_settings.get('teams_app_name', f"ANPI Teams Bot {env.capitalize()}")
    default_teams_redirect_uri = saved_settings.get('teams_redirect_uri', "https://token.botframework.com/.auth/web/redirect")
    default_bot_id = saved_settings.get('bot_id', "add0fcf1-3190-4a12-8ca0-00c47acb6178")
    default_package_name = saved_settings.get('package_name', f"com.fjp.anpibot{env}")
    
    # Create input fields with default values
    teams_app_name = st.text_input("Teams App Name", value=default_teams_app_name)
    teams_redirect_uri = st.text_input("Teams Redirect URI", value=default_teams_redirect_uri)
    
    # Add Bot ID field (same as MS App ID)
    col1, col2 = st.columns(2)
    with col1:
        bot_id = st.text_input("Bot ID (same as MS App ID)", 
                               value=st.session_state.sidebar_values.get('ms_app_id', default_bot_id))
    
    with col2:
        package_name = st.text_input("Package Name", value=default_package_name)
    
    # Download Teams App Manifest
    st.subheader("Teams App Package")
    st.info("Download a Teams app manifest package (ZIP) to use when registering your bot in Teams.")
    
    # Button to download the Teams app manifest ZIP
    if st.button("Generate Teams App Package"):
        # Generate the manifest and ZIP file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_link = get_teams_app_manifest_download_link(
            teams_app_name, 
            bot_id, 
            package_name,
            env
        )
        st.markdown(download_link, unsafe_allow_html=True)
        st.success("Teams app manifest package generated successfully!")
    
    # Teams Channel Configuration Section
    st.subheader("Microsoft Teams Channel Setup")
    st.info("Follow these steps to enable and configure the Microsoft Teams channel for your bot.")
    
    with st.expander("Teams Channel Configuration Guide", expanded=True):
        st.markdown("""
        ### Configuring Microsoft Teams Channel for Your Bot
        
        After creating your bot in Azure, you need to enable the Microsoft Teams channel to allow users to interact with your bot in Teams:
        
        #### Step 1: Navigate to the Bot Channel Registration
        
        1. Go to the Azure Portal and find your bot resource (`bot-itz-anpi-{env}`)
        2. In the left menu, click on **Channels** under Settings
        
        #### Step 2: Add Microsoft Teams Channel
        
        1. In the available channels list, find and click on **Microsoft Teams**
        2. In the Terms of Service dialog, check the box to agree to the Microsoft Channel Publication Terms and the Microsoft Privacy Statement
        3. Click **Agree**
        
        #### Step 3: Configure Teams Channel Settings
        
        1. In the messaging tab:
            - Choose either **Microsoft Teams Commercial** (most common) or **Microsoft Teams Government** depending on your organization
        2. Leave the default settings for other options
        3. Click **Apply**
        
        #### Step 4: Test Your Bot in Teams
        
        1. Once the Teams channel is enabled, you can access your bot in Teams through:
            - The Teams app you uploaded using the manifest package
            - Direct testing link in the Azure portal
        
        #### Additional Channels (Optional)
        
        You can enable other channels as needed:
        - **Web Chat**: For embedding the bot on websites
        - **Direct Line**: For custom client applications
        - **Email**: For interaction via email
        - **Microsoft 365**: For Outlook and other Microsoft 365 apps
        
        #### Troubleshooting Tips
        
        - If you update your bot in Azure, you might need to update the manifest and reinstall it in Teams
        - If your bot isn't responding in Teams, check the bot's endpoint URL and ensure it's correctly pointing to your API Management service
        - Verify the Microsoft App ID and password match between your bot registration and your app settings
        """)
    
    # Complete End-to-End Setup Guide
    with st.expander("Complete End-to-End Setup Process", expanded=False):
        st.markdown("""
        ### End-to-End Setup Process
        
        Follow these steps to completely set up your bot for Microsoft Teams:
        
        #### 1. Azure Resources Deployment
        - Deploy all Azure resources using the generated scripts
        - Verify all resources are properly configured
        
        #### 2. Bot Service Configuration
        - Ensure the Bot Service is configured with the APIM endpoint URL
        - Verify the Bot Service has the correct App ID and password
        
        #### 3. Teams Channel Configuration
        - Enable the Microsoft Teams channel in Azure Bot Service
        - Configure messaging settings
        
        #### 4. Teams App Package Creation
        - Generate the Teams app manifest package using this tool
        - Ensure the bot ID matches your Microsoft App ID
        
        #### 5. Teams App Installation
        - Upload the manifest package to Microsoft Teams
        - Install the app in your Teams environment
        
        #### 6. Testing
        - Test the bot in Teams directly
        - Verify all intended functionality works
        
        #### 7. Deployment to Production
        - Repeat the process for production environment
        - Ensure proper security and compliance settings
        """)
    
    # Create a dictionary with the current settings
    current_settings = {
        'teams_app_name': teams_app_name,
        'teams_redirect_uri': teams_redirect_uri,
        'bot_id': bot_id,
        'package_name': package_name
    }
    
    # Save the current settings to session state
    from state import save_tab_settings
    save_tab_settings('teams_integration', current_settings)
    
    return current_settings
def create_deployment_checklist_tab():
    """Create the Deployment Checklist tab with comprehensive security checks"""
    st.header("Deployment Checklist")
    
    # Create expandable sections for different check categories
    with st.expander("1. Initial Setup", expanded=True):
        if "setup_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["setup_checks"] = [False, False, False]
        
        setup_checks = st.session_state.checklist_state["setup_checks"]
        setup_checks[0] = st.checkbox("☐ Install Azure CLI", value=setup_checks[0], key="check_install_cli")
        setup_checks[1] = st.checkbox("☐ Login to Azure CLI (`az login`)", value=setup_checks[1], key="check_login_cli")
        setup_checks[2] = st.checkbox("☐ Set correct subscription (`az account set --subscription \"$SUBSCRIPTION_ID\"`)", value=setup_checks[2], key="check_set_sub")
    
    with st.expander("2. Resource Group Deployment", expanded=True):
        if "rg_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["rg_checks"] = [False]
        
        rg_checks = st.session_state.checklist_state["rg_checks"]
        rg_checks[0] = st.checkbox("☐ Create Resource Group", value=rg_checks[0], key="check_create_rg")
    
    with st.expander("3. API Management & Networking", expanded=True):
        if "api_net_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["api_net_checks"] = [False, False, False, False, False]
        
        api_net_checks = st.session_state.checklist_state["api_net_checks"]
        api_net_checks[0] = st.checkbox("☐ Create API Management Service", value=api_net_checks[0], key="check_create_apim")
        api_net_checks[1] = st.checkbox("☐ Create Virtual Network and Subnet", value=api_net_checks[1], key="check_create_vnet")
        api_net_checks[2] = st.checkbox("☐ Create Public IP Address", value=api_net_checks[2], key="check_create_pip")
        api_net_checks[3] = st.checkbox("☐ Create Application Gateway with WAF", value=api_net_checks[3], key="check_create_agw")
        api_net_checks[4] = st.checkbox("☐ Configure API in APIM", value=api_net_checks[4], key="check_config_apim")
    
    with st.expander("4. Data & AI Services", expanded=True):
        if "data_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["data_checks"] = [False, False, False, False, False]
        
        data_checks = st.session_state.checklist_state["data_checks"]
        data_checks[0] = st.checkbox("☐ Create Key Vault", value=data_checks[0], key="check_create_kv")
        data_checks[1] = st.checkbox("☐ Create Cosmos DB and Containers", value=data_checks[1], key="check_create_cosmos")
        data_checks[2] = st.checkbox("☐ Create Azure OpenAI Service", value=data_checks[2], key="check_create_openai")
        data_checks[3] = st.checkbox("☐ Deploy OpenAI Models", value=data_checks[3], key="check_deploy_models")
        data_checks[4] = st.checkbox("☐ Create Azure Search Service and Index", value=data_checks[4], key="check_create_search")
    
    with st.expander("5. App Service & Bot Configuration", expanded=True):
        if "app_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["app_checks"] = [False, False, False, False, False]
        
        app_checks = st.session_state.checklist_state["app_checks"]
        app_checks[0] = st.checkbox("☐ Create App Service Plan", value=app_checks[0], key="check_create_asp")
        app_checks[1] = st.checkbox("☐ Create Application Insights", value=app_checks[1], key="check_create_appins")
        app_checks[2] = st.checkbox("☐ Create Web App", value=app_checks[2], key="check_create_webapp")
        app_checks[3] = st.checkbox("☐ Store Secrets in Key Vault", value=app_checks[3], key="check_store_secrets")
        app_checks[4] = st.checkbox("☐ Create Bot Service", value=app_checks[4], key="check_create_bot")
    
    with st.expander("6. Teams Integration", expanded=True):
        if "teams_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["teams_checks"] = [False, False, False]
        
        teams_checks = st.session_state.checklist_state["teams_checks"]
        teams_checks[0] = st.checkbox("☐ Register Teams App", value=teams_checks[0], key="check_register_teams")
        teams_checks[1] = st.checkbox("☐ Configure Teams Channel in Bot", value=teams_checks[1], key="check_teams_channel")
        teams_checks[2] = st.checkbox("☐ Test Teams Integration", value=teams_checks[2], key="check_verify_teams")
    
    with st.expander("7. Network Security & Isolation", expanded=True):
        if "net_sec_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["net_sec_checks"] = [False, False, False, False, False]
        
        net_sec_checks = st.session_state.checklist_state["net_sec_checks"]
        
        # Check 1: Verify services in VNet
        col1, col2 = st.columns([1, 3])
        with col1:
            net_sec_checks[0] = st.checkbox("☐ Verify all services are inside Virtual Network or have Private Endpoints", 
                                            value=net_sec_checks[0], key="check_vnet_integration")
        with col2:
            if st.button("Show Verification Script", key="script_vnet_check"):
                st.code("""
    # Check if resources are in VNet or have private endpoints
    # Run these commands and review the output for each service

    # 1. Check App Service VNet integration
    az webapp vnet-integration list --resource-group $RG_NAME --name $APP_NAME -o table

    # 2. Check Private Endpoints for Cosmos DB
    az network private-endpoint-connection list --resource-group $RG_NAME \\
    --name $COSMOS_NAME --type Microsoft.DocumentDB/databaseAccounts -o table

    # 3. Check Private Endpoints for Key Vault
    az network private-endpoint-connection list --resource-group $RG_NAME \\
    --name $KV_NAME --type Microsoft.KeyVault/vaults -o table

    # 4. Check Private Endpoints for OpenAI
    az network private-endpoint-connection list --resource-group $RG_NAME \\
    --name $OPENAI_NAME --type Microsoft.CognitiveServices/accounts -o table

    # 5. Check Private Endpoints for Search
    az network private-endpoint-connection list --resource-group $RG_NAME \\
    --name $SEARCH_NAME --type Microsoft.Search/searchServices -o table

    # 6. List all resources not behind private endpoints
    echo "Resources that may not be properly isolated:"
    az resource list --resource-group $RG_NAME --query "[?type!='Microsoft.Network/virtualNetworks' && type!='Microsoft.Network/privateEndpoints'].{Name:name, Type:type}" -o table
                """, language="bash")
        
        # Check 2: Verify APIM access through App Gateway
        col1, col2 = st.columns([1, 3])
        with col1:
            net_sec_checks[1] = st.checkbox("☐ Verify APIM is accessible through Application Gateway only", 
                                            value=net_sec_checks[1], key="check_apim_access")
        with col2:
            if st.button("Show Verification Script", key="script_apim_check"):
                st.code("""
    # Check APIM network configuration
    echo "Checking APIM network configuration..."

    # 1. Verify APIM network type (should be Internal for proper isolation)
    APIM_NETWORK_TYPE=$(az apim show --name $APIM_NAME --resource-group $RG_NAME --query "properties.virtualNetworkType" -o tsv)
    echo "APIM Network Type: $APIM_NETWORK_TYPE"
    if [ "$APIM_NETWORK_TYPE" != "Internal" ]; then
    echo "WARNING: APIM is not set to Internal VNet type. External access may be possible."
    fi

    # 2. Check if APIM is in a subnet (for internal type)
    APIM_SUBNET_ID=$(az apim show --name $APIM_NAME --resource-group $RG_NAME --query "properties.virtualNetworkConfiguration.subnetResourceId" -o tsv)
    if [ -z "$APIM_SUBNET_ID" ]; then
    echo "WARNING: APIM is not associated with a subnet"
    else
    echo "APIM Subnet: $APIM_SUBNET_ID"
    fi

    # 3. Check Application Gateway backend pool configuration
    echo "Checking Application Gateway backend pool for APIM..."
    AGW_BACKEND_POOLS=$(az network application-gateway address-pool list \\
    --gateway-name $AGW_NAME \\
    --resource-group $RG_NAME -o json)

    # Find APIM in the backend pools
    echo "$AGW_BACKEND_POOLS" | grep -q $APIM_NAME
    if [ $? -eq 0 ]; then
    echo "SUCCESS: APIM found in Application Gateway backend pool"
    else
    echo "WARNING: APIM not found in Application Gateway backend pool"
    fi

    # 4. Test access - try to access APIM directly (should fail if properly configured)
    echo "To test if APIM is only accessible through Application Gateway:"
    echo "  1. Try to access APIM directly: curl -I https://$APIM_NAME.azure-api.net"
    echo "  2. Then try through Application Gateway: curl -I http://$AGW_PIP_FQDN"
    echo "  The first request should fail if APIM is properly isolated"
                """, language="bash")
        
        # Check 3: Verify NSG rules
        col1, col2 = st.columns([1, 3])
        with col1:
            net_sec_checks[2] = st.checkbox("☐ Configure NSGs for all subnets with proper rules", 
                                            value=net_sec_checks[2], key="check_nsgs")
        with col2:
            if st.button("Show Verification Script", key="script_nsg_check"):
                st.code("""
    # List and verify NSGs on all subnets
    echo "Checking NSG configurations for all subnets..."

    # 1. List all subnets and their NSGs
    az network vnet subnet list \\
    --resource-group $RG_NAME \\
    --vnet-name $VNET_NAME \\
    --query "[].{Name:name, NSG:networkSecurityGroup.id, AddressPrefix:addressPrefix}" -o table

    # 2. For each subnet with an NSG, check the rules
    for SUBNET in $(az network vnet subnet list --resource-group $RG_NAME --vnet-name $VNET_NAME --query "[].name" -o tsv); do
    NSG_ID=$(az network vnet subnet show --resource-group $RG_NAME --vnet-name $VNET_NAME --name $SUBNET --query "networkSecurityGroup.id" -o tsv)
    
    if [ -n "$NSG_ID" ]; then
        # Extract NSG name from ID
        NSG_NAME=$(echo $NSG_ID | cut -d'/' -f9)
        
        echo "Checking NSG rules for subnet $SUBNET (NSG: $NSG_NAME):"
        az network nsg rule list \\
        --resource-group $RG_NAME \\
        --nsg-name $NSG_NAME \\
        --query "[].{Name:name, Priority:priority, Direction:direction, Access:access, Protocol:protocol, SourcePrefix:sourceAddressPrefix, DestinationPrefix:destinationAddressPrefix, DestinationPortRange:destinationPortRange}" \\
        -o table
        
        # Check for overly permissive rules
        OPEN_RULES=$(az network nsg rule list \\
        --resource-group $RG_NAME \\
        --nsg-name $NSG_NAME \\
        --query "[?access=='Allow' && (sourceAddressPrefix=='*' || sourceAddressPrefix=='0.0.0.0/0' || sourceAddressPrefix=='Internet')].name" -o tsv)
        
        if [ -n "$OPEN_RULES" ]; then
        echo "WARNING: Found potentially overly permissive rules in $NSG_NAME:"
        echo "$OPEN_RULES"
        else
        echo "No overly permissive rules found in $NSG_NAME"
        fi
    else
        echo "WARNING: Subnet $SUBNET has no NSG attached"
    fi
    
    echo "------------------------------------------"
    done

    # 3. Verify NSG flow logs are enabled (optional but recommended)
    echo "Checking if NSG flow logs are enabled..."
    for NSG in $(az network nsg list --resource-group $RG_NAME --query "[].name" -o tsv); do
    FLOW_LOGS=$(az network watcher flow-log show --nsg $NSG --resource-group $RG_NAME 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "Flow logs are configured for NSG: $NSG"
    else
        echo "WARNING: No flow logs configured for NSG: $NSG"
    fi
    done
                """, language="bash")
        
        # Check 4: Verify App Service access restrictions
        col1, col2 = st.columns([1, 3])
        with col1:
            net_sec_checks[3] = st.checkbox("☐ Verify App Service access restrictions are configured", 
                                            value=net_sec_checks[3], key="check_app_restrictions")
        with col2:
            if st.button("Show Verification Script", key="script_app_restriction_check"):
                st.code("""
    # Check App Service network access restrictions
    echo "Checking App Service network access restrictions..."

    # 1. List access restrictions for App Service
    az webapp config access-restriction show \\
    --resource-group $RG_NAME \\
    --name $APP_NAME \\
    -o table

    # 2. Check for unrestricted access (default 'Allow All' rule)
    DEFAULT_RULE=$(az webapp config access-restriction show \\
    --resource-group $RG_NAME \\
    --name $APP_NAME \\
    --query "ipSecurityRestrictions[?name=='Allow all']" -o json)

    if [ -z "$DEFAULT_RULE" ] || [ "$DEFAULT_RULE" == "[]" ]; then
    echo "SUCCESS: Default 'Allow All' rule has been restricted"
    else
    echo "WARNING: Default 'Allow All' rule still exists - app is accessible from anywhere"
    fi

    # 3. Check if SCM site also has access restrictions
    SCM_RESTRICTIONS=$(az webapp config access-restriction show \\
    --resource-group $RG_NAME \\
    --name $APP_NAME \\
    --query "scmIpSecurityRestrictions" -o json)

    echo "SCM site access restrictions:"
    echo $SCM_RESTRICTIONS | jq .

    # 4. Verify App Service is using VNet integration if available
    VNET_INTEGRATION=$(az webapp vnet-integration show \\
    --resource-group $RG_NAME \\
    --name $APP_NAME 2>/dev/null)

    if [ $? -eq 0 ]; then
    echo "App Service has VNet integration configured"
    else
    echo "WARNING: App Service does not have VNet integration"
    fi

    # 5. Check if outbound traffic is forced through VNet
    VNET_ROUTE_ALL=$(az webapp config show \\
    --resource-group $RG_NAME \\
    --name $APP_NAME \\
    --query "vnetRouteAllEnabled" -o tsv)

    if [ "$VNET_ROUTE_ALL" == "true" ]; then
    echo "SUCCESS: App Service outbound traffic is forced through VNet"
    else
    echo "WARNING: App Service outbound traffic is not forced through VNet"
    fi
                """, language="bash")
        
        # Check 5: Verify Bastion/Jump server
        col1, col2 = st.columns([1, 3])
        with col1:
            net_sec_checks[4] = st.checkbox("☐ Configure Azure Bastion or Jump server for admin access", 
                                            value=net_sec_checks[4], key="check_bastion")
        with col2:
            if st.button("Show Verification Script", key="script_bastion_check"):
                st.code("""
    # Check if Azure Bastion is configured
    echo "Checking for Azure Bastion or Jump Server..."

    # 1. Check if Azure Bastion exists in the resource group
    BASTION=$(az resource list \\
    --resource-group $RG_NAME \\
    --resource-type "Microsoft.Network/bastionHosts" \\
    --query "[].{Name:name, Type:type}" -o table)

    if [ -n "$BASTION" ]; then
    echo "Azure Bastion found:"
    echo "$BASTION"
    else
    echo "Azure Bastion not found in resource group $RG_NAME"
    
    # 2. Check if there's a VM that might be used as a jump server
    JUMP_VMS=$(az vm list \\
        --resource-group $RG_NAME \\
        --query "[?tags.Role=='JumpServer'].{Name:name, Size:hardwareProfile.vmSize}" -o table)
    
    if [ -n "$JUMP_VMS" ]; then
        echo "Potential Jump Server VMs found:"
        echo "$JUMP_VMS"
    else
        echo "WARNING: No Azure Bastion or potential Jump Server found"
        echo "RECOMMENDATION: Deploy Azure Bastion or a secure Jump Server for administrative access"
    fi
    fi

    # 3. Check if Just-In-Time VM access is configured (if using Azure Security Center/Defender for Cloud)
    if command -v az security -v &>/dev/null; then
    echo "Checking for Just-In-Time VM access configuration..."
    JIT_POLICY=$(az security jit-policy list --resource-group $RG_NAME 2>/dev/null)
    if [ $? -eq 0 ] && [ "$JIT_POLICY" != "[]" ]; then
        echo "Just-In-Time VM access policy found:"
        echo "$JIT_POLICY" | jq .
    else
        echo "No Just-In-Time VM access policy found"
    fi
    fi

    # 4. Check if Privileged Identity Management (PIM) is enabled for the resource group
    echo "To check if PIM is configured for the resource group:"
    echo "1. Go to Azure Portal > Azure AD > Privileged Identity Management"
    echo "2. Check if the resource group $RG_NAME is managed with PIM"
    echo "3. Verify that administrative roles require activation"
    echo "NOTE: PIM configuration cannot be checked via CLI"

    # 5. Check if Conditional Access policies exist for administrative access
    echo "To check Conditional Access policies:"
    echo "1. Go to Azure Portal > Azure AD > Security > Conditional Access"
    echo "2. Verify policies exist that require MFA for administrative access"
    echo "3. Ensure policies target admin roles for Azure resources"
    echo "NOTE: Conditional Access configuration cannot be checked via CLI"
                """, language="bash")
        
        # Add a section for network diagram generation
        st.subheader("Network Diagram Generation")
        if st.button("Generate Network Architecture Diagram", key="gen_network_diagram"):
            st.info("This would generate a network architecture diagram showing VNets, subnets, NSGs, and connectivity between resources.")
            st.markdown("For a comprehensive network security assessment, consider using:")
            st.markdown("- [Azure Network Watcher](https://learn.microsoft.com/en-us/azure/network-watcher/)")
            st.markdown("- [Azure Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/)")
            st.markdown("- [Microsoft Defender for Cloud Apps](https://learn.microsoft.com/en-us/defender-cloud-apps/)")
            
    with st.expander("8. WAF & DDoS Protection", expanded=True):
        if "waf_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["waf_checks"] = [False, False, False, False]
        
        waf_checks = st.session_state.checklist_state["waf_checks"]
        waf_checks[0] = st.checkbox("☐ Configure WAF in Block Mode with OWASP rules", value=waf_checks[0], key="check_waf_block")
        waf_checks[1] = st.checkbox("☐ Configure DDoS protection", value=waf_checks[1], key="check_ddos")
        waf_checks[2] = st.checkbox("☐ Test WAF rules with sample attacks", value=waf_checks[2], key="check_waf_test")
        waf_checks[3] = st.checkbox("☐ Review and customize WAF rule exclusions if needed", value=waf_checks[3], key="check_waf_exclusions")
    
    with st.expander("9. Logging & Monitoring", expanded=True):
        if "log_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["log_checks"] = [False, False, False, False, False]
        
        log_checks = st.session_state.checklist_state["log_checks"]
        log_checks[0] = st.checkbox("☐ Configure diagnostic settings for all resources", value=log_checks[0], key="check_diag_settings")
        log_checks[1] = st.checkbox("☐ Set up Log Analytics workspace with appropriate retention (min 3 months)", value=log_checks[1], key="check_log_retention")
        log_checks[2] = st.checkbox("☐ Configure alerts for critical errors", value=log_checks[2], key="check_alerts")
        log_checks[3] = st.checkbox("☐ Set up Azure Monitor or integrate with SIEM if available", value=log_checks[3], key="check_monitor")
        log_checks[4] = st.checkbox("☐ Verify all key logs are being captured (HTTP access, errors, auth, DB)", value=log_checks[4], key="check_log_types")
    
    with st.expander("10. HTTPS & Security Headers", expanded=True):
        if "https_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["https_checks"] = [False, False, False, False]
        
        https_checks = st.session_state.checklist_state["https_checks"]
        https_checks[0] = st.checkbox("☐ Enforce HTTPS for all services", value=https_checks[0], key="check_https")
        https_checks[1] = st.checkbox("☐ Configure TLS 1.2+ and disable older protocols", value=https_checks[1], key="check_tls")
        
        security_headers_tooltip = """
        Configure the following security headers:
        - Cache-Control: no-store
        - Content-Security-Policy with appropriate settings
        - Permissions-Policy
        - Referrer-Policy
        - Strict-Transport-Security
        - X-Content-Type-Options
        - X-Frame-Options
        - X-XSS-Protection
        - Cross-Origin policies
        """
        
        https_checks[2] = st.checkbox("☐ Configure security headers", value=https_checks[2], key="check_sec_headers", help=security_headers_tooltip)
        https_checks[3] = st.checkbox("☐ Test HTTPS configuration with SSL Labs or similar tool", value=https_checks[3], key="check_ssl_test")
    
    with st.expander("11. Production Environment Security", expanded=True):
        if "prod_sec_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["prod_sec_checks"] = [False, False, False, False]
        
        prod_sec_checks = st.session_state.checklist_state["prod_sec_checks"]
        prod_sec_checks[0] = st.checkbox("☐ Verify production keys and secrets are different from test environment", value=prod_sec_checks[0], key="check_prod_keys")
        prod_sec_checks[1] = st.checkbox("☐ Properly scope firewall rules to minimize exposure", value=prod_sec_checks[1], key="check_firewall")
        prod_sec_checks[2] = st.checkbox("☐ Configure Azure PAM/PIM for administrative access", value=prod_sec_checks[2], key="check_pam_pim")
        prod_sec_checks[3] = st.checkbox("☐ Remove any test data from production environment", value=prod_sec_checks[3], key="check_test_data")
    
    with st.expander("12. Final Verification", expanded=True):
        if "final_checks" not in st.session_state.checklist_state:
            st.session_state.checklist_state["final_checks"] = [False, False, False, False]
        
        final_checks = st.session_state.checklist_state["final_checks"]
        final_checks[0] = st.checkbox("☐ Run a security scan on all exposed endpoints", value=final_checks[0], key="check_sec_scan")
        final_checks[1] = st.checkbox("☐ Test the bot in Teams", value=final_checks[1], key="check_test_teams")
        final_checks[2] = st.checkbox("☐ Verify resource costs are within budget", value=final_checks[2], key="check_costs")
        final_checks[3] = st.checkbox("☐ Document environment configuration and access procedures", value=final_checks[3], key="check_document")
    
    # Security guidelines section
    st.header("Security Guidelines Reference")
    with st.expander("Network Isolation Guidelines"):
        st.markdown("""
        ### Network Isolation Best Practices
        
        - All services should be protected within a virtual network or using private endpoints
        - API Management should only be accessible through Application Gateway
        - App Service and other PaaS services should have access restrictions configured
        - NSG rules should be configured to allow only necessary traffic
        - Use service endpoints or private endpoints for Azure services (Key Vault, Cosmos DB, etc.)
        """)
    
    with st.expander("WAF & DDoS Configuration"):
        st.markdown("""
        ### Web Application Firewall Configuration
        
        - Configure WAF in block mode with OWASP core rule set
        - Enable DDoS protection
        - For higher protection, consider:
          - Azure WAF with Application Gateway
          - Azure Front Door with WAF
          - CloudFlare Enterprise (approximately $250/month)
        
        ### WAF Rule Configuration
        
        The WAF should be configured to protect against:
        - SQL Injection
        - Cross-site scripting
        - Command injection
        - HTTP request smuggling
        - HTTP protocol violations
        - Bot protection
        - Local/remote file inclusion
        """)
    
    with st.expander("Logging & Monitoring Requirements"):
        st.markdown("""
        ### Minimum Logging Requirements
        
        Logs should be retained for at least 3 months and include:
        - HTTP access logs
        - Error logs
        - Authentication logs
        - Database logs
        - System logs (cron, messages)
        
        ### SIEM Integration
        
        If a SIEM system is available, configure:
        - Log forwarding to SIEM
        - Alert rules in SIEM
        - Regular log review procedures
        
        If no SIEM is available, consider:
        - Azure Monitor
        - Log Analytics
        - Storage account for log archiving
        """)
    
    with st.expander("Security Headers Configuration"):
        st.markdown("""
        ### Required Security Headers
        
        Configure the following headers for all exposed endpoints:
        
        ```
        Cache-Control: no-store
        Content-Security-Policy: default-src 'self'; upgrade-insecure-requests; block-all-mixed-content; connect-src 'self'; img-src 'self'; frame-ancestors 'self'; form-action 'self'; font-src 'self'; style-src 'self'; script-src 'strict-dynamic'; script-src-elem 'self'; report-to default; base-uri 'self';
        Permissions-Policy: geolocation=self
        Referrer-Policy: no-referrer-when-downgrade
        Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
        X-Content-Type-Options: nosniff
        X-Frame-Options: SAMEORIGIN
        X-XSS-Protection: 1; mode=block
        Cross-Origin-Embedder-Policy: require-corp
        Cross-Origin-Opener-Policy: same-origin
        Cross-Origin-Resource-Policy: same-origin
        Access-Control-Allow-Credentials: true
        Access-Control-Allow-Origin: https://trusted-domain.com
        ```
        
        Headers can be configured at:
        1. Application code level
        2. Web server/proxy level
        3. CloudFlare or other WAF
        """)
    
    with st.expander("Production Environment Requirements"):
        st.markdown("""
        ### Production Environment Security
        
        - Production secrets and keys must be different from test environment
        - Administrator access should be restricted to:
          - Azure Bastion
          - Jump server
          - VPN with MFA
        - Implement Azure PAM/PIM for privileged access management
        - Configure least-privilege RBAC for all administrators
        - Enable adaptive MFA for all accounts
        
        ### Firewall Configuration
        
        - Only expose necessary ports to the internet
        - Configure internal-only access for management endpoints
        - For endpoints requiring limited access, configure IP restrictions
        - If access is limited to specific IPs, configure 403 redirect to notification page
        """)

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
        if st.button("Export All Settings", key="export_all_settings_output"):
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

def create_arm_template_section(networking_settings, env, location):
    """Create a section for generating ARM template for Application Gateway
    
    Args:
        networking_settings (dict): Settings from the networking tab
        env (str): Environment (dev, test, etc.)
        location (str): Azure region
    """
    st.markdown("---")
    st.subheader("Application Gateway ARM Template")
    st.info("Generate an ARM template for the Application Gateway with proper configuration.")
    
    # Get values from the networking settings
    agw_name = networking_settings.get('agw_name', f"agw-itz-{env}-jpe-001")
    vnet_name = networking_settings.get('vnet_name', f"vnet-itz-{env}-jpe-001")
    subnet_name = networking_settings.get('subnet_name', f"snet-itz-{env}-jpe-001")
    pip_name = networking_settings.get('pip_name', f"pip-itz-anpi-{env}-jpe-001")
    waf_name = networking_settings.get('waf_name', f"waf-itz-{env}-jpe-001")
    
    # Allow customization of key values with unique keys
    st.subheader("ARM Template Options")
    custom_agw_name = st.text_input("Application Gateway Name", value=agw_name, key="arm_agw_name")
    custom_vnet_name = st.text_input("Virtual Network Name", value=vnet_name, key="arm_vnet_name")
    custom_subnet_name = st.text_input("Subnet Name", value=subnet_name, key="arm_subnet_name")
    custom_pip_name = st.text_input("Public IP Name", value=pip_name, key="arm_pip_name")
    custom_waf_name = st.text_input("WAF Policy Name", value=waf_name, key="arm_waf_name")
    
    # Add button to generate ARM template
    if st.button("Generate ARM Template", key="generate_arm_template"):
        # Import function for generating download link
        from utils import get_arm_template_download_link
        
        # Generate the download link
        download_link = get_arm_template_download_link(
            custom_agw_name,
            custom_vnet_name,
            custom_subnet_name,
            custom_pip_name,
            env.capitalize(),
            location
        )
        
        # Display the download link
        st.markdown(download_link, unsafe_allow_html=True)
        st.success("ARM template generated successfully. Click the download button above to save it.")
        
        # Display deployment instructions directly (not in an expander)
        st.subheader("Deployment Instructions")
        st.markdown(f"""
        ### How to Deploy the ARM Template
        
        1. **Save the template**: Click the download button above to save the ARM template.
        
        2. **Deploy with Azure CLI**:
        ```bash
        az deployment group create \\
          --resource-group $RG_NAME \\
          --template-file appgateway.json
        ```
        
        3. **After deployment, configure WAF policy**:
        ```bash
        # Create WAF policy
        az network application-gateway waf-policy create \\
          --name {custom_waf_name} \\
          --resource-group $RG_NAME \\
          --location {location} \\
          --tags "Environment={env.capitalize()} Project=ITZ-Chatbot" \\
          --policy-settings state=Enabled mode=Prevention requestBodyCheck=false maxRequestBodySizeInKb=128 fileUploadLimitInMb=100
        
        # Update App Gateway to WAF_v2 SKU
        az network application-gateway update \\
          --name {custom_agw_name} \\
          --resource-group $RG_NAME \\
          --sku WAF_v2 \\
          --enable-http2
        
        # Link WAF policy
        WAF_POLICY_ID=$(az network application-gateway waf-policy show --name {custom_waf_name} --resource-group $RG_NAME --query id -o tsv)
        
        az network application-gateway waf-policy-link update \\
          --resource-group $RG_NAME \\
          --gateway-name {custom_agw_name} \\
          --policy $WAF_POLICY_ID
        ```
        
        4. **Configure backend pool with APIM host**:
        ```bash
        # Get the API endpoint from APIM
        APIM_NAME="apim-itz-fjp"
        
        # Get the host using bash parameter expansion (avoids sed issues)
        APIM_GATEWAY_URL=$(az apim show --name $APIM_NAME --resource-group $RG_NAME --query properties.gatewayUrl -o tsv)
        APIM_HOST=${{APIM_GATEWAY_URL#https://}}
        APIM_HOST=${{APIM_HOST%%/*}}
        
        # Add APIM to backend pool
        az network application-gateway address-pool create \\
          --name apim-backend-pool \\
          --gateway-name {custom_agw_name} \\
          --resource-group $RG_NAME \\
          --servers "$APIM_HOST"
        ```
        """)
    
    # Return the customized values for potential use elsewhere
    return {
        'agw_name': custom_agw_name,
        'vnet_name': custom_vnet_name,
        'subnet_name': custom_subnet_name,
        'pip_name': custom_pip_name,
        'waf_name': custom_waf_name
    }