"""
Utility functions for the Azure ANPI Bot Infrastructure Generator.
"""
import base64
import json
import random
import string
from datetime import datetime

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
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">Download Markdown</a>'
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

def get_yaml_download_link(api_display_name, env, app_name):
    """
    Create a downloadable link for OpenAPI YAML file
    
    Args:
        apim_name (str): API Management service name
        api_path (str): API path
        api_id (str): API ID
        api_display_name (str): Display name for the API
        env (str): Environment (dev, test, etc.)
        app_name (str): App Service name
        
    Returns:
        str: HTML link for downloading the YAML file
    """
    yaml_content = f"""openapi: 3.0.1
info:
  title: {api_display_name}
  description: API for FJP ANPI Safety Confirmation System Bot - {env.upper()}
  version: '1.0'
servers:
  - url: https://{app_name}.azurewebsites.net
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