"""
Utility functions for the Azure ANPI Bot Infrastructure Generator.
"""
import base64
import json
import random
import string
from datetime import datetime
import io
import zipfile
from PIL import Image
import os

def get_markdown_download_link(md_content, filename):
    """
    Create a downloadable link for Markdown content
    
    Args:
        md_content (str): Markdown content to download
        filename (str): Name of the file to download
        
    Returns:
        str: HTML link for downloading the content
    """
    b64 = base64.b64encode(md_content.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}" class="download-button">📄 Download Markdown</a>'
    return href

def generate_jwt_secret():
    """
    Generate a secure JWT Secret Key
    
    Returns:
        str: A random string suitable for use as a JWT secret
    """
    # Create a mix of letters, numbers and special characters
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    # Generate a random string of 40 characters
    jwt_secret = ''.join(random.choice(characters) for _ in range(40))
    return jwt_secret

def create_markdown_content(scripts, env):
    """
    Create formatted markdown content from scripts for download
    
    Args:
        scripts (dict): Dictionary containing generated script sections
        env (str): Environment name (dev, test, etc.)
        
    Returns:
        str: Formatted markdown content
    """
    return f"""# Azure ANPI Bot Deployment Script

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for environment: {env}

## Environment Variables
```bash
{scripts["environment_vars"]}
```

## Resource Group
```bash
{scripts["resource_group"]}
```

## Networking
```bash
{scripts["networking"]}
```

## App Service
```bash
{scripts["app_service"]}
```

## Data & AI Services
```bash
{scripts["data_ai_services"]}
```

## API Management
```bash
{scripts["api_management"]}
```

## Web App
```bash
{scripts["web_app"]}
```

## Bot Service
```bash
{scripts["bot_service"]}
```

## Teams Integration
```bash
{scripts["teams_integration"]}
```

## Network Verification
```bash
{scripts["network_verification"]}
```
"""


def get_settings_download_link(settings, filename):
    """
    Create a downloadable link for settings as JSON
    
    Args:
        settings (dict): Settings dictionary to download
        filename (str): Name of the file to download
        
    Returns:
        str: HTML link for downloading the settings
    """
    settings_json = json.dumps(settings, indent=2)
    b64 = base64.b64encode(settings_json.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}">Download Settings</a>'
    return href

def parse_uploaded_settings(uploaded_file):
    """
    Parse an uploaded settings JSON file
    
    Args:
        uploaded_file: File object from st.file_uploader
        
    Returns:
        dict: Parsed settings dictionary or None if parsing failed
    """
    try:
        content = uploaded_file.read()
        settings = json.loads(content)
        return settings
    except Exception as e:
        return None
        
def get_full_settings_download_link(settings, filename):
    """
    Create a downloadable link for full application settings as JSON
    
    Args:
        settings (dict): Full settings dictionary to download
        filename (str): Name of the file to download
        
    Returns:
        str: HTML link for downloading the settings
    """
    settings_json = json.dumps(settings, indent=2)
    b64 = base64.b64encode(settings_json.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}" class="download-button">Download Complete Settings</a>'
    return href

def get_yaml_download_link(api_display_name, env, app_name, apim_name="apim-itz-fjp", api_path="anpi"):
    """
    Create a downloadable link for OpenAPI YAML file
    
    Args:
        api_display_name (str): Display name for the API
        env (str): Environment (dev, test, etc.)
        app_name (str): App Service name
        apim_name (str): API Management service name
        api_path (str): API path
        
    Returns:
        str: HTML link for downloading the YAML file
    """
    yaml_content = f"""openapi: 3.0.1
info:
  title: {api_display_name}
  description: API for FJP ANPI Safety Confirmation System Bot - {env.upper()}
  version: '1.0'
servers:
  - url: https://{apim_name}.azure-api.net/{api_path}
paths:
  /api/auth/token:
    post:
      tags:
        - Authentication
      summary: Login to get JWT token
      description: Login to get JWT token
      operationId: login
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
            example:
              apiClientId: string
              apiKey: string
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
              example:
                token: string
                expiresIn: 0
        '401':
          description: Unauthorized
        '500':
          description: Internal server error
  /api/auth/refresh-token:
    post:
      tags:
        - Authentication
      summary: Refresh JWT token
      description: Refresh JWT token
      operationId: refreshToken
      responses:
        '200':
          description: Token refreshed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
              example:
                token: string
                expiresIn: 0
        '401':
          description: Unauthorized
        '500':
          description: Internal server error
  /api/auth/validate:
    get:
      tags:
        - Authentication
      summary: Validate JWT token
      description: Validate JWT token
      operationId: validateToken
      responses:
        '200':
          description: Token is valid
          content:
            application/json:
              schema:
                type: object
                properties:
                  valid:
                    type: boolean
                  userId:
                    type: string
                  userName:
                    type: string
                  roles:
                    type: array
                    items:
                      type: string
              example:
                valid: true
                userId: string
                userName: string
                roles:
                  - string
        '401':
          description: Unauthorized
        '500':
          description: Internal server error
  /api/broadcast/anpi-confirms:
    post:
      tags:
        - Broadcast
      summary: Send emergency ANPI confirmation messages to users
      description: Send emergency ANPI confirmation messages to users
      operationId: sendAnpiConfirms
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SimpleBroadcastRequest'
            example:
              recipients:
                - username: string
                  nationality: string
                  token: string
              channel: string
              event:
                isResend: false
                eventId: 0
                dateTime: string
                severity: string
                location: string
                earthquakeMaxIntRate: string
                link: string
      responses:
        '200':
          description: Broadcast messages sent successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BroadcastResponse'
              example:
                message: string
                timestamp: string
                eventId: 0
                recipientCount: 0
        '400':
          description: Bad request
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
        '500':
          description: Internal server error
  /api/broadcast/leaderships-earthquakealert:
    post:
      tags:
        - Broadcast
      summary: Send earthquake alert to leadership members
      description: Send earthquake alert to leadership members
      operationId: sendEarthquakeAlert
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SimpleBroadcastRequest'
            example:
              recipients:
                - username: string
                  nationality: string
                  token: string
              channel: string
              event:
                isResend: false
                eventId: 0
                dateTime: string
                severity: string
                location: string
                earthquakeMaxIntRate: string
                link: string
      responses:
        '200':
          description: Earthquake alert sent successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BroadcastResponse'
              example:
                message: string
                timestamp: string
                eventId: 0
                recipientCount: 0
        '400':
          description: Bad request
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
        '500':
          description: Internal server error
  /api/broadcast/leaderships-statusreport:
    post:
      tags:
        - Broadcast
      summary: Send status report to leadership members
      description: Send status report to leadership members
      operationId: sendStatusReport
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/StatusReportBroadcastRequest'
            example:
              recipients:
                - username: string
                  nationality: string
                  token: string
              channel: string
              event:
                isResend: false
                eventId: 0
                dateTime: string
                severity: string
                location: string
                earthquakeMaxIntRate: string
                link: string
              statusReport:
                titleConfig: string
                totalInfluencers: 0
                totalUnconfirmed: 0
                totalPeopleWithProblems: 0
      responses:
        '200':
          description: Status report sent successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BroadcastResponse'
              example:
                message: string
                timestamp: string
                eventId: 0
                recipientCount: 0
        '400':
          description: Bad request
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
        '500':
          description: Internal server error
  /api/broadcast/notify:
    post:
      tags:
        - Broadcast
      summary: Send custom notification to users
      description: Send custom notification to users
      operationId: sendNotification
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NotificationRequest'
            example:
              recipients:
                - username: string
                  nationality: string
                  token: string
              channel: string
              messageMarkdown: string
              dialogName: string
      responses:
        '200':
          description: Notification sent successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BroadcastResponse'
              example:
                message: string
                timestamp: string
                eventId: 0
                recipientCount: 0
        '400':
          description: Bad request
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
        '500':
          description: Internal server error
  /api/alive:
    get:
      tags:
        - Health
      summary: Get current date and time
      description: Get current date and time
      operationId: getAlive
      responses:
        '200':
          description: Current date and time
          content:
            application/json:
              schema:
                type: string
                format: date-time
              example: string
        '500':
          description: Internal server error
  /api/alive/version:
    get:
      tags:
        - Health
      summary: Get application version
      description: Get application version
      operationId: getVersion
      responses:
        '200':
          description: Application version
          content:
            application/json:
              schema:
                type: string
              example: string
        '500':
          description: Internal server error
  /api/alive/status:
    get:
      tags:
        - Health
      summary: Get application status
      description: Get application status
      operationId: getStatus
      responses:
        '200':
          description: Application status
          content:
            application/json:
              schema:
                type: object
        '401':
          description: Unauthorized
        '500':
          description: Internal server error
  /api/messages:
    post:
      tags:
        - Bot
      summary: Bot Framework message endpoint
      description: Bot Framework message endpoint
      operationId: botMessages
      requestBody:
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: OK
        '500':
          description: Internal server error
components:
  schemas:
    LoginRequest:
      required:
        - userId
        - apiKey
      type: object
      properties:
        userId:
          type: string
        apiKey:
          type: string
    LoginResponse:
      type: object
      properties:
        token:
          type: string
        userId:
          type: string
        userName:
          type: string
        email:
          type: string
        roles:
          type: array
          items:
            type: string
        expiresIn:
          type: integer
          format: int32
    SimpleRecipient:
      required:
        - username
      type: object
      properties:
        username:
          type: string
          description: User's login name
        nationality:
          type: string
          description: User's nationality (determines language preference)
        token:
          type: string
          description: User's authentication token
    EventDetails:
      required:
        - eventId
        - dateTime
        - severity
        - location
      type: object
      properties:
        isResend:
          type: boolean
          description: Whether this is a resent notification
          default: false
        eventId:
          type: integer
          description: Unique identifier for the event
          format: int32
        dateTime:
          type: string
          description: Date and time of the event
          format: date-time
        severity:
          type: string
          description: Severity level of the event
        location:
          type: string
          description: Geographic location of the event
        earthquakeMaxIntRate:
          type: string
          description: Maximum earthquake intensity rating
        link:
          type: string
          description: URL with more information about the event
    StatusReportInfo:
      type: object
      properties:
        titleConfig:
          type: string
          description: Title for the status report
        totalInfluencers:
          type: integer
          description: Total number of impacted employees
          format: int32
        totalUnconfirmed:
          type: integer
          description: Number of employees who haven't confirmed status
          format: int32
        totalPeopleWithProblems:
          type: integer
          description: Number of employees reporting problems
          format: int32
    SimpleBroadcastRequest:
      required:
        - recipients
        - channel
        - event
      type: object
      properties:
        recipients:
          type: array
          items:
            $ref: '#/components/schemas/SimpleRecipient'
        channel:
          type: string
          description: 'Communication channel to use (e.g., msteams, webchat)'
        event:
          $ref: '#/components/schemas/EventDetails'
    StatusReportBroadcastRequest:
      required:
        - recipients
        - channel
        - event
        - statusReport
      type: object
      properties:
        recipients:
          type: array
          items:
            $ref: '#/components/schemas/SimpleRecipient'
        channel:
          type: string
          description: Communication channel to use
        event:
          $ref: '#/components/schemas/EventDetails'
        statusReport:
          $ref: '#/components/schemas/StatusReportInfo'
    NotificationRequest:
      required:
        - recipients
        - messageMarkdown
      type: object
      properties:
        recipients:
          type: array
          items:
            $ref: '#/components/schemas/SimpleRecipient'
        channel:
          type: string
          description: Communication channel to use
        messageMarkdown:
          type: string
          description: Message content in markdown format
        dialogName:
          type: string
          description: Dialog name for tracking purposes
    BroadcastResponse:
      type: object
      properties:
        message:
          type: string
          description: Success/failure message
        timestamp:
          type: string
          description: When the broadcast was sent
          format: date-time
        eventId:
          type: integer
          description: ID of the event that prompted the broadcast
          format: int32
        recipientCount:
          type: integer
          description: Number of recipients who received the message
          format: int32
  securitySchemes:
    apiKeyHeader:
      type: apiKey
      name: Ocp-Apim-Subscription-Key
      in: header
    apiKeyQuery:
      type: apiKey
      name: subscription-key
      in: query
security:
  - apiKeyHeader: [ ]
  - apiKeyQuery: [ ]
"""
    b64 = base64.b64encode(yaml_content.encode()).decode()
    href = f'<a href="data:file/yaml;base64,{b64}" download="anpi_bot_api_{env}.openapi.yaml">Download OpenAPI YAML</a>'
    return href
  
def get_arm_template_download_link(app_gw_name, vnet_name, subnet_name, pip_name, environment, location):
    """
    Create a downloadable ARM template for Application Gateway with WAF configuration
    
    Args:
        app_gw_name (str): Application Gateway name
        vnet_name (str): VNet name
        subnet_name (str): Subnet name
        pip_name (str): Public IP name
        environment (str): Environment name (e.g., Dev, Test, Prod)
        location (str): Azure region
        
    Returns:
        str: HTML link for downloading the template
    """
    # Create the ARM template
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "applicationGatewayName": {
                "type": "string",
                "defaultValue": app_gw_name,
                "metadata": {
                    "description": "Application Gateway name"
                }
            },
            "vnetName": {
                "type": "string",
                "defaultValue": vnet_name,
                "metadata": {
                    "description": "Virtual Network name"
                }
            },
            "subnetName": {
                "type": "string",
                "defaultValue": subnet_name,
                "metadata": {
                    "description": "Subnet name"
                }
            },
            "publicIpName": {
                "type": "string",
                "defaultValue": pip_name,
                "metadata": {
                    "description": "Public IP name"
                }
            },
            "environment": {
                "type": "string",
                "defaultValue": environment,
                "metadata": {
                    "description": "Environment name"
                }
            },
            "location": {
                "type": "string",
                "defaultValue": location,
                "metadata": {
                    "description": "Location for all resources"
                }
            }
        },
        "variables": {
            "appGwPublicIPRef": "[resourceId('Microsoft.Network/publicIPAddresses', parameters('publicIpName'))]",
            "appGwId": "[resourceId('Microsoft.Network/applicationGateways', parameters('applicationGatewayName'))]",
            "subnetRef": "[resourceId('Microsoft.Network/virtualNetworks/subnets', parameters('vnetName'), parameters('subnetName'))]"
        },
        "resources": [
            {
                "apiVersion": "2021-05-01",
                "type": "Microsoft.Network/applicationGateways",
                "name": "[parameters('applicationGatewayName')]",
                "location": "[parameters('location')]",
                "tags": {
                    "Project": "AnpiBot",
                    "Environment": "[parameters('environment')]"
                },
                "properties": {
                    "sku": {
                        "name": "WAF_v2",
                        "tier": "WAF_v2"
                    },
                    "autoscaleConfiguration": {
                        "minCapacity": 0,
                        "maxCapacity": 10
                    },
                    "gatewayIPConfigurations": [
                        {
                            "name": "appGatewayIpConfig",
                            "properties": {
                                "subnet": {
                                    "id": "[variables('subnetRef')]"
                                }
                            }
                        }
                    ],
                    "frontendIPConfigurations": [
                        {
                            "name": "appGatewayFrontendIP",
                            "properties": {
                                "publicIPAddress": {
                                    "id": "[variables('appGwPublicIPRef')]"
                                }
                            }
                        }
                    ],
                    "frontendPorts": [
                        {
                            "name": "appGatewayFrontendPort",
                            "properties": {
                                "port": 80
                            }
                        }
                    ],
                    "backendAddressPools": [
                        {
                            "name": "appGatewayBackendPool",
                            "properties": {
                                "backendAddresses": []
                            }
                        }
                    ],
                    "backendHttpSettingsCollection": [
                        {
                            "name": "appGatewayBackendHttpSettings",
                            "properties": {
                                "port": 80,
                                "protocol": "Http",
                                "cookieBasedAffinity": "Disabled",
                                "pickHostNameFromBackendAddress": False,
                                "requestTimeout": 30
                            }
                        }
                    ],
                    "httpListeners": [
                        {
                            "name": "appGatewayHttpListener",
                            "properties": {
                                "frontendIPConfiguration": {
                                    "id": "[concat(variables('appGwId'), '/frontendIPConfigurations/appGatewayFrontendIP')]"
                                },
                                "frontendPort": {
                                    "id": "[concat(variables('appGwId'), '/frontendPorts/appGatewayFrontendPort')]"
                                },
                                "protocol": "Http",
                                "requireServerNameIndication": False
                            }
                        }
                    ],
                    "requestRoutingRules": [
                        {
                            "name": "rule1",
                            "properties": {
                                "ruleType": "Basic",
                                "httpListener": {
                                    "id": "[concat(variables('appGwId'), '/httpListeners/appGatewayHttpListener')]"
                                },
                                "backendAddressPool": {
                                    "id": "[concat(variables('appGwId'), '/backendAddressPools/appGatewayBackendPool')]"
                                },
                                "backendHttpSettings": {
                                    "id": "[concat(variables('appGwId'), '/backendHttpSettingsCollection/appGatewayBackendHttpSettings')]"
                                },
                                "priority": 100
                            }
                        }
                    ],
                    "enableHttp2": True,
                    "webApplicationFirewallConfiguration": {
                        "enabled": True,
                        "firewallMode": "Prevention",
                        "ruleSetType": "OWASP",
                        "ruleSetVersion": "3.2"
                    }
                }
            }
        ],
        "outputs": {
            "applicationGatewayId": {
                "type": "string",
                "value": "[variables('appGwId')]"
            }
        }
    }
    
    # Convert template to JSON string with proper indentation
    template_json = json.dumps(template, indent=2)
    
    # Convert to base64 for download link
    template_b64 = base64.b64encode(template_json.encode('utf-8')).decode('utf-8')
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"appgateway_{environment.lower()}_{timestamp}.json"
    
    # Create HTML download link
    href = f'<a href="data:application/json;base64,{template_b64}" download="{filename}" class="download-button">📥 Download ARM Template</a>'
    
    # Add deployment instructions
    deployment_instructions = f"""
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; border: 1px solid #ddd;">
        <h4>Deployment Instructions</h4>
        <p><strong>Deploy the WAF-enabled Application Gateway:</strong></p>
        <pre style="background-color: #f1f1f1; padding: 10px; border-radius: 4px; overflow-x: auto;">
az deployment group create \\
  --resource-group $RG_NAME \\
  --template-file {filename}
        </pre>
        
        <p><strong>Note:</strong> This template includes:</p>
        <ul>
          <li>WAF_v2 SKU with prevention mode enabled</li>
          <li>OWASP 3.2 rule set</li>
          <li>HTTP/2 support enabled</li>
          <li>Autoscaling configuration (0-10 capacity)</li>
        </ul>
        
        <p><strong>After deployment:</strong> Configure the backend pool to point to your API Management service:</p>
        <pre style="background-color: #f1f1f1; padding: 10px; border-radius: 4px; overflow-x: auto;">
# Get the API Management hostname
APIM_NAME="apim-itz-fjp"
APIM_HOST=$(az apim show --name $APIM_NAME --resource-group $RG_NAME --query hostname -o tsv)

# Update the backend pool to point to APIM backend
az network application-gateway address-pool update \\
  --name appGatewayBackendPool \\
  --gateway-name {app_gw_name} \\
  --resource-group $RG_NAME \\
  --servers "$APIM_HOST"
        </pre>
    </div>
    """
    
    return href + deployment_instructions

def get_search_index_json(index_name, semantic_config_name):
    """
    Generate JSON for search index configuration
    
    Args:
        index_name (str): Name of the search index
        semantic_config_name (str): Name of the semantic configuration
        
    Returns:
        str: JSON string with index configuration
    """
    index_json = {
      "name": index_name,
      "fields": [
        {
          "name": "id",
          "type": "Edm.String",
          "searchable": True,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": True,
          "facetable": False,
          "key": True,
          "synonymMaps": []
        },
        {
          "name": "partitionKey",
          "type": "Edm.String",
          "searchable": False,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": False,
          "facetable": False,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "type",
          "type": "Edm.String",
          "searchable": False,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": False,
          "facetable": True,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "title",
          "type": "Edm.String",
          "searchable": True,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": True,
          "facetable": False,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "content",
          "type": "Edm.String",
          "searchable": True,
          "filterable": False,
          "retrievable": True,
          "stored": True,
          "sortable": False,
          "facetable": False,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "category",
          "type": "Edm.String",
          "searchable": True,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": True,
          "facetable": True,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "language",
          "type": "Edm.String",
          "searchable": False,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": True,
          "facetable": True,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "tags",
          "type": "Collection(Edm.String)",
          "searchable": True,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": False,
          "facetable": True,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "createdDate",
          "type": "Edm.String",
          "searchable": False,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": True,
          "facetable": False,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "lastUpdatedDate",
          "type": "Edm.String",
          "searchable": False,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": True,
          "facetable": False,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "hasEmbedding",
          "type": "Edm.Boolean",
          "searchable": False,
          "filterable": True,
          "retrievable": True,
          "stored": True,
          "sortable": False,
          "facetable": True,
          "key": False,
          "synonymMaps": []
        },
        {
          "name": "embedding",
          "type": "Collection(Edm.Single)",
          "searchable": True,
          "filterable": False,
          "retrievable": True,
          "stored": True,
          "sortable": False,
          "facetable": False,
          "key": False,
          "dimensions": 1536,
          "vectorSearchProfile": "my-vector-profile",
          "synonymMaps": []
        }
      ],
      "scoringProfiles": [],
      "suggesters": [],
      "analyzers": [],
      "normalizers": [],
      "tokenizers": [],
      "tokenFilters": [],
      "charFilters": [],
      "similarity": {
        "@odata.type": "#Microsoft.Azure.Search.BM25Similarity"
      },
      "semantic": {
        "configurations": [
          {
            "name": semantic_config_name,
            "flightingOptIn": False,
            "prioritizedFields": {
              "titleField": {
                "fieldName": "title"
              },
              "prioritizedContentFields": [
                {
                  "fieldName": "content"
                }
              ],
              "prioritizedKeywordsFields": [
                {
                  "fieldName": "category"
                },
                {
                  "fieldName": "tags"
                }
              ]
            }
          }
        ]
      },
      "vectorSearch": {
        "algorithms": [
          {
            "name": "my-algorithm-config",
            "kind": "hnsw",
            "hnswParameters": {
              "metric": "cosine",
              "m": 4,
              "efConstruction": 400,
              "efSearch": 500
            }
          }
        ],
        "profiles": [
          {
            "name": "my-vector-profile",
            "algorithm": "my-algorithm-config"
          }
        ],
        "vectorizers": [],
        "compressions": []
      }
    }
    
    return json.dumps(index_json, indent=2)

def get_search_indexer_json(index_name):
    """
    Generate JSON for search indexer configuration
    
    Args:
        index_name (str): Name of the search index
        
    Returns:
        str: JSON string with indexer configuration
    """
    indexer_json = {
      "name": f"{index_name}-indexer",
      "description": "",
      "dataSourceName": f"cosmos-{index_name}",
      "skillsetName": None,
      "targetIndexName": index_name,
      "disabled": None,
      "schedule": None,
      "parameters": None,
      "fieldMappings": [],
      "outputFieldMappings": [],
      "cache": None,
      "encryptionKey": None
    }
    
    return json.dumps(indexer_json, indent=2)

def get_json_download_link(json_content, filename):
    """
    Create a downloadable link for JSON content
    
    Args:
        json_content (str): JSON content to download
        filename (str): Name of the file to download
        
    Returns:
        str: HTML link for downloading the content
    """
    b64 = base64.b64encode(json_content.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}" class="download-button">📄 Download {filename}</a>'
    return href

def get_search_datasource_json(cosmos_name, cosmos_db_name, index_name):
    """
    Generate JSON for search data source configuration
    
    Args:
        cosmos_name (str): Name of the Cosmos DB account
        cosmos_db_name (str): Name of the Cosmos DB database
        index_name (str): Name of the search index
        
    Returns:
        str: JSON string with data source configuration
    """
    datasource_json = {
      "name": f"cosmos-{index_name}",
      "description": None,
      "type": "cosmosdb",
      "subtype": None,
      "credentials": {
        "connectionString": f"AccountEndpoint=https://{cosmos_name}.documents.azure.com;AccountKey=...;Database={cosmos_db_name}"
      },
      "container": {
        "name": "knowledge",
        "query": None
      },
      "dataChangeDetectionPolicy": None,
      "dataDeletionDetectionPolicy": None,
      "encryptionKey": None,
      "identity": None
    }
    
    return json.dumps(datasource_json, indent=2)

def get_initial_knowledge_json():
    """
    Generate JSON for initial knowledge entries
    
    Returns:
        str: JSON string with initial knowledge entries
    """
    import uuid
    from datetime import datetime, timezone
    
    # Current time in ISO format with Z
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Create sample knowledge entries
    knowledge_entries = [
    {
      "title": "ANPI System Overview",
      "content": "The ANPI (Safety Confirmation) System is used by FJP to quickly confirm the safety status of employees during emergencies.\n",
      "category": "SystemOverview",
      "language": "en",
      "tags": [
        "ANPI",
        "Safety",
        "Disaster"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "How to Respond to ANPI Messages",
      "content": "When you receive an ANPI safety confirmation message, please respond as soon as possible.\n",
      "category": "Usage",
      "language": "en",
      "tags": [
        "ANPI",
        "Instructions"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "ANPI System Overview",
      "content": "The ANPI (Safety Confirmation) System is used by FJP to quickly confirm the safety status of employees during emergencies.\n",
      "category": "SystemOverview",
      "language": "en",
      "tags": [
        "ANPI",
        "Safety",
        "Disaster"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "How to Respond to ANPI Messages",
      "content": "When you receive an ANPI safety confirmation message, please respond as soon as possible.\n",
      "category": "Usage",
      "language": "en",
      "tags": [
        "ANPI",
        "Instructions"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Staying Calm and Responding to Disasters",
      "content": "When disasters strike, the first thing you need to do is stay *CALM*. Absolutely *CALM*! If you're not calm, you won't be able to make sound judgments when problems arise.\nHow to handle the situation will vary depending on the circumstances.\nTo report that your area is experiencing a disaster, call 📱 *171*. This is the disaster messaging hotline. You can call to confirm your own safety as well as that of your friends and family. 💥 Remember: The number for disaster messaging is *171*\nThis is a method to communicate with family and friends during a major disaster when you can't connect via 📱 phone. You can use a landline, mobile phone, or public phone to 🎤 record a 💬 message within ⌚️ 30 seconds.\n💥 When you feel \"it's dangerous to stay at home\", 🏃 evacuate to a shelter\nDangerous situations include:\n🔶 When your house seems about to collapse due to an earthquake\n🔶 When there is a 🔥 fire near your home\n🏃‍♀️ *Evacuate!*\n🔶 Turn on the TV or radio\n🔶 Take 🔦💵 emergency supplies with you\n🔶 Turn off the gas and the main power breaker\n🔶 At the shelter, live in a spirit of mutual aid\n💥 For more information, refer to: 📖 Disaster Prevention Guide for 👨‍👩‍👧‍👦 Parents and Children:\n➡️https://www.hyogo-ip.or.jp/torikumi/tabunkakyose/documents/osu-e-8baj7-24.pdf\n",
      "category": "Disaster Response",
      "language": "vi",
      "tags": [
        "Disaster Preparedness",
        "Emergency Communication",
        "Earthquake",
        "Fire",
        "Evacuation"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "What to Do During an Earthquake",
      "content": "🔶 *Stay calm* and *sit still* to assess the situation.\n🔶 If it's a small earthquake: It will pass in 5-10s. You don't need to do anything.\n🔶 *If it's a strong earthquake* that lasts a long time:\n- Open the door of the room or a window\n- Stay away from places with objects that can easily fall: bookcases, dish cabinets, shelves...\n- Find safe, secure places to shelter, avoiding falling objects: under a table, under a chair, a one-piece toilet...\n- After the tremors pass, turn off the gas and electricity to prevent fire and explosions, take valuables like 💰💴 wallets, 📱 phones, emergency bags... (don't take too many other things to avoid bulkiness and wasting time) then move to an open space or evacuation site in your area. You can search for evacuation sites by searching \"避難所+ Name of your living area\"! \n- After the tremors have passed and stabilized, you can return home.\n- If your house is definitely secure, you can stay at home without having to evacuate. However, if a large earthquake has passed, remember to go outside and wait for the situation to stabilize before going back inside!\n- Throughout the process of waiting for the tremors to pass, always update information and follow government instructions!\n📝 NOTE: *Do not use elevators* during an earthquake.\n",
      "category": "Earthquake Response",
      "language": "vi",
      "tags": [
        "Earthquake Safety",
        "Disaster Preparedness",
        "Evacuation",
        "Emergency Supplies"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Tsunami Awareness and Response",
      "content": "💥 Tsunamis often occur due to the phenomenon of continental shelf fracturing after earthquakes or 🌋 volcanic eruptions off the continental shelf.\n🔶 Signs of a 🌊 tsunami:\n     - Seawater suddenly recedes offshore, 10-100m away from the shore depending on the energy and cycle of the waves.\n     - The second sign is the phenomenon of strong fluctuations on the sea surface.\n🔶 How to respond:\n    - Tsunamis are usually predicted due to preceding earthquakes or volcanic eruptions. Therefore, when you receive a notification, go to a shelter or somewhere secure, the higher the better. The response is similar to that for earthquakes.\n    - There are also cases where tsunami information is predicted incorrectly, or the tsunami arrives too suddenly without warning. In this case, try to save yourself. Bring your 👪 loved ones and family to high mounds of earth or 🏙 tall buildings to take shelter. Remember, property is external, *life* is the most important thing.\n",
      "category": "Tsunami Response",
      "language": "vi",
      "tags": [
        "Tsunami",
        "Disaster Preparedness",
        "Evacuation",
        "Earthquake",
        "Volcano"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Typhoon Preparedness and Response in Japan",
      "content": "💥 ⛈ Typhoons in Japan usually occur from June to October each year, accompanied by strong gusts, flash floods, or landslides. Follow government information and guidance to ensure the safety of yourself, your family, and your loved ones.\n💥 What to do when a typhoon comes:\n 🔹 Unlike earthquakes, typhoons are updated early, so we have time to prepare to deal with them.\n 🔹 If your house is not sturdy or is near a river or mountain: go to a shelter after reinforcing your house and bringing necessary personal belongings and essentials. Then follow government instructions and guidance. Before leaving the house, hang the cloth provided by the city hall or leave a sign to show that you have moved to a safe place.\n 🔹 If your house is sturdy and high enough: stay 🏠 inside after carefully reinforcing the 🏤 house. Make sure you always update news regularly.\n \n 🔹 In the worst case, if you are in an unsafe place and don't have time to evacuate, call *110*. At these times, the switchboard is usually jammed, so call wherever you can get help, such as the 🏨 city hall, police station, police department... where you live. However, usually when a large ⛈ typhoon comes, the entire area affected by the 🌧 typhoon will be provided with free wifi and an emergency contact number, this information will change depending on the time. Therefore, before the typhoon comes, update the news and prepare carefully!\n \n🔹 If you have notified but the rescue team still doesn't arrive in time, try to save yourself as much as possible. Respond according to the situation, create prominent signs so that the rescue team can see you as clearly as possible. If you decide to leave before the rescue team arrives, contact and notify the situation, or hang a cloth or make a sign to show that you have left. And remember, be careful! Life is above all else!\n💥 Things to do before a typhoon comes:\n 🔹 Stock up on 🥙🧀 food, 🍶 water, medicine, and necessary items and essentials\n 🔹 If you have a car, make sure your car is always full of gas before the typhoon hits.\n 🔹 Reinforce the house: roof, pillars, objects outside the house such as bicycles, plant pots\n 🔹 Use tape to tape the windows and always close the curtains to avoid danger when hit. How to tape windows: https://electrictoolboy.com/media/38252/\n 🔹 Follow typhoon information regularly\n",
      "category": "Typhoon Response",
      "language": "vi",
      "tags": [
        "Typhoon",
        "Disaster Preparedness",
        "Evacuation",
        "Emergency Supplies",
        "Home Reinforcement"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Flooding and Landslides",
      "content": "💥 Floods and landslides are signs that come without warning when ⛈ typhoons arrive. However, you can follow weather forecast news to have the most effective preventive measures. Please refer to how to act when a typhoon comes.\n💥 Signs of a landslide are that the water flowing nearby changes from white to cloudy, with soil and sand mixed in the ground.\n💥 Signs of flash floods: the flow suddenly changes color, there are signs of undercurrents in the riverbed, there are loud sounds at the source...\n",
      "category": "Disaster Response",
      "language": "vi",
      "tags": [
        "Flood",
        "Landslide",
        "Typhoon",
        "Disaster Preparedness"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Thunder, Lightning, and Tornadoes in Japan",
      "content": "In 🇯🇵 Japan there is ⚡️ thunder and lightning and it is common during the 🌧 rainy season. However, the 🌪 tornado phenomenon is very rare.\n",
      "category": "Weather Phenomena",
      "language": "vi",
      "tags": [
        "Thunder",
        "Lightning",
        "Tornado",
        "Japan Weather"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Fire Response",
      "content": "🔹 When a fire occurs, if it is a small fire, try to extinguish it before the fire spreads. If there is a fire extinguisher, use the fire extinguisher.\n - Pan oil fire: turn off the fire, cover it, sprinkle salt or powder on it to extinguish. Note that because oil is lighter than water, *do not use water to extinguish oil*.\n - Other types of fires that are not oil: use water to extinguish. Note: do not use dry blankets or quilts to extinguish the fire, as it will make the fire flare up.\n \n🔹 When a fire is a large fire: If there is a fire extinguisher, use the fire extinguisher to extinguish the fire. If it cannot be extinguished, try to get out as quickly as possible. Because smoke is lighter than air, smoke will float up, so make sure you keep your body low when moving to avoid suffocation. After escaping the fire, call the rescue force. Clearly state the situation and address of the fire.\n🔹 If you want to call *119* but don't know Japanese: Notify the nearest Japanese person you know. Fire in Japanese is KAJI.\n",
      "category": "Fire Response",
      "language": "vi",
      "tags": [
        "Fire",
        "Fire Extinguisher",
        "Evacuation",
        "Emergency Call"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Fire Prevention",
      "content": "🔹 How to prevent and fight fires:\n  - Always pay attention when cooking and remember to turn off the gas when finished\n  - You can buy a gas stove with automatic shut-off capability\n  - Always keep a fire extinguisher in the house\n  - Prepare knowledge about fire prevention and fighting\n  - Practice fire prevention and fighting drills...\n \n🔹 If there is a fire alarm, do not rush to push each other, but follow the instructions of those in charge. Move in an orderly manner to the evacuation site. When a fire occurs, do not use the elevator, as the electrical system may have been affected by the fire.\n💥 You can refer to the details and necessary notes at this link:\n ➡️ https://www.n-bouka.or.jp/materials/pdf/13_ifresidential.pdf\n ➡️ https://www.nhk.or.jp/nhkworld-blog/vi/?cid=wohk-fb-org_site_multilingual_vt_msvi-202101-001\n",
      "category": "Fire Prevention",
      "language": "vi",
      "tags": [
        "Fire Safety",
        "Fire Alarm",
        "Evacuation",
        "Disaster Preparedness"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Understanding the My ANPI Safety Confirmation System",
      "content": "My ANPI is a critical safety verification tool developed by FPT Japan to quickly confirm employee safety during large-scale disasters. Key features include:\n\n1. Purpose:\n- Rapidly verify the safety of employees in disaster-affected areas\n- Minimize business disruption risks\n- Enable timely emergency response\n\n2. User Roles:\nDepartment Leaders:\n- Check employee safety status\n- Make critical business continuity decisions\n- Contact staff to confirm safety\n\nTimesheet Approvers:\n- Employee safety check\n- Provide necessary support\n- Update safety status in the app\n\nEmployees:\n- Report personal and family safety\n- Request support if needed\n- Maintain updated contact information\n\n3. Notification Channels:\n- MyKintai mobile app\n- Email\n- Work chat platforms\n\n4. Importance:\n- Ensures rapid communication during emergencies\n- Supports business continuity planning\n- Provides a structured approach to employee safety\n",
      "category": "SafetySystem",
      "language": "en",
      "tags": [
        "ANPI",
        "Safety",
        "DisasterResponse",
        None
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "My ANPIシステムの理解：安全確認システムの詳細",
      "content": "My ANPIは、FPTジャパンが開発した大規模災害時に従業員の安全を迅速に確認するための重要な安全検証ツールです。主な特徴は以下の通りです：\n\n1. 目的：\n- 災害地域の従業員の安全を迅速に確認\n- 事業中断のリスクを最小限に抑える\n- 迅速な緊急対応を可能にする\n\n2. ユーザーの役割：\n部門リーダー：\n- 従業員の安全状況を確認\n- 重要な事業継続の意思決定\n- スタッフに安全確認の連絡\n\nタイムシート承認者：\n- 従業員の安全確認\n- 必要な支援の提供\n- アプリでの安全状況の更新\n\n従業員：\n- 個人と家族の安全を報告\n- 必要に応じて支援を要請\n- 連絡先情報の最新状態維持\n\n3. 通知チャンネル：\n- MyKintaiモバイルアプリ\n- メール\n- 職場チャットプラットフォーム\n\n4. 重要性：\n- 緊急時の迅速な連絡を確保\n- 事業継続計画をサポート\n- 従業員の安全に構造的アプローチを提供\n",
      "category": "安全システム",
      "language": "ja",
      "tags": [
        "ANPI",
        "安全",
        "災害対応",
        "事業継続"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Hệ Thống My ANPI - Hệ Thống Xác Nhận An Toàn Chi Tiết",
      "content": "My ANPI là một công cụ xác minh an toàn quan trọng do FPT Japan phát triển để nhanh chóng xác nhận an toàn cho nhân viên trong các thảm họa quy mô lớn. Các tính năng chính bao gồm:\n\n1. Mục Đích:\n- Nhanh chóng xác minh an toàn của nhân viên tại các khu vực bị ảnh hưởng bởi thảm họa\n- Giảm thiểu rủi ro gián đoạn kinh doanh\n- Cho phép ứng phó khẩn cấp kịp thời\n\n2. Vai Trò Người Dùng:\nLãnh Đạo Phòng Ban:\n- Kiểm tra tình trạng an toàn của nhân viên\n- Đưa ra quyết định về sự liên tục kinh doanh\n- Liên hệ với nhân viên để xác nhận an toàn\n\nNgười Phê Duyệt Bảng Chấm Công:\n- Kiểm tra an toàn của nhân viên\n- Cung cấp hỗ trợ cần thiết\n- Cập nhật trạng thái an toàn trong ứng dụng\n\nNhân Viên:\n- Báo cáo an toàn cá nhân và gia đình\n- Yêu cầu hỗ trợ nếu cần\n- Duy trì thông tin liên hệ được cập nhật\n\n3. Kênh Thông Báo:\n- Ứng dụng di động MyKintai\n- Email\n- Nền tảng chat công việc\n\n4. Tầm Quan Trọng:\n- Đảm bảo giao tiếp nhanh chóng trong tình trạng khẩn cấp\n- Hỗ trợ kế hoạch liên tục kinh doanh\n- Cung cấp phương pháp có cấu trúc cho an toàn nhân viên\n",
      "category": "Hệ Thống An Toàn",
      "language": "vi",
      "tags": [
        "ANPI",
        "An Toàn",
        "Ứng Phó Thảm Họa",
        "Liên Tục Kinh Doanh"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Disaster Prevention Experience Tour 2025",
      "content": "FJP is organizing a comprehensive Disaster Prevention Experience Tour to enhance employee safety skills and emergency preparedness.\n\nEvent Details:\n- Date: March 15th, 2025\n- Time: 2:20 PM - 4:00 PM\n- Location: Honjo Disaster Prevention Hall, Sumida Ward, Tokyo\n\nExperience Zones:\n1. Earthquake Simulation\n- Simulate earthquakes in various settings (outdoors, convenience stores)\n- Suitable for ages 3 and up\n- Experience different seismic intensity levels\n\n2. Smoke Safety Experience\n- Learn about smoke properties and dangers\n- Practice safe evacuation techniques\n- Understand navigation through smoke-filled environments\n\n3. Fire Extinguishing Training\n- Real-life fire simulation\n- Learn proper fire extinguisher usage\n- Recommended for grade 3 and above\n\n4. First Aid Workshop\n- CPR demonstration\n- AED usage training\n- Recommended for grade 4 and above\n\nRegistration:\n- Deadline: March 13th, 2025\n- Registration Link: https://forms.office.com/Pages/ResponsePage.aspx...\n- Contact: GiaoNTN for inquiries\n\nPurpose:\n- Strengthen disaster response capabilities\n- Enhance emergency preparedness\n- Provide practical safety skills\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "Disaster",
        "LifeSafety"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP防災体験ツアー2025 - 命を守る知識とスキルの習得",
      "content": "FJPは、従業員の安全スキルと緊急時対応能力を高めるための包括的な防災体験ツアーを開催します。\n\nイベント詳細：\n- 日付：2025年3月15日\n- 時間：午後2時20分 - 午後4時00分\n- 場所：本所防災館（東京都墨田区）\n\n体験エリア：\n1. 地震シミュレーション\n- 屋外や店内など、様々な状況での地震体験\n- 3歳以上対象\n- 異なる震度レベルの体験\n\n2. 煙体験\n- 煙の特性と危険性を学ぶ\n- 安全な避難技術の実践\n- 煙の中での適切な行動方法の理解\n\n3. 消火訓練\n- 実際の火災状況シミュレーション\n- 消火器の正しい使用方法\n- 3年生以上推奨\n\n4. 応急処置ワークショップ\n- 心肺蘇生法（CPR）のデモンストレーション\n- AEDの使用方法トレーニング\n- 4年生以上推奨\n\n参加登録：\n- 締切：2025年3月13日\n- 登録リンク：https://forms.office.com/Pages/ResponsePage.aspx...\n- 問い合わせ：GiaoNTN\n\n目的：\n- 災害対応能力の強化\n- 緊急時への備えの向上\n- 実践的な安全スキルの提供\n",
      "category": "防災",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害",
        "生命安全"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Chuyến Tham Quan Trải Nghiệm Phòng Chống Thảm Họa của FJP 2025",
      "content": "FJP tổ chức chuyến tham quan trải nghiệm phòng chống thảm họa toàn diện nhằm nâng cao kỹ năng an toàn và khả năng ứng phó khẩn cấp cho nhân viên.\n\nChi Tiết Sự Kiện:\n- Ngày: 15 tháng 3 năm 2025\n- Thời gian: 14:20 - 16:00\n- Địa điểm: Trung Tâm Phòng Chống Thảm Họa Honjo, Quận Sumida, Tokyo\n\nCác Khu Trải Nghiệm:\n1. Mô Phỏng Động Đất\n- Trải nghiệm động đất trong nhiều môi trường khác nhau (ngoài trời, cửa hàng tiện lợi)\n- Phù hợp với độ tuổi 3 trở lên\n- Trải nghiệm các mức độ địa chấn khác nhau\n\n2. Trải Nghiệm An Toàn Khói\n- Học về đặc tính và nguy hiểm của khói\n- Thực hành kỹ thuật sơ tán an toàn\n- Hiểu cách di chuyển trong môi trường đầy khói\n\n3. Huấn Luyện Chữa Cháy\n- Mô phỏng tình huống cháy thực tế\n- Học cách sử dụng bình chữa cháy\n- Khuyến nghị cho học sinh từ lớp 3 trở lên\n\n4. Hội Thảo Sơ Cứu\n- Hướng dẫn hồi sinh tim phổi (CPR)\n- Tập sử dụng thiết bị AED\n- Khuyến nghị cho học sinh từ lớp 4 trở lên\n\nĐăng Ký:\n- Hạn chót: 13 tháng 3 năm 2025\n- Liên kết đăng ký: https://forms.office.com/Pages/ResponsePage.aspx...\n- Liên hệ: GiaoNTN để biết thêm chi tiết\n\nMục Đích:\n- Tăng cường khả năng ứng phó thảm họa\n- Nâng cao sự chuẩn bị cho tình huống khẩn cấp\n- Cung cấp các kỹ năng an toàn thực tế\n",
      "category": "Phòng Chống Thảm Họa",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Đào Tạo Khẩn Cấp",
        "Thảm Họa",
        "An Toàn Sinh Mạng"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Tochigi Branch Earthquake and Tsunami Preparedness Drill",
      "content": "On October 4th, FJP conducted a comprehensive disaster preparedness drill at its Tochigi branch, focusing on emergency response and employee safety.\n\nDrill Highlights:\n1. Drill Scenario\n- Simulated Earthquake: Magnitude 5+ \n- Locations: Company offices and customer sites\n- Participants: Employees across different departments\n\n2. Key Objectives\n- Strengthen emergency response skills\n- Test Mykintai/Anpi safety confirmation system\n- Improve disaster readiness\n- Enhance inter-departmental coordination\n\n3. System Improvements\n- Enhanced Employee Portal Anpi functionality\n- Direct status updates by administrators\n- Reduced dependency on HR department\n- More streamlined emergency communication\n\n4. Participant Feedback\n- High enthusiasm and engagement\n- Quick safety status updates\n- Improved understanding of disaster response\n- Valuable insights for system enhancement\n\n5. Future Recommendations\n- Regular drill schedules\n- Include complex scenarios (power outages, injuries)\n- Continuous system refinement\n- Active involvement of department leaders\n\nSignificance:\n- Proactive approach to employee safety\n- Continuous improvement of emergency protocols\n- Building organizational resilience\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "DisasterResponse",
        "SystemImprovement"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP栃木支店における地震・津波対策訓練",
      "content": "10月4日、FJPは栃木支店で包括的な災害対策訓練を実施し、緊急対応と従業員の安全に焦点を当てました。\n\n訓練のハイライト：\n1. 訓練シナリオ\n- 想定地震：マグニチュード5+\n- 場所：会社のオフィスと顧客サイト\n- 参加者：各部門の従業員\n\n2. 主な目的\n- 緊急対応スキルの強化\n- Mykintai/Anpiの安全確認システムの検証\n- 災害への備えの向上\n- 部門間連携の改善\n\n3. システム改善点\n- Employee PortalのAnpi機能強化\n- 管理者による直接的な状況更新\n- 人事部門への依存度低減\n- より効率的な緊急時コミュニケーション\n\n4. 参加者からのフィードバック\n- 高い熱意と参加意欲\n- 迅速な安全状況の更新\n- 災害対応に対する理解の深化\n- システム改善に向けた貴重な洞察\n\n5. 今後の推奨事項\n- 定期的な訓練スケジュール\n- 複雑なシナリオの導入（停電、負傷者対応）\n- システムの継続的な改善\n- 部門リーダーの積極的な関与\n\n意義：\n- 従業員の安全に対する先見的なアプローチ\n- 緊急プロトコルの継続的な改善\n- 組織的な回復力の構築\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害対応",
        "システム改善"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Diễn Tập Phòng Chống Động Đất và Sóng Thần Chi Nhánh Tochigi của FJP",
      "content": "Vào ngày 4 tháng 10, FJP đã tiến hành một buổi diễn tập toàn diện về ứng phó thiên tai tại chi nhánh Tochigi, tập trung vào phản ứng khẩn cấp và an toàn cho nhân viên.\n\nĐiểm Nổi Bật của Buổi Diễn Tập:\n1. Kịch Bản Diễn Tập\n- Động Đất Giả Định: Độ lớn 5+\n- Địa Điểm: Văn phòng công ty và các địa điểm khách hàng\n- Người Tham Gia: Nhân viên từ các phòng ban khác nhau\n\n2. Mục Tiêu Chính\n- Tăng cường kỹ năng ứng phó khẩn cấp\n- Kiểm tra hệ thống xác nhận an toàn Mykintai/Anpi\n- Cải thiện sự sẵn sàng ứng phó thiên tai\n- Nâng cao sự phối hợp giữa các phòng ban\n\n3. Cải Tiến Hệ Thống\n- Nâng cấp chức năng Anpi trên Cổng Nhân Viên\n- Cập nhật trạng thái trực tiếp bởi quản trị viên\n- Giảm sự phụ thuộc vào phòng nhân sự\n- Giao tiếp khẩn cấp hiệu quả hơn\n\n4. Phản Hồi Từ Người Tham Gia\n- Sự nhiệt tình và tham gia cao\n- Cập nhật trạng thái an toàn nhanh chóng\n- Hiểu biết sâu hơn về ứng phó thiên tai\n- Những góc nhìn có giá trị cho việc cải thiện hệ thống\n\n5. Khuyến Nghị Trong Tương Lai\n- Lịch diễn tập thường xuyên\n- Bao gồm các kịch bản phức tạp (mất điện, người bị thương)\n- Cải tiến liên tục hệ thống\n- Sự tham gia tích cực của các trưởng phòng\n\nÝ Nghĩa:\n- Cách tiếp cận chủ động đối với an toàn nhân viên\n- Cải thiện liên tục các giao thức khẩn cấp\n- Xây dựng sức chống chịu của tổ chức\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Đào Tạo Khẩn Cấp",
        "Ứng Phó Thiên Tai",
        "Cải Tiến Hệ Thống"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Tochigi Branch Comprehensive Disaster Prevention Drill",
      "content": "Comprehensive Disaster Prevention Drill Announcement\n\nEvent Details:\n- Date: October 4th\n- Participants: \n  * Tochigi Branch Employees\n  * Employees from Customer Sites\n  * Expected Participation: 100% of Tochigi Branch Staff\n\nDrill Objectives:\n1. Emergency Response Training\n- Simulate Earthquake Scenario (Magnitude 5+)\n- Develop Incident Response Skills\n- Test Emergency Protocols\n\n2. Technology Integration\n- Validate Mykintai/Anpi App Functionality\n- Check System Readiness\n- Ensure Effective Communication Channels\n\n3. Organizational Preparedness\n- Enhance Employee Safety Awareness\n- Improve Incident Management Capabilities\n- Support Business Continuity Planning\n\nPre-Drill Preparation:\n- Preliminary Training Session Scheduled\n- Comprehensive Briefing for Participants\n- Technical System Readiness Check\n\nSignificance:\n- Proactive Approach to Disaster Preparedness\n- Company-Wide Safety Culture Development\n- Critical for Effective Emergency Management\n\nContext:\n- Part of Regular Disaster Prevention Activities\n- Coordinated with Functional Agencies\n- Conducted at Company Offices and Dormitories\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "DisasterResponse",
        "BusinessContinuity"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP栃木支店 包括的防災訓練のお知らせ",
      "content": "包括的な防災訓練のお知らせ\n\nイベント詳細：\n- 日付：10月4日\n- 参加者：\n  * 栃木支店の従業員\n  * 顧客サイトで働く従業員\n  * 予想参加率：栃木支店スタッフ100%\n\n訓練目的：\n1. 緊急対応訓練\n- 地震シナリオのシミュレーション（マグニチュード5+）\n- 事故対応スキルの開発\n- 緊急プロトコルの検証\n\n2. テクノロジー統合\n- Mykintai/Anpiアプリの機能検証\n- システムの準備状況確認\n- 効果的な通信チャネルの確保\n\n3. 組織的な準備\n- 従業員の安全意識向上\n- インシデント管理能力の改善\n- 事業継続計画のサポート\n\n訓練前準備：\n- 予備トレーニングセッションの計画\n- 参加者への包括的な説明\n- 技術システムの準備状況確認\n\n重要性：\n- 災害への先見的なアプローチ\n- 会社全体の安全文化の発展\n- 効果的な緊急管理に不可欠\n\n背景：\n- 定期的な防災活動の一環\n- 機能的な機関との連携\n- 会社のオフィスと寮で実施\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害対応",
        "事業継続"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Thông Báo Diễn Tập Phòng Chống Thiên Tai Toàn Diện Chi Nhánh Tochigi của FJP",
      "content": "Thông Báo Diễn Tập Phòng Chống Thiên Tai Toàn Diện\n\nChi Tiết Sự Kiện:\n- Ngày: 4 tháng 10\n- Người Tham Gia:\n  * Nhân viên Chi nhánh Tochigi\n  * Nhân viên làm việc tại các địa điểm khách hàng\n  * Dự kiến Tỷ lệ Tham gia: 100% Nhân viên Chi nhánh Tochigi\n\nMục Tiêu Diễn Tập:\n1. Đào Tạo Ứng Phó Khẩn Cấp\n- Mô phỏng Kịch bản Động đất (Độ lớn 5+)\n- Phát triển Kỹ năng Ứng phó Sự cố\n- Kiểm tra Giao thức Khẩn cấp\n\n2. Tích Hợp Công Nghệ\n- Xác thực Chức năng Ứng dụng Mykintai/Anpi\n- Kiểm tra Tính Sẵn sàng của Hệ thống\n- Đảm bảo Các Kênh Truyền thông Hiệu quả\n\n3. Sự Chuẩn Bị của Tổ Chức\n- Nâng cao Nhận thức An toàn của Nhân viên\n- Cải thiện Năng lực Quản lý Sự cố\n- Hỗ trợ Kế hoạch Liên tục Kinh doanh\n\nChuẩn Bị Trước Diễn Tập:\n- Lên lịch Phiên Đào tạo Sơ bộ\n- Brifing Toàn diện cho Người tham gia\n- Kiểm tra Tính Sẵn sàng Hệ thống Kỹ thuật\n\nÝ Nghĩa:\n- Cách Tiếp cận Chủ động về Chuẩn bị Thiên tai\n- Phát triển Văn hóa An toàn Toàn công ty\n- Quan trọng cho Quản lý Khẩn cấp Hiệu quả\n\nBối Cảnh:\n- Là một phần của Các hoạt động Phòng chống Thiên tai Thường kỳ\n- Phối hợp với Các cơ quan Chức năng\n- Được thực hiện tại Văn phòng và Ký túc xá Công ty\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Đào Tạo Khẩn Cấp",
        "Ứng Phó Thiên Tai",
        "Liên Tục Kinh Doanh"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Comprehensive Disaster Prevention Drill Campaign 2025",
      "content": "Comprehensive Disaster Prevention Initiative Overview\n\nCampaign Structure:\n- Duration: May to October 2025\n- Phased Approach with Three Stages\n  1. First Phase: Nagoya (June 2nd)\n  2. Second Phase: Smaller Offices Outside Kanto (July)\n  3. Third Phase: Kanto Region (Early October)\n\nDrill Objectives:\n1. Employee Preparedness\n- Equip staff with disaster response skills\n- Enhance safety awareness\n- Develop proactive emergency management capabilities\n\n2. Safety Confirmation Process\n- Large-Scale Earthquake Scenario Simulation\n- Multi-Channel Safety Verification:\n  * My Kintai App\n  * Email\n  * Work Chat\n\n3. Communication Protocol\n- Anpi Tool Signal Mechanism:\n  * 3 Signal Attempts for Non-Responsive Employees\n  * Data Aggregation\n  * HR Follow-up for Unresponsive or At-Risk Employees\n\nContextual Background:\n- Japan's Seismic Landscape:\n  * 1-3 Earthquakes Daily\n  * Approximately 1,000 Earthquakes Annually\n- Earthquakes Considered a National Characteristic\n\nKey Event Details:\n- Seminar Date: May 24th\n- Seminar Platform: Livestreamed in FJP Group\n- Target Participation: 100% Employee Involvement\n\nLong-Term Goals:\n- Annual Disaster Preparedness Training\n- Continuous Improvement of Emergency Response\n- Organizational Resilience Development\n\nSignificance:\n- Proactive Approach to Employee Safety\n- Business Continuity Planning\n- Building a Culture of Emergency Preparedness\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "DisasterResponse",
        "BusinessContinuity"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP包括的防災訓練キャンペーン2025",
      "content": "包括的防災イニシアチブの概要\n\nキャンペーン構造：\n- 期間：2025年5月から10月\n- 3段階のアプローチ\n  1. 第1段階：名古屋（6月2日）\n  2. 第2段階：関東地域外の小規模オフィス（7月）\n  3. 第3段階：関東地域（10月初旬）\n\n訓練目的：\n1. 従業員の準備\n- 災害対応スキルの習得\n- 安全意識の向上\n- 積極的な緊急管理能力の開発\n\n2. 安全確認プロセス\n- 大規模地震シナリオのシミュレーション\n- 多チャンネル安全確認：\n  * My Kintaiアプリ\n  * メール\n  * ワークチャット\n\n3. 通信プロトコル\n- Anpiツールシグナルメカニズム：\n  * 無応答従業員への3回の信号送信\n  * データ集計\n  * 無応答または危険な従業員へのHR フォローアップ\n\n背景：\n- 日本の地震環境：\n  * 1日1〜3回の地震\n  * 年間約1,000回の地震\n- 地震は国の特徴とされる\n\n主要イベント詳細：\n- セミナー日：5月24日\n- セミナープラットフォーム：FJPグループでライブストリーミング\n- 目標参加率：従業員100%参加\n\n長期目標：\n- 年次防災訓練\n- 緊急対応の継続的改善\n- 組織的レジリエンスの構築\n\n意義：\n- 従業員安全への積極的アプローチ\n- 事業継続計画\n- 緊急時準備文化の構築\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害対応",
        "事業継続"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Chiến Dịch Diễn Tập Phòng Chống Thiên Tai Toàn Diện của FJP 2025",
      "content": "Tổng Quan Sáng Kiến Phòng Chống Thiên Tai\n\nCấu Trúc Chiến Dịch:\n- Thời Gian: Từ tháng 5 đến tháng 10 năm 2025\n- Tiếp Cận Theo 3 Giai Đoạn\n  1. Giai Đoạn 1: Nagoya (Ngày 2 tháng 6)\n  2. Giai Đoạn 2: Các Văn Phòng Nhỏ Ngoài Khu Vực Kanto (Tháng 7)\n  3. Giai Đoạn 3: Khu Vực Kanto (Đầu tháng 10)\n\nMục Tiêu Diễn Tập:\n1. Chuẩn Bị Cho Nhân Viên\n- Trang bị kỹ năng ứng phó thiên tai\n- Nâng cao nhận thức an toàn\n- Phát triển năng lực quản lý khẩn cấp chủ động\n\n2. Quy Trình Xác Nhận An Toàn\n- Mô Phỏng Kịch Bản Động Đất Quy Mô Lớn\n- Xác Minh An Toàn Đa Kênh:\n  * Ứng Dụng My Kintai\n  * Email\n  * Work Chat\n\n3. Giao Thức Truyền Thông\n- Cơ Chế Tín Hiệu Công Cụ Anpi:\n  * 3 Lần Gửi Tín Hiệu Cho Nhân Viên Không Phản Hồi\n  * Tổng Hợp Dữ Liệu\n  * Theo Dõi của Nhân Sự Đối Với Nhân Viên Không Phản Hồi hoặc Có Nguy Cơ\n\nBối Cảnh:\n- Bối Cảnh Địa Chấn Nhật Bản:\n  * 1-3 Trận Động Đất Hàng Ngày\n  * Khoảng 1,000 Trận Động Đất Mỗi Năm\n- Động Đất Được Coi Là Đặc Trưng Quốc Gia\n\nChi Tiết Sự Kiện Chính:\n- Ngày Hội Thảo: 24 tháng 5\n- Nền Tảng Hội Thảo: Phát Trực Tiếp Trên Nhóm FJP\n- Mục Tiêu Tham Gia: 100% Nhân Viên Tham Gia\n\nMục Tiêu Dài Hạn:\n- Đào Tạo Phòng Chống Thiên Tai Hàng Năm\n- Cải Thiện Liên Tục Ứng Phó Khẩn Cấp\n- Phát Triển Khả Năng Chống Chịu Của Tổ Chức\n\nÝ Nghĩa:\n- Cách Tiếp Cận Chủ Động Về An Toàn Nhân Viên\n- Kế Hoạch Liên Tục Kinh Doanh\n- Xây Dựng Văn Hóa Sẵn Sàng Ứng Phó Khẩn Cấp\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Đào Tạo Khẩn Cấp",
        "Ứng Phó Thiên Tai",
        "Liên Tục Kinh Doanh"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Aichi Prefecture Earthquake Safety Drill",
      "content": "Comprehensive Safety Confirmation Exercise Details\n\nDrill Specifications:\n- Date: June 2nd, 2023 (Friday)\n- Time: 12:00 PM\n- Location: Aichi Prefecture\n- Target Participants: Employees Residing/Working in Aichi\n\nDrill Scenario:\n1. Earthquake Simulation\n- Magnitude: 5+ on the Seismic Scale\n- Simulated Disaster Context: Large-scale Earthquake\n\n2. Safety Confirmation Process\n- Communication Channels:\n  * MyKintai App\n  * Workchat\n  * Email\n- Confirmation Rounds: 3 Consecutive Attempts\n- Employee Response Options:\n  * SAFE\n  * UNSAFE (with Situation Details)\n\n3. Organizational Response Protocol\n- Immediate Data Collection by FET (Disaster Response Committee)\n- Follow-up for Non-Responsive Employees\n  * Contact Department Heads\n  * Direct Employee Outreach\n- Comprehensive Safety Status Tracking\n\nDrill Objectives:\n- Rapid Safety Status Assessment\n- Emergency Communication Testing\n- Organizational Preparedness Validation\n- Employee Safety Awareness Enhancement\n\nSupport Contacts:\n- Drill Details: FJP.HR@fpt.com\n- Technical Support: FJP.Tool.Team@fpt.com\n\nKey Outcomes:\n- Validate Emergency Communication Systems\n- Identify Potential Improvement Areas\n- Enhance Organizational Resilience\n\nSignificance:\n- Proactive Disaster Preparedness\n- Employee Safety Priority\n- Systematic Emergency Response Development\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "DisasterResponse",
        "CommunicationProtocol"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP愛知県地震安否確認訓練",
      "content": "包括的な安全確認演習の詳細\n\n訓練詳細：\n- 日付：2023年6月2日（金）\n- 時間：午後12時\n- 場所：愛知県\n- 対象参加者：愛知県在住・勤務の従業員\n\n訓練シナリオ：\n1. 地震シミュレーション\n- マグニチュード：震度5+\n- 想定災害状況：大規模地震\n\n2. 安否確認プロセス\n- 通信チャンネル：\n  * MyKintaiアプリ\n  * Workchat\n  * メール\n- 確認ラウンド：3回連続試行\n- 従業員の回答オプション：\n  * 安全（SAFE）\n  * 安全ではない（UNSAFE、状況詳細）\n\n3. 組織的対応プロトコル\n- FET（災害対策委員会）による即時データ収集\n- 無応答従業員へのフォローアップ\n  * 部門長への連絡\n  * 直接的な従業員への連絡\n- 包括的な安全状況追跡\n\n訓練目的：\n- 迅速な安全状況評価\n- 緊急時通信テスト\n- 組織的な準備状況の検証\n- 従業員の安全意識向上\n\nサポート連絡先：\n- 訓練詳細：FJP.HR@fpt.com\n- 技術サポート：FJP.Tool.Team@fpt.com\n\n主な成果：\n- 緊急時通信システムの検証\n- 改善点の特定\n- 組織的な回復力の強化\n\n意義：\n- 積極的な災害への備え\n- 従業員の安全最優先\n- 体系的な緊急対応の開発\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害対応",
        "通信プロトコル"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Diễn Tập Xác Nhận An Toàn FJP Tỉnh Aichi",
      "content": "Chi Tiết Cuộc Diễn Tập Xác Nhận An Toàn Toàn Diện\n\nThông Số Diễn Tập:\n- Ngày: 2 tháng 6, 2023 (Thứ Sáu)\n- Thời Gian: 12:00 Trưa\n- Địa Điểm: Tỉnh Aichi\n- Đối Tượng Tham Gia: Nhân Viên Cư Trú/Làm Việc Tại Aichi\n\nKịch Bản Diễn Tập:\n1. Mô Phỏng Động Đất\n- Độ Lớn: 5+ Trên Thang Động Đất\n- Bối Cảnh Thảm Họa Giả Định: Động Đất Quy Mô Lớn\n\n2. Quy Trình Xác Nhận An Toàn\n- Kênh Truyền Thông:\n  * Ứng Dụng MyKintai\n  * Workchat\n  * Email\n- Vòng Xác Nhận: 3 Lần Thử Liên Tiếp\n- Tùy Chọn Phản Hồi Nhân Viên:\n  * AN TOÀN\n  * KHÔNG AN TOÀN (với Chi Tiết Tình Trạng)\n\n3. Giao Thức Ứng Phó Của Tổ Chức\n- Thu Thập Dữ Liệu Ngay Lập Tức bởi FET (Ủy Ban Ứng Phó Thảm Họa)\n- Theo Dõi Đối Với Nhân Viên Không Phản Hồi\n  * Liên Hệ Trưởng Phòng\n  * Tiếp Cận Trực Tiếp Nhân Viên\n- Theo Dõi Toàn Diện Trạng Thái An Toàn\n\nMục Tiêu Diễn Tập:\n- Đánh Giá Nhanh Chóng Trạng Thái An Toàn\n- Kiểm Tra Truyền Thông Khẩn Cấp\n- Xác Nhận Sự Sẵn Sàng Của Tổ Chức\n- Nâng Cao Nhận Thức An Toàn Của Nhân Viên\n\nLiên Hệ Hỗ Trợ:\n- Chi Tiết Diễn Tập: FJP.HR@fpt.com\n- Hỗ Trợ Kỹ Thuật: FJP.Tool.Team@fpt.com\n\nKết Quả Chính:\n- Xác Thực Hệ Thống Truyền Thông Khẩn Cấp\n- Xác Định Các Khu Vực Cần Cải Thiện\n- Tăng Cường Khả Năng Phục Hồi Của Tổ Chức\n\nÝ Nghĩa:\n- Sẵn Sàng Chủ Động Ứng Phó Thảm Họa\n- Ưu Tiên An Toàn Nhân Viên\n- Phát Triển Hệ Thống Ứng Phó Khẩn Cấp\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Đào Tạo Khẩn Cấp",
        "Ứng Phó Thiên Tai",
        "Giao Thức Truyền Thông"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Aichi Prefecture Disaster Prevention Drill Outcomes",
      "content": "Comprehensive Drill Completion Summary\n\nDrill Overview:\n- Location: Aichi Prefecture\n- Scenario: Large-Scale Earthquake Simulation\n- Primary Objective: Employee Safety Confirmation\n\nDrill Execution Details:\n1. Safety Verification Channels\n- My Kintai App\n- Email\n- Workchat\n\n2. Verification Process\n- Anpi Tool Signal Transmission\n- Multiple Confirmation Attempts\n- Comprehensive Response Tracking\n\n3. Response Capability Testing\n- Deliberate \"Unsafe\" Responses Introduced\n- Liaison Team Verification of Critical Cases\n- Emergency Response Team (FET) Reaction Assessment\n\nOrganizational Context:\n- Emergency Taskforce (FET) Established: August 2018\n- Core Mission: Professional Protection of \n  * Employee Lives\n  * Company Assets\n- Key Responsibilities:\n  * Action Plan Development\n  * Emergency Training\n  * Preventive Measure Preparation\n\nDrill Significance:\n- Validate Emergency Communication Systems\n- Test Organizational Responsiveness\n- Enhance Disaster Preparedness\n- Identify Potential Improvement Areas\n\nKey Achievements:\n- Successful Multi-Channel Safety Verification\n- Comprehensive Emergency Response Simulation\n- Proactive Risk Management Demonstration\n\nContinuous Improvement Focus:\n- Refine Emergency Response Protocols\n- Enhance Employee Safety Awareness\n- Develop More Robust Communication Systems\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "DisasterResponse",
        "OrganizationalResilience"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP愛知県防災訓練 完了報告",
      "content": "包括的な訓練完了サマリー\n\n訓練概要：\n- 場所：愛知県\n- シナリオ：大規模地震シミュレーション\n- 主な目的：従業員の安全確認\n\n訓練実施詳細：\n1. 安全確認チャンネル\n- My Kintaiアプリ\n- メール\n- Workchat\n\n2. 確認プロセス\n- Anpiツール信号送信\n- 複数回の確認試行\n- 包括的な応答追跡\n\n3. 対応能力テスト\n- 意図的な「安全ではない」応答の導入\n- 連絡チームによる重要ケースの検証\n- 緊急対応チーム（FET）の反応評価\n\n組織的背景：\n- 緊急タスクフォース（FET）設立：2018年8月\n- 中核的ミッション：専門的な保護\n  * 従業員の生命\n  * 会社の資産\n- 主な責任：\n  * 行動計画の策定\n  * 緊急時訓練\n  * 予防措置の準備\n\n訓練の重要性：\n- 緊急時通信システムの検証\n- 組織的対応能力のテスト\n- 災害への備えの強化\n- 改善点の特定\n\n主な成果：\n- 多チャンネル安全確認の成功\n- 包括的な緊急対応シミュレーション\n- 積極的なリスク管理の実証\n\n継続的改善の焦点：\n- 緊急対応プロトコルの改良\n- 従業員の安全意識向上\n- より堅牢な通信システムの開発\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害対応",
        "組織的回復力"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Báo Cáo Hoàn Thành Diễn Tập Phòng Chống Thiên Tai FJP Tỉnh Aichi",
      "content": "Tóm Tắt Toàn Diện Về Diễn Tập Đã Hoàn Thành\n\nTổng Quan Diễn Tập:\n- Địa Điểm: Tỉnh Aichi\n- Kịch Bản: Mô Phỏng Động Đất Quy Mô Lớn\n- Mục Tiêu Chính: Xác Nhận An Toàn Nhân Viên\n\nChi Tiết Thực Hiện Diễn Tập:\n1. Kênh Xác Minh An Toàn\n- Ứng Dụng My Kintai\n- Email\n- Workchat\n\n2. Quy Trình Xác Nhận\n- Truyền Tín Hiệu Công Cụ Anpi\n- Nhiều Lần Thử Xác Nhận\n- Theo Dõi Phản Hồi Toàn Diện\n\n3. Kiểm Tra Năng Lực Ứng Phó\n- Giới Thiệu Phản Hồi \"Không An Toàn\" Có Chủ Đích\n- Xác Minh Các Trường Hợp Quan Trọng Bởi Đội Liên Lạc\n- Đánh Giá Phản Ứng Của Nhóm Ứng Phó Khẩn Cấp (FET)\n\nBối Cảnh Tổ Chức:\n- Thành Lập Lực Lượng Nhiệm Vụ Khẩn Cấp (FET): Tháng 8/2018\n- Sứ Mệnh Cốt Lõi: Bảo Vệ Chuyên Nghiệp\n  * Sinh Mạng Nhân Viên\n  * Tài Sản Công Ty\n- Trách Nhiệm Chính:\n  * Phát Triển Kế Hoạch Hành Động\n  * Đào Tạo Khẩn Cấp\n  * Chuẩn Bị Các Biện Pháp Phòng Ngừa\n\nÝ Nghĩa Của Diễn Tập:\n- Xác Thực Hệ Thống Truyền Thông Khẩn Cấp\n- Kiểm Tra Khả Năng Ứng Phó của Tổ Chức\n- Tăng Cường Sự Sẵn Sàng Ứng Phó Thảm Họa\n- Xác Định Các Khu Vực Cần Cải Thiện\n\nThành Tựu Chính:\n- Xác Minh An Toàn Đa Kênh Thành Công\n- Mô Phỏng Ứng Phó Khẩn Cấp Toàn Diện\n- Minh Chứng Quản Lý Rủi Ro Chủ Động\n\nTrọng Tâm Cải Tiến Liên Tục:\n- Tinh Chỉnh Các Giao Thức Ứng Phó Khẩn Cấp\n- Nâng Cao Nhận Thức An Toàn Của Nhân Viên\n- Phát Triển Hệ Thống Truyền Thông Mạnh Mẽ Hơn\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Đào Tạo Khẩn Cấp",
        "Ứng Phó Thiên Tai",
        "Khả Năng Phục Hồi Tổ Chức"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP Disaster Prevention Drill in Aichi Prefecture",
      "content": "Comprehensive Drill Event Specifications\n\nEvent Overview:\n- Date: June 2nd\n- Time: 11:30 AM - 2:00 PM\n- Location: Aichi Prefecture\n- Target Participants: All FJP Employees in Aichi\n\nDrill Scenario:\n1. Emergency Simulation\n- Scenario: Large-Scale Earthquake\n- Objective: Employee Safety Confirmation\n\n2. Communication and Verification Process\n- Communication Channels:\n  * My Kintai App\n  * Email\n  * Workchat\n\n3. Safety Confirmation Mechanism\n- Anpi Tool Signal Transmission\n  * 3 Consecutive Signal Attempts for Non-Responsive Employees\n  * Comprehensive Data Aggregation\n\n4. Organizational Response\n- Human Resources Department Follow-up\n  * Contact Non-Responsive Employees\n  * Reach Out to Employees Reporting Unsafe Conditions\n  * Provide Specific Follow-up Instructions\n\nKey Operational Details:\n- Signal Transmission Methodology\n- Multi-Channel Communication Strategy\n- Systematic Safety Status Tracking\n\nDrill Significance:\n- Validate Emergency Communication Systems\n- Test Organizational Responsiveness\n- Enhance Employee Safety Preparedness\n- Develop Robust Crisis Management Protocols\n\nExpected Outcomes:\n- Comprehensive Safety Status Assessment\n- Identification of Communication Gaps\n- Improvement of Emergency Response Mechanisms\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyTraining",
        "DisasterResponse",
        "CommunicationProtocol"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "FJP愛知県防災訓練の詳細",
      "content": "包括的な訓練イベントの仕様\n\nイベント概要：\n- 日付：6月2日\n- 時間：午前11:30 - 午後2:00\n- 場所：愛知県\n- 対象参加者：愛知県のFJP全従業員\n\n訓練シナリオ：\n1. 緊急事態シミュレーション\n- シナリオ：大規模地震\n- 目的：従業員の安全確認\n\n2. 通信と確認プロセス\n- 通信チャンネル：\n  * My Kintaiアプリ\n  * メール\n  * Workchat\n\n3. 安全確認メカニズム\n- Anpiツール信号送信\n  * 無応答従業員への3回の連続信号\n  * 包括的データ集計\n\n4. 組織的対応\n- 人事部門によるフォローアップ\n  * 無応答従業員への連絡\n  * 安全でない状況を報告した従業員への連絡\n  * 具体的な指示の提供\n\n主要な運用詳細：\n- 信号送信方法論\n- 多チャンネル通信戦略\n- 体系的な安全状況追跡\n\n訓練の重要性：\n- 緊急時通信システムの検証\n- 組織的対応能力のテスト\n- 従業員の安全準備の強化\n- 堅牢な危機管理プロトコルの開発\n\n期待される成果：\n- 包括的な安全状況評価\n- 通信ギャップの特定\n- 緊急対応メカニズムの改善\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急訓練",
        "災害対応",
        "通信プロトコル"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Chi Tiết Diễn Tập Phòng Chống Thiên Tai của FJP tại Tỉnh Aichi",
      "content": "Thông Số Chi Tiết Sự Kiện Diễn Tập Toàn Diện\n\nTổng Quan Sự Kiện:\n- Ngày: 2 tháng 6\n- Thời Gian: 11:30 Sáng - 2:00 Chiều\n- Địa Điểm: Tỉnh Aichi\n- Đối Tượng Tham Gia: Toàn Bộ Nhân Viên FJP tại Aichi\n\nKịch Bản Diễn Tập:\n1. Mô Phỏng Tình Huống Khẩn Cấp\n- Kịch Bản: Động Đất Quy Mô Lớn\n- Mục Tiêu: Xác Nhận An Toàn Nhân Viên\n\n2. Quy Trình Truyền Thông và Xác Minh\n- Kênh Truyền Thông:\n  * Ứng Dụng My Kintai\n  * Email\n  * Workchat\n\n3. Cơ Chế Xác Nhận An Toàn\n- Truyền Tín Hiệu Công Cụ Anpi\n  * 3 Lần Thử Tín Hiệu Cho Nhân Viên Không Phản Hồi\n  * Tổng Hợp Dữ Liệu Toàn Diện\n\n4. Phản Ứng Của Tổ Chức\n- Theo Dõi Của Phòng Nhân Sự\n  * Liên Hệ Nhân Viên Không Phản Hồi\n  * Tiếp Cận Nhân Viên Báo Cáo Tình Trạng Không An Toàn\n  * Cung Cấp Hướng Dẫn Cụ Thể\n\nChi Tiết Vận Hành Chính:\n- Phương Pháp Truyền Tín Hiệu\n- Chiến Lược Truyền Thông Đa Kênh\n- Theo Dõi Trạng Thái An Toàn Có Hệ Thống\n\nÝ Nghĩa Của Diễn Tập:\n- Xác Thực Hệ Thống Truyền Thông Khẩn Cấp\n- Kiểm Tra Khả Năng Ứng Phó Của Tổ Chức\n- Tăng Cường Sự Chuẩn Bị An Toàn Của Nhân Viên\n- Phát Triển Các Giao Thức Quản Lý Khủ\n",
      "category": "General",
      "language": "en",
      "tags": [
        "ANPI",
        "Safety"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Comprehensive Guide to Disaster Communication Channels in Japan",
      "content": "Emergency Communication and Information Sources During Disasters\n\nPrimary Communication Channels:\n1. Radio\n- Reliable real-time information source\n- Accessible during power outages\n- Provides emergency broadcasts and updates\n\n2. Television\n- Nationwide emergency broadcasting\n- Visual information and evacuation instructions\n- Multiple language support for international residents\n\n3. Government Radio Stations\n- Official emergency communication\n- Authoritative and timely information\n- Coordinated disaster response updates\n\n4. Public Information Vehicles\n- Mobile communication units\n- Direct local area announcements\n- Evacuation route guidance\n\n5. Digital Platforms\n- Safety Tips Mobile Application\n  * Comprehensive disaster information\n  * Real-time alerts and notifications\n  * Multi-language support\n  * Recommended for all residents and visitors\n\n6. Official Websites\n- Japan Meteorological Agency Disaster Information\n  * URL: https://www.jma.go.jp/jma/kokusai/multi.html\n  * Comprehensive meteorological and disaster data\n  * Multilingual disaster updates\n\n7. Additional Digital Resources\n- NHK WORLD-JAPAN Stay Safe Portal\n  * URL: https://www3.nhk.or.jp/nhkworld/en/special/staysafe/\n  * Comprehensive emergency guidance\n  * Multilingual emergency information\n\nRecommended Preparation Steps:\n- Download Safety Tips app in advance\n- Save important emergency websites\n- Keep battery-powered or hand-crank radio\n- Understand local evacuation procedures\n\nKey Benefits:\n- Rapid information dissemination\n- Comprehensive emergency coverage\n- Multilingual support\n- Multiple redundant communication channels\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyCommunication",
        "DisasterResponse",
        "InformationChannels"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "日本の災害時通信チャンネル総合ガイド",
      "content": "災害時の緊急通信および情報源\n\n主要な通信チャンネル：\n1. ラジオ\n- 信頼性の高いリアルタイム情報源\n- 停電時にも利用可能\n- 緊急放送と最新情報の提供\n\n2. テレビ\n- 全国規模の緊急放送\n- 視覚的情報と避難指示\n- 外国人向け多言語サポート\n\n3. 政府放送局\n- 公式の緊急通信\n- 信頼性の高い最新情報\n- 災害対応の coordinated な更新\n\n4. 公共情報車両\n- 移動式通信ユニット\n- 直接的な地域アナウンス\n- 避難経路案内\n\n5. デジタルプラットフォーム\n- Safety Tips モバイルアプリ\n  * 包括的な災害情報\n  * リアルタイム警報と通知\n  * 多言語サポート\n  * 全居住者と訪問者に推奨\n\n6. 公式ウェブサイト\n- 気象庁災害情報\n  * URL: https://www.jma.go.jp/jma/kokusai/multi.html\n  * 包括的な気象および災害データ\n  * 多言語災害情報\n\n7. 追加デジタルリソース\n- NHK WORLD-JAPAN 安全ポータル\n  * URL: https://www3.nhk.or.jp/nhkworld/en/special/staysafe/\n  * 包括的な緊急ガイダンス\n  * 多言語緊急情報\n\n推奨される準備手順：\n- 事前にSafety Tipsアプリをダウンロード\n- 重要な緊急ウェブサイトを保存\n- 電池式または手回し充電ラジオを用意\n- 地域の避難手順を理解\n\n主な利点：\n- 迅速な情報伝達\n- 包括的な緊急対応カバレッジ\n- 多言語サポート\n- 複数の冗長な通信チャンネル\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急通信",
        "災害対応",
        "情報チャンネル"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Hướng Dẫn Toàn Diện về Các Kênh Thông Tin Khẩn Cấp tại Nhật Bản",
      "content": "Nguồn Thông Tin và Liên Lạc Khẩn Cấp Trong Thiên Tai\n\nCác Kênh Liên Lạc Chính:\n1. Radio\n- Nguồn thông tin thời gian thực đáng tin cậy\n- Có thể truy cập trong trường hợp mất điện\n- Cung cấp các bản tin và cập nhật khẩn cấp\n\n2. Truyền Hình\n- Phát sóng khẩn cấp trên toàn quốc\n- Thông tin hình ảnh và hướng dẫn sơ tán\n- Hỗ trợ nhiều ngôn ngữ cho cư dân quốc tế\n\n3. Đài Phát Thanh Chính Phủ\n- Thông tin liên lạc khẩn cấp chính thức\n- Thông tin có thẩm quyền và kịp thời\n- Cập nhật ứng phó thảm họa có điều phối\n\n4. Xe Thông Tin Công Cộng\n- Đơn vị truyền thông di động\n- Thông báo trực tiếp tại khu vực\n- Hướng dẫn tuyến đường sơ tán\n\n5. Nền Tảng Kỹ Thuật Số\n- Ứng Dụng Safety Tips\n  * Thông tin thảm họa toàn diện\n  * Cảnh báo và thông báo thời gian thực\n  * Hỗ trợ đa ngôn ngữ\n  * Được khuyến nghị cho tất cả cư dân và du khách\n\n6. Trang Web Chính Thức\n- Thông Tin Thảm Họa của Cơ Quan Khí Tượng Nhật Bản\n  * URL: https://www.jma.go.jp/jma/kokusai/multi.html\n  * Dữ liệu khí tượng và thảm họa toàn diện\n  * Cập nhật thảm họa đa ngôn ngữ\n\n7. Tài Nguyên Kỹ Thuật Số Bổ Sung\n- Cổng Thông Tin An Toàn NHK WORLD-JAPAN\n  * URL: https://www3.nhk.or.jp/nhkworld/en/special/staysafe/\n  * Hướng dẫn khẩn cấp toàn diện\n  * Thông tin khẩn cấp đa ngôn ngữ\n\nCác Bước Chuẩn Bị Được Khuyến Nghị:\n- Tải ứng dụng Safety Tips trước\n- Lưu các trang web khẩn cấp quan trọng\n- Chuẩn bị radio chạy bằng pin hoặc quay tay\n- Hiểu các quy trình sơ tán địa phương\n\nƯu Điểm Chính:\n- Phát tán thông tin nhanh chóng\n- Bao phủ khẩn cấp toàn diện\n- Hỗ trợ đa ngôn ngữ\n- Nhiều kênh liên lạc dự phòng\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Truyền Thông Khẩn Cấp",
        "Ứng Phó Thảm Họa",
        "Kênh Thông Tin"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Comprehensive Disaster Emergency Communication and Preparedness Guide",
      "content": "Critical Survival Strategies During Disasters\n\nPrimary Mental Preparation:\n1. Stay Calm\n- Emotional Control is Crucial\n- Clear Thinking Enables Better Decision Making\n- Panic Reduces Effective Problem Solving\n\nEmergency Communication Protocols:\n1. Emergency Message Service (*171)\n- Universal Disaster Communication Number\n- Usable on:\n  * Landline Phones\n  * Mobile Phones\n  * Public Telephones\n\nMessage Leaving Process:\n- Dial *171\n- Press *1* and home phone number\n- Press 1#\n- Record 30-second message\n- Press 9#\n\nMessage Retrieval Process:\n- Dial *171\n- Press *2* and home phone number\n- Press 1#\n- Listen to messages\n- Press 9#\n\nAlternative Digital Communication:\n- Web171 Disaster Message Board\n  * URL: https://www.web171.jp/\n  * Internet-based messaging service\n  * Accessible during large-scale disasters\n\nFinancial Preparedness:\n- Keep 10,000-20,000 JPY in cash\n- Prepare for potential:\n  * Power outages\n  * ATM unavailability\n  * Electronic payment system failures\n\nEmergency Preparedness Kit:\n- Recommended Resources:\n  * Comprehensive Kit Guide: \n    https://www.pro-bousai.jp/shopdetail/000000000001/\n  * Detailed Checklist: \n    http://www.yokohamashakyo.jp/higashitotsuka/pdf/checklist.pdf\n\nRecommended Kit Contents:\n- Essential Documents\n- First Aid Supplies\n- Non-Perishable Food\n- Water\n- Flashlight\n- Battery-Powered Radio\n- Extra Batteries\n- Personal Medications\n- Emergency Contact Information\n\nKey Principles:\n- Mental Calmness\n- Advance Preparation\n- Multiple Communication Channels\n- Financial Flexibility\n",
      "category": "DisasterPreparedness",
      "language": "en",
      "tags": [
        "Safety",
        "EmergencyCommunication",
        "DisasterResponse",
        "SurvivalSkills"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "災害時の緊急通信および防災ガイド",
      "content": "災害時の重要な生存戦略\n\n精神的準備の基本：\n1. 冷静さを保つ\n- 感情のコントロールが重要\n- 明確な思考が適切な意思決定を可能にする\n- パニックは効果的な問題解決を妨げる\n\n緊急通信プロトコル：\n1. 災害用伝言ダイヤル（*171）\n- 汎用災害通信番号\n- 利用可能な通信手段：\n  * 固定電話\n  * 携帯電話\n  * 公衆電話\n\nメッセージ録音プロセス：\n- *171にダイヤル\n- *1*と自宅の電話番号を押す\n- 1#を押す\n- 30秒のメッセージを録音\n- 9#を押す\n\nメッセージ再生プロセス：\n- *171にダイヤル\n- *2*と自宅の電話番号を押す\n- 1#を押す\n- メッセージを聴く\n- 9#を押す\n\n代替デジタル通信：\n- Web171災害伝言板\n  * URL: https://www.web171.jp/\n  * インターネットベースのメッセージサービス\n  * 大規模災害時にアクセス可能\n\n財務的準備：\n- 現金を10,000〜20,000円用意\n- 以下に備える：\n  * 停電\n  * ATM利用不可\n  * 電子決済システムの障害\n\n緊急時防災キット：\n- おすすめリソース：\n  * 包括的キットガイド：\n    https://www.pro-bousai.jp/shopdetail/000000000001/\n  * 詳細チェックリスト：\n    http://www.yokohamashakyo.jp/higashitotsuka/pdf/checklist.pdf\n\n推奨キット内容：\n- 重要書類\n- 救急用品\n- 非常食\n- 水\n- 懐中電灯\n- 電池式ラジオ\n- 予備電池\n- 個人用薬\n- 緊急連絡先情報\n\n重要原則：\n- 精神的冷静さ\n- 事前準備\n- 複数の通信チャンネル\n- 財務的柔軟性\n",
      "category": "防災対策",
      "language": "ja",
      "tags": [
        "安全",
        "緊急通信",
        "災害対応",
        "生存スキル"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    },
    {
      "title": "Hướng Dẫn Liên Lạc Khẩn Cấp và Phòng Chống Thiên Tai tại Nhật Bản",
      "content": "Chiến Lược Sống Sót Quan Trọng Trong Thiên Tai\n\nChuẩn Bị Tinh Thần Chính:\n1. Giữ Bình Tĩnh\n- Kiểm Soát Cảm Xúc Là Điều Quan Trọng\n- Suy Nghĩ Rõ Ràng Giúp Ra Quyết Định Tốt Hơn\n- Hoảng Loạn Làm Giảm Khả Năng Giải Quyết Vấn Đề\n\nGiao Thức Liên Lạc Khẩn Cấp:\n1. Dịch Vụ Tin Nhắn Khẩn Cấp (*171)\n- Số Liên Lạc Thiên Tai Đa Năng\n- Có Thể Sử Dụng Trên:\n  * Điện Thoại Cố Định\n  * Điện Thoại Di Động\n  * Điện Thoại Công Cộng\n\nQuy Trình Để Lại Tin Nhắn:\n- Gọi *171\n- Nhấn *1* và số điện thoại nhà\n- Nhấn 1#\n- Ghi âm tin nhắn 30 giây\n- Nhấn 9#\n\nQuy Trình Nghe Tin Nhắn:\n- Gọi *171\n- Nhấn *2* và số điện thoại nhà\n- Nhấn 1#\n- Nghe tin nhắn\n- Nhấn 9#\n\nPhương Thức Liên Lạc Kỹ Thuật Số Thay Thế:\n- Bảng Tin Thiên Tai Web171\n  * URL: https://www.web171.jp/\n  * Dịch vụ nhắn tin trên internet\n  * Truy cập được trong các thảm họa quy mô lớn\n\nChuẩn Bị Tài Chính:\n- Giữ 10.000-20.000 JPY tiền mặt\n- Chuẩn bị cho khả năng:\n  * Mất điện\n  * ATM không hoạt động\n  * Lỗi hệ thống thanh toán điện tử\n\nBộ Dụng Cụ Khẩn Cấp:\n- Tài Nguyên Được Khuyến Nghị:\n  * Hướng Dẫn Bộ Kit Toàn Diện: \n    https://www.pro-bousai.jp/shopdetail/000000000001/\n  * Danh Sách Kiểm Tra Chi Tiết: \n    http://www.yokohamashakyo.jp/higashitotsuka/pdf/checklist.pdf\n\nNội Dung Bộ Kit Được Khuyến Nghị:\n- Giấy Tờ Quan Trọng\n- Vật Dụng Sơ Cứu\n- Thực Phẩm Khô\n- Nước\n- Đèn Pin\n- Radio Chạy Pin\n- Pin Dự Phòng\n- Thuốc Cá Nhân\n- Thông Tin Liên Hệ Khẩn Cấp\n\nNguyên Tắc Chính:\n- Bình Tĩnh Tinh Thần\n- Chuẩn Bị Trước\n- Nhiều Kênh Liên Lạc\n- Linh Hoạt Tài Chính\n",
      "category": "Phòng Chống Thiên Tai",
      "language": "vi",
      "tags": [
        "An Toàn",
        "Truyền Thông Khẩn Cấp",
        "Ứng Phó Thiên Tai",
        "Kỹ Năng Sinh Tồn"
      ],
      "createdDate": current_time,
      "lastUpdatedDate": current_time,
      "hasEmbedding": False,
      "id": str(uuid.uuid4()),
      "partitionKey": "anpi_knowledge",
      "type": "knowledge",
    }
  ]
    
    return json.dumps(knowledge_entries, indent=2)

def get_apim_policy_xml(allowed_origins):
    """
    Generate XML for API Management policy
    
    Args:
        allowed_origins (str): JSON string containing allowed origins for CORS
        
    Returns:
        str: XML string with API policy
    """
    try:
        # Try to parse the JSON string to get individual origins
        import json
        origins = json.loads(allowed_origins)
        origin_tags = '\n        '.join([f'<origin>{origin}</origin>' for origin in origins])
    except:
        # If parsing fails, use default origins
        origin_tags = '<origin>https://*.fjpservice.net</origin>\n        <origin>https://localhost:4200</origin>'
    
    policy_xml = f"""<policies>
  <inbound>
    <base />
    <set-backend-service backend-id="anpi-app-service" />
    <cors>
      <allowed-origins>
        {origin_tags}
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
</policies>"""
    
    return policy_xml

def get_xml_download_link(xml_content, filename):
    """
    Create a downloadable link for XML content
    
    Args:
        xml_content (str): XML content to download
        filename (str): Name of the file to download
        
    Returns:
        str: HTML link for downloading the content
    """
    b64 = base64.b64encode(xml_content.encode()).decode()
    href = f'<a href="data:application/xml;base64,{b64}" download="{filename}" class="download-button">📄 Download {filename}</a>'
    return href

def generate_azure_pipeline_yaml(service_conn_name):
    """
    Generate Azure Pipelines YAML for CI/CD
    
    Args:
        service_conn_name (str): Base name for service connections
        
    Returns:
        str: YAML content for azure-pipelines.yml
    """
    yaml_content = f"""# Azure DevOps CI/CD Pipeline for ANPI Teams Bot
# Generated by Azure ANPI Bot Infrastructure Generator

trigger:
  branches:
    include:
      - main
      - develop
      - feature/*
      - release/*

variables:
  # Build Variables
  solution: '**/*.sln'
  buildPlatform: 'Any CPU'
  buildConfiguration: 'Release'
  dotNetVersion: '6.0.x'
  
  # Environment Variables
  ${{if eq(variables['Build.SourceBranchName'], 'main')}}:
    environment: 'prod'
    serviceConnectionName: '{service_conn_name}-Prod'
    resourceGroupName: 'itz-prod-jpe-001'
    appServiceName: 'app-itz-anpi-prod-001'
  ${{elseif eq(variables['Build.SourceBranchName'], 'develop')}}:
    environment: 'dev'
    serviceConnectionName: '{service_conn_name}-Dev'
    resourceGroupName: 'itz-dev-jpe-001'
    appServiceName: 'app-itz-anpi-dev-001'
  ${{else}}:
    environment: 'test'
    serviceConnectionName: '{service_conn_name}-Test'
    resourceGroupName: 'itz-test-jpe-001'
    appServiceName: 'app-itz-anpi-test-001'

stages:
- stage: Build
  displayName: 'Build Stage'
  jobs:
  - job: Build
    displayName: 'Build Job'
    pool:
      vmImage: 'windows-latest'
    
    steps:
    - task: UseDotNet@2
      displayName: 'Install .NET Core SDK'
      inputs:
        version: $(dotNetVersion)
        performMultiLevelLookup: true
    
    - task: NuGetToolInstaller@1
      displayName: 'Install NuGet Tools'
    
    - task: NuGetCommand@2
      displayName: 'Restore NuGet Packages'
      inputs:
        restoreSolution: '$(solution)'
    
    - task: DotNetCoreCLI@2
      displayName: 'Build Solution'
      inputs:
        command: 'build'
        projects: '$(solution)'
        arguments: '--configuration $(buildConfiguration)'
    
    - task: DotNetCoreCLI@2
      displayName: 'Run Unit Tests'
      inputs:
        command: 'test'
        projects: '**/*Tests/*.csproj'
        arguments: '--configuration $(buildConfiguration) --collect "Code Coverage"'
    
    - task: DotNetCoreCLI@2
      displayName: 'Publish Web App'
      inputs:
        command: 'publish'
        publishWebProjects: true
        arguments: '--configuration $(buildConfiguration) --output $(Build.ArtifactStagingDirectory)'
        zipAfterPublish: true
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Artifacts'
      inputs:
        pathToPublish: '$(Build.ArtifactStagingDirectory)'
        artifactName: 'drop'

- stage: Deploy
  displayName: 'Deploy Stage'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: Deploy
    displayName: 'Deploy to $(environment)'
    environment: $(environment)
    pool:
      vmImage: 'windows-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureRmWebAppDeployment@4
            displayName: 'Deploy to App Service'
            inputs:
              ConnectionType: 'AzureRM'
              azureSubscription: '$(serviceConnectionName)'
              appType: 'webApp'
              WebAppName: '$(appServiceName)'
              packageForLinux: '$(Pipeline.Workspace)/drop/*.zip'
              DeploymentType: 'zipDeploy'
              AppSettings: '-WEBSITE_RUN_FROM_PACKAGE 1'
          
          - task: AzureAppServiceManage@0
            displayName: 'Restart App Service'
            inputs:
              azureSubscription: '$(serviceConnectionName)'
              Action: 'Restart Azure App Service'
              WebAppName: '$(appServiceName)'
"""
    
    return yaml_content

def get_teams_app_manifest_download_link(app_name, bot_id, package_name, env):
    """
    Create a downloadable link for Teams app manifest ZIP file
    
    Args:
        app_name (str): Name of the Teams app
        bot_id (str): Bot ID (same as MS App ID)
        package_name (str): Package name for the app
        env (str): Environment (dev, test, etc.) - used for naming
        
    Returns:
        str: HTML link for downloading the ZIP file
    """
    # Set the short and full names based on environment
    if env.lower() == 'prod':
        short_name = "Anpi Bot"
        full_name = "AnpiBot - Safety Confirmation System"
    else:
        short_name = f"Anpi {env.capitalize()}"
        full_name = f"AnpiBot - Safety Confirmation System ({env.capitalize()})"
    
    # Create the manifest JSON content
    manifest_json = {
        "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.11/MicrosoftTeams.schema.json",
        "manifestVersion": "1.11",
        "version": "1.0.0",
        "id": bot_id,
        "packageName": package_name,
        "developer": {
            "name": "FJP FST",
            "mpnId": "",
            "websiteUrl": "https://fsoft.com.vn/2119eeb1-7817-479b-b9e7-85f668299259",
            "privacyUrl": "https://developer.microsoft.com/privacy",
            "termsOfUseUrl": "https://learn.microsoft.com/en-us/legal/marketplace/certification-policies#114043-bots"
        },
        "icons": {
            "color": "color.png",
            "outline": "outline.png"
        },
        "name": {
            "short": short_name,
            "full": full_name
        },
        "description": {
            "short": "Safety confirmation bot for employees during disasters",
            "full": "AnpiBot helps to confirm the safety status of employees during a disaster to facilitate necessary support measures."
        },
        "accentColor": "#FFFFFF",
        "bots": [
            {
                "botId": bot_id,
                "scopes": [
                    "personal",
                    "team",
                    "groupchat"
                ],
                "supportsFiles": False,
                "isNotificationOnly": False
            }
        ],
        "permissions": [
            "identity",
            "messageTeamMembers"
        ],
        "validDomains": [
            "*.azurewebsites.net",
            "token.botframework.com"
        ]
    }
    
    # Convert manifest to JSON string
    manifest_content = json.dumps(manifest_json, indent=4)
    
    # Create a ZIP file in memory
    memory_file = io.BytesIO()
    
    # Get the current directory to locate image files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Add manifest.json
        zf.writestr('manifest.json', manifest_content)
        
        # Add image files from the source
        try:
            # Path to image files
            color_path = os.path.join(current_dir, 'assets', 'color.png')
            outline_path = os.path.join(current_dir, 'assets', 'outline.png')
            
            # Check if files exist
            if os.path.exists(color_path) and os.path.exists(outline_path):
                # Add actual image files
                zf.write(color_path, 'color.png')
                zf.write(outline_path, 'outline.png')
            else:
                # Create placeholder images if files don't exist
                # Create a simple color image (96x96)
                color_img = Image.new('RGB', (96, 96), color = '#0078D4')
                color_img_bytes = io.BytesIO()
                color_img.save(color_img_bytes, format='PNG')
                zf.writestr('color.png', color_img_bytes.getvalue())
                
                # Create a simple outline image (32x32)
                outline_img = Image.new('RGB', (32, 32), color = '#FFFFFF')
                outline_img_bytes = io.BytesIO()
                outline_img.save(outline_img_bytes, format='PNG')
                zf.writestr('outline.png', outline_img_bytes.getvalue())
        except Exception as e:
            # If there's any error with the images, create placeholder images
            # Create a simple color image (96x96)
            color_img = Image.new('RGB', (96, 96), color = '#0078D4')
            color_img_bytes = io.BytesIO()
            color_img.save(color_img_bytes, format='PNG')
            zf.writestr('color.png', color_img_bytes.getvalue())
            
            # Create a simple outline image (32x32)
            outline_img = Image.new('RGB', (32, 32), color = '#FFFFFF')
            outline_img_bytes = io.BytesIO()
            outline_img.save(outline_img_bytes, format='PNG')
            zf.writestr('outline.png', outline_img_bytes.getvalue())
    
    # Reset file pointer to the beginning
    memory_file.seek(0)
    
    # Create base64 encoded string
    b64 = base64.b64encode(memory_file.getvalue()).decode()
    
    # Create download link
    file_name = f"anpi_teams_app_{env.lower()}.zip"
    href = f'<a href="data:application/zip;base64,{b64}" download="{file_name}" class="download-button">📥 Download Teams App Package</a>'
    
    return href