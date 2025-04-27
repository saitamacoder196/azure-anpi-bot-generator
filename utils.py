"""
Utility functions for the Azure ANPI Bot Infrastructure Generator.
"""
import base64
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