"""
UI components for the Streamlit application.
"""
from datetime import datetime
import streamlit as st
from utils import get_markdown_download_link, generate_jwt_secret, create_markdown_content, get_settings_download_link, get_yaml_download_link, parse_uploaded_settings
from state import update_jwt_secret

def configure_page():
    """Configure the Streamlit page settings"""
    st.set_page_config(page_title="Azure ANPI Bot Infrastructure Generator", layout="wide")
    st.title("Azure ANPI Bot Infrastructure Deployment Generator")
    st.markdown("This tool helps you generate Azure CLI commands for deploying the ANPI Bot infrastructure. Fill in the parameters below and copy the generated commands.")

def create_sidebar():
    """Create and configure the sidebar with environment settings and export/import functionality"""
    with st.sidebar:
        st.header("Environment Settings")
        
        # Add export/import section at the top
        with st.expander("Export/Import Settings", expanded=False):
            # Export settings
            if st.button("Export Settings"):
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
                        f"anpi_settings_{timestamp}.json"
                    )
                    st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("No settings available to export")
            
            # Import settings
            uploaded_file = st.file_uploader("Import Settings", type=["json"])
            if uploaded_file is not None:
                settings = parse_uploaded_settings(uploaded_file)
                if settings:
                    if st.button("Apply Imported Settings"):
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
                        
                        st.success("Settings imported successfully!")
                        st.rerun()
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
    """Create the Basic Resources tab"""
    st.header("Resource Group and Basic Settings")
    env = st.session_state.sidebar_values['env']
    
    rg_name = st.text_input("Resource Group Name", value=f"itz-{env}-jpe-001")
    
    # Corrected tag definitions
    anpi_tag = st.text_input("ANPI Tags", value=f"Project=AnpiBot Environment={env.capitalize()}")
    shared_tag = st.text_input("Shared Tags", value=f"Environment={env.capitalize()} Project=ITZ-Chatbot")
    
    api_base_url = st.text_input("API Base URL", value="https://api-test.fjpservice.net")
    timeout_minutes = st.number_input("Timeout Minutes", value=30, min_value=1, max_value=60)
    
    jwt_issuer = st.text_input("JWT Issuer", value="https://api.botframework.com")
    
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
    
    jwt_expiry_minutes = st.number_input("JWT Expiry Minutes", value=60, min_value=1, max_value=1440)
    
    return {
        'rg_name': rg_name,
        'anpi_tag': anpi_tag,
        'shared_tag': shared_tag,
        'api_base_url': api_base_url,
        'timeout_minutes': timeout_minutes,
        'jwt_issuer': jwt_issuer,
        'jwt_secret_key': jwt_secret_key,
        'jwt_expiry_minutes': jwt_expiry_minutes
    }

def create_networking_tab():
    """Create the Networking tab"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Networking Configuration")
    vnet_name = st.text_input("Virtual Network Name", value=f"vnet-itz-{env}-jpe-001")
    vnet_address_prefix = st.text_input("VNet Address Prefix", value="10.0.0.0/16")
    
    st.subheader("Subnets")
    subnet_name = st.text_input("Subnet Name", value=f"snet-itz-{env}-jpe-001")
    subnet_prefix = st.text_input("Subnet Address Prefix", value="10.0.1.0/24")
    
    st.subheader("Application Gateway")
    pip_name = st.text_input("Public IP Name", value=f"pip-itz-anpi-{env}-jpe-001")
    agw_name = st.text_input("Application Gateway Name", value=f"agw-itz-{env}-jpe-001")
    waf_name = st.text_input("WAF Policy Name", value=f"waf-itz-{env}-jpe-001")
    
    return {
        'vnet_name': vnet_name,
        'vnet_address_prefix': vnet_address_prefix,
        'subnet_name': subnet_name,
        'subnet_prefix': subnet_prefix,
        'pip_name': pip_name,
        'agw_name': agw_name,
        'waf_name': waf_name
    }

def create_app_service_tab():
    """Create the App Service tab"""
    env = st.session_state.sidebar_values['env']
    
    st.header("App Service Configuration")
    asp_name = st.text_input("App Service Plan Name", value=f"asp-itz-{env}-001")
    asp_sku = st.selectbox("App Service Plan SKU", ["B1", "S1", "P1V2", "P2V2", "P3V2"])
    
    app_name = st.text_input("Web App Name", value=f"app-itz-anpi-{env}-001")
    app_runtime = st.selectbox("App Runtime", ["DOTNETCORE|6.0", "DOTNETCORE|7.0", "DOTNETCORE|8.0", "NODE|14-lts", "NODE|16-lts"])
    
    st.subheader("Application Insights")
    appinsights_name = st.text_input("Application Insights Name", value=f"appi-itz-anpi-{env}-jpe-001")
    
    bot_name = st.text_input("Bot Service Name", value=f"bot-itz-anpi-{env}")
    
    return {
        'asp_name': asp_name,
        'asp_sku': asp_sku,
        'app_name': app_name,
        'app_runtime': app_runtime,
        'appinsights_name': appinsights_name,
        'bot_name': bot_name
    }

def create_data_ai_tab():
    """Create the Data and AI Services tab"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Data and AI Services")
    
    st.subheader("Key Vault")
    kv_name = st.text_input("Key Vault Name", value=f"kv-itz-{env}-jpe-001")
    
    st.subheader("Cosmos DB")
    cosmos_name = st.text_input("Cosmos DB Account Name", value=f"cosmos-itz-{env}")
    cosmos_db_name = st.text_input("Cosmos DB Database Name", value="AnpiDb")
    
    st.subheader("Azure OpenAI")
    openai_name = st.text_input("OpenAI Service Name", value=f"oai-itz-{env}")
    openai_model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o", "gpt-35-turbo", "gpt-4"])
    model_version = st.text_input("Model Version", value="2024-07-18")
    embedding_model = st.text_input("Embedding Model", value="text-embedding-ada-002")
    embedding_model_version = st.number_input("Embedding Model Version", value=2, min_value=1)
    
    st.subheader("Azure Search")
    search_name = st.text_input("Search Service Name", value=f"srch-itz-{env}")
    search_sku = st.selectbox("Search SKU", ["Basic", "Standard", "Standard2", "Standard3"])
    search_index_name = st.text_input("Search Index Name", value="anpi-knowledge")
    semantic_config_name = st.text_input("Semantic Config Name", value="my-semantic-config")
    
    return {
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

def create_api_management_tab():
    """Create the API Management tab with fields from ARM template"""
    st.header("API Management")
    
    apim_name = st.text_input("API Management Name", value="apim-itz")
    
    # Updated SKU options to include Consumption per ARM template
    apim_sku = st.selectbox("API Management SKU", ["Consumption", "Developer", "Basic", "Standard", "Premium"])
    
    # Updated with publisher details from the ARM template
    apim_publisher_email = st.text_input("Publisher Email", value="tuyendhq@fpt.com")
    apim_publisher_name = st.text_input("Publisher Name", value="FJP Japan Holding")
    
    api_id = st.text_input("API ID", value="anpi-bot-api")
    api_path = st.text_input("API Path", value="anpi")
    api_display_name = st.text_input("API Display Name", value="ANPI Bot API")
    
    allowed_origins = st.text_area("Allowed Origins (JSON array)", value='["https://*.fjpservice.net","https://localhost:4200"]')
    
    # Save to session state for yaml generation
    st.session_state['apim_name'] = apim_name
    st.session_state['api_path'] = api_path
    st.session_state['api_id'] = api_id
    st.session_state['api_display_name'] = api_display_name
    
    return {
        'apim_name': apim_name,
        'apim_sku': apim_sku,
        'apim_publisher_email': apim_publisher_email,
        'apim_publisher_name': apim_publisher_name,
        'api_id': api_id,
        'api_path': api_path,
        'api_display_name': api_display_name,
        'allowed_origins': allowed_origins
    }
    
def create_teams_integration_tab():
    """Create the Teams Integration tab"""
    env = st.session_state.sidebar_values['env']
    
    st.header("Teams Integration")
    teams_app_name = st.text_input("Teams App Name", value=f"ANPI Teams Bot {env.capitalize()}")
    teams_redirect_uri = st.text_input("Teams Redirect URI", value="https://token.botframework.com/.auth/web/redirect")
    
    return {
        'teams_app_name': teams_app_name,
        'teams_redirect_uri': teams_redirect_uri
    }

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
            # Collect all settings from session state
            all_settings = {
                "environment": st.session_state.sidebar_values,
                "basic_resources": {k: v for k, v in st.session_state.items() if k.startswith("basic_")},
                "networking": {k: v for k, v in st.session_state.items() if k.startswith("net_")},
                "app_service": {k: v for k, v in st.session_state.items() if k.startswith("app_")},
                "data_ai": {k: v for k, v in st.session_state.items() if k.startswith("data_") or k.startswith("ai_")},
                "api_management": {k: v for k, v in st.session_state.items() if k.startswith("api_")},
                "teams_integration": {k: v for k, v in st.session_state.items() if k.startswith("teams_")}
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_link = get_settings_download_link(
                all_settings, 
                f"anpi_full_settings_{timestamp}.json"
            )
            st.markdown(download_link, unsafe_allow_html=True)
    
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