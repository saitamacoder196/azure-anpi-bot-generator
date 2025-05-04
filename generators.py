"""
Script generator functions for Azure infrastructure components.
This module contains functions to generate various Azure CLI scripts.
"""
from datetime import datetime

def generate_environment_vars(env, subscription_id, location, rg_name, 
                              anpi_tag, shared_tag, ms_app_id, ms_app_password, 
                              ms_app_tenant_id, openai_model, model_version, 
                              embedding_model, embedding_model_version):
    """Generate environment variables script section"""
    return f"""# Set environment name and basic settings
ENV="{env}"
SUBSCRIPTION_ID="{subscription_id}"
LOCATION="{location}"
RG_NAME="{rg_name}"
ENVIRONMENT="{env.capitalize()}"

# Shared Tags
SHARED_TAG="{shared_tag}"
ANPI_TAG="{anpi_tag}"

# Bot Framework Settings
MS_APP_TYPE="SingleTenant"
MS_APP_ID="{ms_app_id}"
MS_APP_PASSWORD="{ms_app_password}"
MS_APP_TENANT_ID="{ms_app_tenant_id}"

# Azure OpenAI Settings
AZURE_OPENAI_MODEL="{openai_model}"
MODEL_VERSION="{model_version}"
EMBEDDING_MODEL="{embedding_model}"
EMBEDDING_MODEL_VERSION={embedding_model_version}
"""

def generate_resource_group():
    """Generate resource group script section"""
    return """
# Set Azure subscription
az account set --subscription "$SUBSCRIPTION_ID"

# Create Resource Group
az group create --name $RG_NAME --location $LOCATION --tags "$SHARED_TAG"

# Verification:
# Azure Portal: Go to Resource Groups and search for the resource group
# CLI Verification:
az group show --name $RG_NAME -o table
"""

def generate_networking(vnet_name, vnet_address_prefix, subnet_name, 
                      subnet_prefix, pip_name, agw_name, waf_name, apim_name, app_name, env):
    """Generate networking script section with App Service backend configured"""
    return f"""
# Create Virtual Network
az network vnet create \\
  --name {vnet_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --address-prefix {vnet_address_prefix} \\
  --tags "$SHARED_TAG"

# Create subnet
az network vnet subnet create \\
  --name {subnet_name} \\
  --resource-group $RG_NAME \\
  --vnet-name {vnet_name} \\
  --address-prefix {subnet_prefix}

# Create Public IP for Application Gateway
az network public-ip create \\
  --name {pip_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --allocation-method Static \\
  --sku Standard \\
  --zone 1 2 3 \\
  --dns-name anpi-{env.lower()} \\
  --tags "$SHARED_TAG"

# Create WAF policy with correct parameter format
az network application-gateway waf-policy create \\
  --name {waf_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --tags "Environment=$ENVIRONMENT Project=ITZ-Chatbot" \\
  --policy-settings state=Enabled mode=Prevention requestBodyCheck=false maxRequestBodySizeInKb=128 fileUploadLimitInMb=100

# Get WAF policy ID for use in Application Gateway creation
WAF_POLICY_ID=$(az network application-gateway waf-policy show --name {waf_name} --resource-group $RG_NAME --query id -o tsv)

# Get the API endpoint from APIM for backend configuration - using more compatible approach
APIM_HOST=$(az apim show --name {apim_name} --resource-group $RG_NAME --query hostname -o tsv)

# If the above doesn't work (depends on Azure CLI version), try this alternative:
if [ -z "$APIM_HOST" ]; then
  # Get the full URL and extract just the hostname part using bash string manipulation
  APIM_GATEWAY_URL=$(az apim show --name {apim_name} --resource-group $RG_NAME --query properties.gatewayUrl -o tsv)
  APIM_HOST=${{APIM_GATEWAY_URL#https://}}
  # Use string replacement to remove any path component if present
  APIM_HOST=${{APIM_HOST%%/*}}
fi

# Use a simpler approach for the initial Application Gateway
echo "Creating Application Gateway with minimal configuration..."

# Create a default Application Gateway with priority specified for the routing rule
az network application-gateway create \\
  --name {agw_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --vnet-name {vnet_name} \\
  --subnet {subnet_name} \\
  --public-ip-address {pip_name} \\
  --sku Standard_v2 \\
  --capacity 2 \\
  --frontend-port 80 \\
  --http-settings-cookie-based-affinity Disabled \\
  --http-settings-port 80 \\
  --http-settings-protocol Http \\
  --routing-rule-type Basic \\
  --routing-rule-priority 100 \\
  --tags "Project=AnpiBot Environment=$ENVIRONMENT" "Environment=$ENVIRONMENT Project=ITZ-Chatbot"

# Then upgrade to WAF_v2 with WAF policy
echo "Upgrading to WAF_v2 and configuring advanced settings..."
az network application-gateway update \\
  --name {agw_name} \\
  --resource-group $RG_NAME \\
  --sku WAF_v2 \\
  --enable-http2

# Set autoscale configuration
echo "Setting autoscale configuration..."
az network application-gateway autoscale-configuration update \\
  --gateway-name {agw_name} \\
  --resource-group $RG_NAME \\
  --min-capacity 0 \\
  --max-capacity 10

# Set availability zones
echo "Setting availability zones..."
az network application-gateway update \\
  --name {agw_name} \\
  --resource-group $RG_NAME \\
  --zones 1 2 3

# Then update the Application Gateway to attach the WAF policy
echo "Linking WAF policy..."
az network application-gateway waf-policy-link update \\
  --resource-group $RG_NAME \\
  --gateway-name {agw_name} \\
  --policy $WAF_POLICY_ID

# Get name of the default HTTP listener
LISTENER_NAME=$(az network application-gateway http-listener list \\
  --gateway-name {agw_name} \\
  --resource-group $RG_NAME \\
  --query "[0].name" -o tsv)

# Get name of the default HTTP settings
HTTP_SETTINGS_NAME=$(az network application-gateway http-settings list \\
  --gateway-name {agw_name} \\
  --resource-group $RG_NAME \\
  --query "[0].name" -o tsv)

# Update the backend pool to point to APIM backend
az network application-gateway address-pool create \\
  --name apim-backend-pool \\
  --gateway-name {agw_name} \\
  --resource-group $RG_NAME \\
  --servers "$APIM_HOST" \\
  --priority 200

# Create a new rule to use our APIM backend pool
az network application-gateway rule create \\
  --gateway-name {agw_name} \\
  --resource-group $RG_NAME \\
  --name "apim-rule" \\
  --http-listener "$LISTENER_NAME" \\
  --http-settings "$HTTP_SETTINGS_NAME" \\
  --address-pool "apim-backend-pool" \\
  --priority 100 \\
  --rule-type Basic

# Verification:
# Azure Portal: 
# - Go to Virtual Networks and check {vnet_name}
# - Go to Application Gateway and check {agw_name}
# - Go to Public IP addresses and check {pip_name}

# CLI Verification:
az network vnet show --name {vnet_name} --resource-group $RG_NAME -o table
az network vnet subnet show --name {subnet_name} --resource-group $RG_NAME --vnet-name {vnet_name} -o table
az network public-ip show --name {pip_name} --resource-group $RG_NAME -o table
az network application-gateway show --name {agw_name} --resource-group $RG_NAME -o table
az network application-gateway address-pool list --gateway-name {agw_name} --resource-group $RG_NAME -o table
az network application-gateway waf-policy show --name {waf_name} --resource-group $RG_NAME -o table
az network application-gateway rule list --gateway-name {agw_name} --resource-group $RG_NAME -o table
"""

def generate_app_service(asp_name, asp_sku, appinsights_name):
    """Generate app service script section"""
    return f"""
# Create App Service Plan
az appservice plan create \\
  --name {asp_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --sku {asp_sku} \\
  --is-linux \\
  --tags "$SHARED_TAG"

# Create Application Insights
az monitor app-insights component create \\
  --app {appinsights_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --application-type web \\
  --tags "$SHARED_TAG"

# Get Application Insights Instrumentation Key
APPINSIGHTS_KEY=$(az monitor app-insights component show \\
  --app {appinsights_name} \\
  --resource-group $RG_NAME \\
  --query instrumentationKey -o tsv)

# Get Application Insights Connection String
APPINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \\
  --app {appinsights_name} \\
  --resource-group $RG_NAME \\
  --query connectionString -o tsv)

# Verification:
# Azure Portal: 
# - Go to App Service Plans and check {asp_name}
# - Go to Application Insights and check {appinsights_name}

# CLI Verification:
az appservice plan show --name {asp_name} --resource-group $RG_NAME -o table
az monitor app-insights component show --app {appinsights_name} --resource-group $RG_NAME -o table
echo $APPINSIGHTS_KEY
echo $APPINSIGHTS_CONNECTION_STRING
"""

def generate_data_ai_services(kv_name, cosmos_name, cosmos_db_name, openai_name, 
                           openai_model, model_version, embedding_model, 
                           embedding_model_version, search_name, search_sku, 
                           search_index_name, semantic_config_name):
    """Generate data and AI services script section"""
    return f"""
# Create Key Vault
az keyvault create \\
  --name {kv_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --tags "$SHARED_TAG"

# Create CosmosDB Account
az cosmosdb create \\
  --name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --locations regionName=$LOCATION \\
  --tags "$SHARED_TAG"

# Create database
az cosmosdb sql database create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --name {cosmos_db_name}

# Create required containers based on application needs
# Example: Create 'users' container
az cosmosdb sql container create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --database-name {cosmos_db_name} \\
  --name users \\
  --partition-key-path "/partitionKey"

# Create other required containers
az cosmosdb sql container create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --database-name {cosmos_db_name} \\
  --name conversations \\
  --partition-key-path "/id"

az cosmosdb sql container create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --database-name {cosmos_db_name} \\
  --name events \\
  --partition-key-path "/partitionKey"

az cosmosdb sql container create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --database-name {cosmos_db_name} \\
  --name responses \\
  --partition-key-path "/eventId"

az cosmosdb sql container create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --database-name {cosmos_db_name} \\
  --name chatLogs \\
  --partition-key-path "/userId"

az cosmosdb sql container create \\
  --account-name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --database-name {cosmos_db_name} \\
  --name knowledge \\
  --partition-key-path "/partitionKey"

# Get CosmosDB Connection String
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \\
  --name {cosmos_name} \\
  --resource-group $RG_NAME \\
  --type connection-strings \\
  --query connectionStrings[0].connectionString -o tsv)

# Create OpenAI service
az cognitiveservices account create \\
  --name {openai_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --kind OpenAI \\
  --sku S0 \\
  --tags "$SHARED_TAG"

# Get Azure OpenAI endpoint and key
AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \\
  --name {openai_name} \\
  --resource-group $RG_NAME \\
  --query properties.endpoint -o tsv)

AZURE_OPENAI_KEY=$(az cognitiveservices account keys list \\
  --name {openai_name} \\
  --resource-group $RG_NAME \\
  --query key1 -o tsv)

# Create OpenAI model deployments
az cognitiveservices account deployment create \\
  --name {openai_name} \\
  --resource-group $RG_NAME \\
  --deployment-name $AZURE_OPENAI_MODEL \\
  --model-name $AZURE_OPENAI_MODEL \\
  --model-version $MODEL_VERSION \\
  --model-format OpenAI \\
  --sku-name Standard \\
  --sku-capacity 1

az cognitiveservices account deployment create \\
  --name {openai_name} \\
  --resource-group $RG_NAME \\
  --deployment-name $EMBEDDING_MODEL \\
  --model-name $EMBEDDING_MODEL \\
  --model-version $EMBEDDING_MODEL_VERSION \\
  --model-format OpenAI \\
  --sku-name Standard \\
  --sku-capacity 1

# Create Azure Search service
az search service create \\
  --name {search_name} \\
  --resource-group $RG_NAME \\
  --location $LOCATION \\
  --sku {search_sku} \\
  --tags "$SHARED_TAG"

# Get Azure Search key
AZURE_SEARCH_KEY=$(az search admin-key show \\
  --service-name {search_name} \\
  --resource-group $RG_NAME \\
  --query primaryKey -o tsv)

AZURE_SEARCH_ENDPOINT="https://{search_name}.search.windows.net"

# Create a json file for index definition
cat > /tmp/search-index.json << EOF
{{
  "name": "{search_index_name}",
  "fields": [
    {{
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": true,
      "filterable": true,
      "sortable": true
    }},
    {{
      "name": "title",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true
    }},
    {{
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "sortable": false
    }},
    {{
      "name": "category",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true
    }},
    {{
      "name": "language",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true
    }},
    {{
      "name": "tags",
      "type": "Collection(Edm.String)",
      "searchable": true,
      "filterable": true,
      "sortable": false
    }},
    {{
      "name": "embedding",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "dimensions": 1536,
      "vectorSearchConfiguration": "vector-config"
    }}
  ],
  "vectorSearch": {{
    "algorithmConfigurations": [
      {{
        "name": "vector-config",
        "kind": "hnsw"
      }}
    ]
  }},
  "semantic": {{
    "configurations": [
      {{
        "name": "{semantic_config_name}",
        "prioritizedFields": {{
          "titleField": {{
            "fieldName": "title"
          }},
          "contentFields": [
            {{
              "fieldName": "content"
            }}
          ],
          "keywordsFields": [
            {{
              "fieldName": "category"
            }},
            {{
              "fieldName": "tags"
            }}
          ]
        }}
      }}
    ]
  }}
}}
EOF

# Create the index using REST API
az rest --method put \\
  --uri "${{AZURE_SEARCH_ENDPOINT}}/indexes/{search_index_name}?api-version=2023-07-01-Preview" \\
  --headers "Content-Type=application/json" "api-key=${{AZURE_SEARCH_KEY}}" \\
  --body @/tmp/search-index.json

# Clean up
rm /tmp/search-index.json

# Verification:
# Azure Portal:
# - Go to Key Vaults and check {kv_name}
# - Go to Azure Cosmos DB and check {cosmos_name}
# - Go to Azure OpenAI and check {openai_name}
# - Go to Azure AI Search and check {search_name}

# CLI Verification:
az keyvault show --name {kv_name} --resource-group $RG_NAME -o table
az cosmosdb show --name {cosmos_name} --resource-group $RG_NAME -o table
az cosmosdb sql database show --name {cosmos_db_name} --account-name {cosmos_name} --resource-group $RG_NAME -o table
az cosmosdb sql container list --database-name {cosmos_db_name} --account-name {cosmos_name} --resource-group $RG_NAME -o table
az cognitiveservices account show --name {openai_name} --resource-group $RG_NAME -o table
az cognitiveservices account deployment list --name {openai_name} --resource-group $RG_NAME -o table
az search service show --name {search_name} --resource-group $RG_NAME -o table
az search index show --name {search_index_name} --service-name {search_name} --resource-group $RG_NAME -o table
"""

def generate_api_management(apim_name, apim_sku, apim_publisher_email, 
                          apim_publisher_name, api_id, api_path, api_display_name, location, app_name):
    """Generate API management script section based on ARM template"""
    return f"""
# Create API Management service
az apim create \\
  --name {apim_name} \\
  --resource-group $RG_NAME \\
  --location {location} \\
  --publisher-email "{apim_publisher_email}" \\
  --publisher-name "{apim_publisher_name}" \\
  --sku-name {apim_sku} \\
  --tags "$SHARED_TAG" "Project=AnpiBot Environment=$ENVIRONMENT"

# Lưu ý: API và Operations
# Thay vì sử dụng CLI, bạn nên tải lên tệp YAML để cấu hình API và Operations
# thông qua Azure Portal
# Các bước thực hiện:
# 1. Truy cập Azure Portal
# 2. Vào API Management service đã tạo
# 3. Trong phần API Management, chọn APIs
# 4. Chọn "Import" và tải lên tệp YAML đã chuẩn bị
#
# Bạn có thể tải xuống tệp YAML mẫu từ nút bên dưới và chỉnh sửa nó.
# Tệp YAML chứa các đường dẫn API sau:
# - API Authentication: /api/auth/token, /api/auth/refresh-token, /api/auth/validate
# - API Broadcast: /api/broadcast/anpi-confirms, /api/broadcast/leaderships-earthquakealert,
#                  /api/broadcast/leaderships-statusreport, /api/broadcast/notify
# - API Health: /api/alive, /api/alive/version, /api/alive/status
# - API Bot: /api/messages
#
# Lưu ý rằng bạn cần thay đổi các biến sau trong file YAML:
# - servers.url: Đã được cấu hình với 2 URL:
#   1. URL của APIM: https://{apim_name}.azure-api.net/{api_path}
#   2. URL của App Service: https://{app_name}.azurewebsites.net

# CLI Verification:
az apim show --name {apim_name} --resource-group $RG_NAME -o table
az apim api show --api-id {api_id} --service-name {apim_name} --resource-group $RG_NAME -o table
az apim api operation list --api-id {api_id} --service-name {apim_name} --resource-group $RG_NAME -o table
"""

def generate_web_app(app_name, asp_name, app_runtime, kv_name, 
                   apim_name, api_id, allowed_origins, jwt_issuer, 
                   jwt_expiry_minutes, cosmos_db_name, search_index_name, 
                   semantic_config_name, api_base_url, timeout_minutes, jwt_secret_key):
    """Generate web app script section"""
    return f"""
# Create Web App
az webapp create \\
  --name {app_name} \\
  --resource-group $RG_NAME \\
  --plan {asp_name} \\
  --runtime "{app_runtime}" \\
  --tags "$ANPI_TAG"

# Assign managed identity
az webapp identity assign \\
  --name {app_name} \\
  --resource-group $RG_NAME

# Get the principal ID for permissions
APP_PRINCIPAL_ID=$(az webapp identity show \\
  --name {app_name} \\
  --resource-group $RG_NAME \\
  --query principalId -o tsv)

# Create backend for App Service
APP_SERVICE_URL="https://{app_name}.azurewebsites.net"
az apim backend create \\
  --resource-group $RG_NAME \\
  --service-name "{apim_name}" \\
  --backend-id "anpi-app-service" \\
  --url "$APP_SERVICE_URL" \\
  --protocol http \\
  --description "ANPI Bot App Service"

# Set API Policy to use backend
cat > /tmp/apim-policy.xml << EOF
<policies>
  <inbound>
    <base />
    <set-backend-service backend-id="anpi-app-service" />
    <cors>
      <allowed-origins>
        <origin>https://*.fjpservice.net</origin>
        <origin>https://localhost:4200</origin>
      </allowed-origins>
      <allowed-methods>
        <method>GET</method>
        <method>POST</method>
        <method>PUT</method>
        <method>DELETE</method>
        <method>PATCH</method>
        <method>OPTIONS</method>
      </allowed-methods>
      <allowed-headers>
        <header>Content-Type</header>
        <header>Authorization</header>
      </allowed-headers>
      <expose-headers>
        <header>*</header>
      </expose-headers>
    </cors>
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
EOF

az apim api policy set \\
  --resource-group $RG_NAME \\
  --service-name "{apim_name}" \\
  --api-id "{api_id}" \\
  --value-file /tmp/apim-policy.xml

rm /tmp/apim-policy.xml

# Store secrets in Key Vault
az keyvault secret set --vault-name {kv_name} --name anpi-MicrosoftAppId --value "$MS_APP_ID"
az keyvault secret set --vault-name {kv_name} --name anpi-MicrosoftAppPassword --value "$MS_APP_PASSWORD"
az keyvault secret set --vault-name {kv_name} --name anpi-MicrosoftAppTenantId --value "$MS_APP_TENANT_ID"
az keyvault secret set --vault-name {kv_name} --name anpi-JwtSecretKey --value "{jwt_secret_key}"
az keyvault secret set --vault-name {kv_name} --name anpi-CosmosDbConnectionString --value "$COSMOS_CONNECTION_STRING"
az keyvault secret set --vault-name {kv_name} --name anpi-AzureOpenAIKey --value "$AZURE_OPENAI_KEY"
az keyvault secret set --vault-name {kv_name} --name anpi-AzureSearchApiKey --value "$AZURE_SEARCH_KEY"

# Grant Key Vault access to App Service
az role assignment create \\
  --assignee-object-id "$APP_PRINCIPAL_ID" \\
  --assignee-principal-type ServicePrincipal \\
  --scope "$(az keyvault show --name {kv_name} --resource-group $RG_NAME --query id -o tsv)" \\
  --role "Key Vault Secrets User"

# Get Key Vault URI for App Settings
KV_URI=$(az keyvault show --name {kv_name} --query properties.vaultUri -o tsv)

# Configure application settings
az webapp config appsettings set \\
  --name {app_name} \\
  --resource-group $RG_NAME \\
  --settings \\
  MicrosoftAppId="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-MicrosoftAppId/)" \\
  MicrosoftAppPassword="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-MicrosoftAppPassword/)" \\
  MicrosoftAppTenantId="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-MicrosoftAppTenantId/)" \\
  CosmosDbConnectionString="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-CosmosDbConnectionString/)" \\
  APPINSIGHTS_INSTRUMENTATIONKEY="$APPINSIGHTS_KEY" \\
  APPLICATIONINSIGHTS_CONNECTION_STRING="$APPINSIGHTS_CONNECTION_STRING" \\
  Environment="$ENVIRONMENT" \\
  ApplicationName="ANPI Bot ${{ENVIRONMENT}}" \\
  ApiBaseUrl="{api_base_url}" \\
  TimeoutMinutes="{timeout_minutes}" \\
  AllowedOrigins='{allowed_origins}' \\
  JwtSettings__Issuer="{jwt_issuer}" \\
  JwtSettings__Audience="$MS_APP_ID" \\
  JwtSettings__SecretKey="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-JwtSecretKey/)" \\
  JwtSettings__ExpiryInMinutes="{jwt_expiry_minutes}" \\
  CosmosDb__DatabaseName="{cosmos_db_name}" \\
  AzureOpenAI__Endpoint="$AZURE_OPENAI_ENDPOINT" \\
  AzureOpenAI__Key="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-AzureOpenAIKey/)" \\
  AzureOpenAI__DeploymentId="$AZURE_OPENAI_MODEL" \\
  AzureOpenAI__ApiVersion="2024-02-15-preview" \\
  AzureOpenAI__EmbeddingApiVersion="2023-05-15" \\
  AzureOpenAI__EmbeddingDeploymentId="$EMBEDDING_MODEL" \\
  AzureSearch__Endpoint="$AZURE_SEARCH_ENDPOINT" \\
  AzureSearch__ApiKey="@Microsoft.KeyVault(SecretUri=${{KV_URI}}secrets/anpi-AzureSearchApiKey/)" \\
  AzureSearch__IndexName="{search_index_name}" \\
  AzureSearch__SemanticConfig="{semantic_config_name}" \\
  SCM_ENABLED=true

# Verification:
# Azure Portal:
# - Go to App Services and check {app_name}
# - Check App Service > Configuration for app settings
# - Check Identity settings are enabled
# - Check Key Vault for stored secrets

# CLI Verification:
az webapp show --name {app_name} --resource-group $RG_NAME -o table
az webapp identity show --name {app_name} --resource-group $RG_NAME -o table
az webapp config appsettings list --name {app_name} --resource-group $RG_NAME -o table
az keyvault secret list --vault-name {kv_name} -o table
az apim backend show --backend-id anpi-app-service --service-name {apim_name} --resource-group $RG_NAME -o table
"""

def generate_bot_service(bot_name, app_name, apim_name, api_id):
    """Generate bot service script section"""
    return f"""
# Create Bot Service
az bot create \\
  --resource-group $RG_NAME \\
  --name {bot_name} \\
  --appid "$MS_APP_ID" \\
  --endpoint "https://{app_name}.azurewebsites.net/api/messages" \\
  --app-type SingleTenant \\
  --tenant-id "$MS_APP_TENANT_ID"

# Get APIM API URL
APIM_API_URL=$(az apim api show \\
  --resource-group $RG_NAME \\
  --service-name "{apim_name}" \\
  --api-id "{api_id}" \\
  --query serviceUrl -o tsv)

APIM_MESSAGES_ENDPOINT="$APIM_API_URL/api/messages"

# Update Bot Service to use APIM URL
az bot update \\
  --resource-group $RG_NAME \\
  --name {bot_name} \\
  --endpoint "$APIM_MESSAGES_ENDPOINT"

# Verification:
# Azure Portal:
# - Go to Azure Bot Services and check {bot_name}
# - Verify the endpoint is correctly configured to use APIM

# CLI Verification:
az bot show --name {bot_name} --resource-group $RG_NAME -o table
# Verify the endpoint points to APIM
az bot show --name {bot_name} --resource-group $RG_NAME --query properties.endpoint -o tsv
"""

def generate_teams_integration(teams_app_name, teams_redirect_uri, kv_name):
    """Generate teams integration script section"""
    return f"""
# Create App Registration for Teams
az ad app create \\
  --display-name "{teams_app_name}" \\
  --sign-in-audience AzureADMyOrg \\
  --web-redirect-uris "{teams_redirect_uri}"

# Get the app ID
TEAMS_APP_ID=$(az ad app show --display-name "{teams_app_name}" --query appId -o tsv)

# Create App Secret
TEAMS_APP_SECRET=$(az ad app credential reset --id $TEAMS_APP_ID --credential-description "Bot secret" --query password -o tsv)

# Store Teams app credentials in Key Vault
az keyvault secret set --vault-name {kv_name} --name anpi-TeamsAppId --value "$TEAMS_APP_ID"
az keyvault secret set --vault-name {kv_name} --name anpi-TeamsAppSecret --value "$TEAMS_APP_SECRET"

# Verification:
# Azure Portal:
# - Go to Azure Active Directory > App Registrations and check for {teams_app_name}
# - Check Key Vault for Teams app secrets

# CLI Verification:
az ad app list --display-name "{teams_app_name}" -o table
az keyvault secret show --vault-name {kv_name} --name anpi-TeamsAppId --query value -o tsv
"""

def generate_network_verification(app_name, kv_name, cosmos_name, cosmos_db_name, 
                                apim_name, agw_name, pip_name, search_name, api_path):
    """Generate network verification script section"""
    return f"""
# ===== Network and Resource Connectivity Verification =====

echo "Starting network and connectivity verification..."

# 1. Verify App Service can access Key Vault
echo "Verifying App Service to Key Vault connectivity..."
APP_IDENTITY_ASSIGNMENTS=$(az webapp identity show --name {app_name} --resource-group $RG_NAME --query principalId -o tsv)
KV_ACCESS_POLICIES=$(az keyvault show --name {kv_name} --resource-group $RG_NAME --query properties.accessPolicies -o json)

if [[ $APP_IDENTITY_ASSIGNMENTS && $KV_ACCESS_POLICIES == *"$APP_IDENTITY_ASSIGNMENTS"* ]]; then
  echo "✅ App Service has proper identity assignment to access Key Vault"
else
  echo "❌ App Service is missing proper Key Vault access. Check managed identity configuration."
fi

# 2. Verify App Service can access Cosmos DB 
echo "Verifying App Service can access Cosmos DB..."
# Create a simple test function in the app to check Cosmos DB connectivity
cat > /tmp/cosmos-test.cs << EOF
using Microsoft.Azure.Cosmos;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/diagnostics")]
public class DiagnosticsController : ControllerBase
{{
    private readonly CosmosClient _cosmosClient;
    
    public DiagnosticsController(CosmosClient cosmosClient)
    {{
        _cosmosClient = cosmosClient;
    }}
    
    [HttpGet("cosmos-test")]
    public async Task<IActionResult> TestCosmosConnection()
    {{
        try
        {{
            // Try to access the database
            var db = _cosmosClient.GetDatabase("{cosmos_db_name}");
            var response = await db.ReadAsync();
            return Ok(new {{ Status = "Connected", DatabaseName = response.Resource.Id }});
        }}
        catch (Exception ex)
        {{
            return StatusCode(500, new {{ Status = "Failed", Error = ex.Message }});
        }}
    }}
}}
EOF

echo "Diagnostic endpoint code has been written to /tmp/cosmos-test.cs"
echo "Please add this file to your project and deploy it to verify Cosmos DB connectivity."
echo "After deployment, access: https://{app_name}.azurewebsites.net/api/diagnostics/cosmos-test"

# 3. Verify App Service can access OpenAI Service
echo "Verifying App Service can access OpenAI Service..."
# Create a simple test function for OpenAI connectivity
cat > /tmp/openai-test.cs << EOF
using Microsoft.AspNetCore.Mvc;
using Azure.AI.OpenAI;
using Azure;

[ApiController]
[Route("api/diagnostics")]
public class OpenAIDiagnosticsController : ControllerBase
{{
    private readonly OpenAIClient _openAIClient;
    private readonly IConfiguration _configuration;
    
    public OpenAIDiagnosticsController(OpenAIClient openAIClient, IConfiguration configuration)
    {{
        _openAIClient = openAIClient;
        _configuration = configuration;
    }}
    
    [HttpGet("openai-test")]
    public async Task<IActionResult> TestOpenAIConnection()
    {{
        try
        {{
            var deploymentId = _configuration["AzureOpenAI:DeploymentId"];
            var response = await _openAIClient.GetCompletionsAsync(
                deploymentId, 
                new CompletionsOptions("Hello, world")
                {{
                    MaxTokens = 5
                }}
            );
            
            return Ok(new {{ 
                Status = "Connected", 
                Model = deploymentId,
                Response = response.Value.Choices[0].Text
            }});
        }}
        catch (Exception ex)
        {{
            return StatusCode(500, new {{ Status = "Failed", Error = ex.Message }});
        }}
    }}
}}
EOF

echo "OpenAI test endpoint code has been written to /tmp/openai-test.cs"
echo "Please add this file to your project and deploy it to verify OpenAI connectivity."
echo "After deployment, access: https://{app_name}.azurewebsites.net/api/diagnostics/openai-test"

# 4. Verify API Management can reach App Service
echo "Verifying API Management can reach App Service..."
APIM_BACKEND=$(az apim backend show --backend-id anpi-app-service --service-name {apim_name} --resource-group $RG_NAME --query url -o tsv)
APP_URL="https://{app_name}.azurewebsites.net"

if [[ "$APIM_BACKEND" == "$APP_URL" ]]; then
  echo "✅ API Management backend is correctly configured to App Service URL"
else
  echo "❌ API Management backend URL doesn't match App Service URL. Check configuration."
  echo "APIM Backend URL: $APIM_BACKEND"
  echo "App Service URL: $APP_URL"
fi

# Test API call through APIM - using more compatible approach
# Get Gateway URL without using sed
APIM_URL=$(az apim show --name {apim_name} --resource-group $RG_NAME --query "properties.gatewayUrl" -o tsv)

# If empty, construct the URL from hostname
if [ -z "$APIM_URL" ]; then
  APIM_HOSTNAME=$(az apim show --name {apim_name} --resource-group $RG_NAME --query "properties.hostnameConfigurations[0].hostName" -o tsv)
  if [ -n "$APIM_HOSTNAME" ]; then
    APIM_URL="https://$APIM_HOSTNAME"
  else
    # Fallback to constructing from name
    APIM_URL="https://{apim_name}.azure-api.net"
  fi
fi

echo "To test API Management connectivity to App Service, run:"
echo "curl -v $APIM_URL/{api_path}/api/alive"

# 5. Test Application Gateway connectivity
echo "Verifying Application Gateway connectivity..."
AGW_PUBLIC_IP=$(az network public-ip show --name {pip_name} --resource-group $RG_NAME --query ipAddress -o tsv)
BACKEND_POOL=$(az network application-gateway address-pool list --gateway-name {agw_name} --resource-group $RG_NAME -o json)

echo "Application Gateway Public IP: $AGW_PUBLIC_IP"
echo "To test Application Gateway connectivity, open a browser and navigate to:"
echo "http://$AGW_PUBLIC_IP/api/alive"

# Additional network diagnostic information
echo "Generating network diagnostic information..."

# DNS resolution test
echo "Testing DNS resolution for resources..."
for domain in $(echo "{app_name}.azurewebsites.net {apim_name}.azure-api.net {kv_name}.vault.azure.net {cosmos_name}.documents.azure.com {search_name}.search.windows.net"); do
  echo "Resolving $domain..."
  nslookup $domain || echo "Could not resolve $domain"
done

echo "Network connectivity verification completed. Review any errors and warnings above."
"""

def generate_complete_script(env, env_vars, resource_group, api_management, networking, app_service,
                           data_ai_services, web_app, bot_service,
                           teams_integration, network_verification):
    """Generate complete deployment script with reordered sections"""
    return f"""#!/bin/bash
# Azure ANPI Bot Deployment Script
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# For environment: {env}

{env_vars}

{resource_group}

# First, create API Management
{api_management}

# Now create networking with Application Gateway pointing to APIM
{networking}

{app_service}

{data_ai_services}

{web_app}

{bot_service}

{teams_integration}

{network_verification}

echo "Deployment completed successfully!"
"""

def generate_all_scripts(params):
    """Generate all script sections based on input parameters with APIM first, then Application Gateway"""
    # Extract environment value first to use consistently
    env = params['env']
    
    # Generate individual sections
    env_vars = generate_environment_vars(
        env,
        params['subscription_id'],
        params['location'],
        params['rg_name'],
        params['anpi_tag'].replace('Dev', env.capitalize()),  # Fix tags to use correct environment
        params['shared_tag'].replace('Dev', env.capitalize()), # Fix tags to use correct environment
        params['ms_app_id'],
        params['ms_app_password'],
        params['ms_app_tenant_id'],
        params['openai_model'],
        params['model_version'],
        params['embedding_model'],
        params['embedding_model_version']
    )
    
    resource_group = generate_resource_group()
    
    # Generate resource names with correct environment
    vnet_name = params['vnet_name'].replace('dev', env.lower())
    subnet_name = params['subnet_name'].replace('dev', env.lower())
    pip_name = params['pip_name'].replace('dev', env.lower())
    agw_name = params['agw_name'].replace('dev', env.lower())
    waf_name = params['waf_name'].replace('dev', env.lower())
    asp_name = params['asp_name'].replace('dev', env.lower())
    appinsights_name = params['appinsights_name'].replace('dev', env.lower())
    kv_name = params['kv_name'].replace('dev', env.lower())
    cosmos_name = params['cosmos_name'].replace('dev', env.lower())
    openai_name = params['openai_name'].replace('dev', env.lower())
    search_name = params['search_name'].replace('dev', env.lower())
    app_name = params['app_name'].replace('dev', env.lower())
    bot_name = params['bot_name'].replace('dev', env.lower())
    teams_app_name = params['teams_app_name'].replace('Dev', env.capitalize())
    
    # Create API Management first
    api_mgmt = generate_api_management(
        params['apim_name'],
        params['apim_sku'],
        params['apim_publisher_email'],
        params['apim_publisher_name'],
        params['api_id'],
        params['api_path'],
        params['api_display_name'],
        params['location'],
        app_name  # Use corrected app_name
    )

    # Then create networking with references to APIM
    networking = generate_networking(
        vnet_name,  # Use corrected name
        params['vnet_address_prefix'],
        subnet_name,  # Use corrected name
        params['subnet_prefix'],
        pip_name,  # Use corrected name
        agw_name,  # Use corrected name
        waf_name,  # Use corrected name
        params['apim_name'],
        app_name,  # Use corrected name
        env
    )
    
    # Continue with other resources
    app_service = generate_app_service(
        asp_name,  # Use corrected name
        params['asp_sku'],
        appinsights_name  # Use corrected name
    )
    
    data_ai = generate_data_ai_services(
        kv_name,  # Use corrected name
        cosmos_name,  # Use corrected name
        params['cosmos_db_name'],
        openai_name,  # Use corrected name
        params['openai_model'],
        params['model_version'],
        params['embedding_model'],
        params['embedding_model_version'],
        search_name,  # Use corrected name
        params['search_sku'],
        params['search_index_name'],
        params['semantic_config_name']
    )
    
    web_app = generate_web_app(
        app_name,  # Use corrected name
        asp_name,  # Use corrected name
        params['app_runtime'],
        kv_name,  # Use corrected name
        params['apim_name'],
        params['api_id'],
        params['allowed_origins'],
        params['jwt_issuer'],
        params['jwt_expiry_minutes'],
        params['cosmos_db_name'],
        params['search_index_name'],
        params['semantic_config_name'],
        params['api_base_url'],
        params['timeout_minutes'],
        params['jwt_secret_key']
    )
    
    bot_service = generate_bot_service(
        bot_name,  # Use corrected name
        app_name,  # Use corrected name
        params['apim_name'],
        params['api_id']
    )
    
    teams_integration = generate_teams_integration(
        teams_app_name,  # Use corrected name
        params['teams_redirect_uri'],
        kv_name  # Use corrected name
    )
    
    network_verification = generate_network_verification(
        app_name,  # Use corrected name
        kv_name,  # Use corrected name
        cosmos_name,  # Use corrected name
        params['cosmos_db_name'],
        params['apim_name'],
        agw_name,  # Use corrected name
        pip_name,  # Use corrected name
        search_name,  # Use corrected name
        params['api_path']
    )
    
    # Generate complete script - reordering sections with API Management first
    complete_script = generate_complete_script(
        env,
        env_vars,
        resource_group,
        api_mgmt,      # APIM first
        networking,    # Networking (Application Gateway) second 
        app_service,
        data_ai,
        web_app,
        bot_service,
        teams_integration,
        network_verification
    )
    
    # Return all scripts in a dictionary
    return {
        "environment_vars": env_vars,
        "resource_group": resource_group,
        "networking": networking,
        "app_service": app_service,
        "data_ai_services": data_ai,
        "api_management": api_mgmt,
        "web_app": web_app,
        "bot_service": bot_service,
        "teams_integration": teams_integration,
        "network_verification": network_verification,
        "complete_script": complete_script
    }