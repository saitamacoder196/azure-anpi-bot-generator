# Azure Deployment Generator

A Streamlit application for generating Azure deployment scripts and configurations.

## Repository

```
https://github.com/saitamacoder196/azure-anpi-bot-generator.git
```

## Setup

### Clone Repository
```bash
git clone https://github.com/saitamacoder196/azure-anpi-bot-generator.git
cd azure-deployment-generator
```

### Activate Conda Environment
```bash
# For Linux/macOS
conda activate azure-deployment-generator
```

```cmd
:: For Windows
conda activate azure-deployment-generator
```

### Installation
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
streamlit run app.py
```

## Development

- Formatting: `black .` (if installed)
- Type checking: `mypy .` (if installed)

## Code Style Guidelines

- **Imports**: Standard library imports first, followed by third-party imports, then local imports
- **Documentation**: All functions require docstrings with Args and Returns sections
- **Formatting**: 4-space indentation, 88 character line limit
- **Types**: Type hints recommended for function parameters and return values
- **Error Handling**: Use try/except blocks with specific exceptions
- **Variable Names**: Use snake_case for variables and functions, PascalCase for classes
- **String Formatting**: Use f-strings for string interpolation
- **Comments**: Add meaningful comments for complex logic only
- **Session State**: Use Streamlit's st.session_state for persisting data between reruns
EOL < /dev/null
