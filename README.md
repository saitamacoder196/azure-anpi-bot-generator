# Azure ANPI Bot Infrastructure Generator

This Streamlit application helps you generate Azure CLI commands for deploying the ANPI Bot infrastructure. The tool generates scripts for creating and configuring all the necessary Azure resources including:

- Resource groups
- Networking (VNets, Subnets, Application Gateway)
- App Services
- Data & AI Services (Cosmos DB, OpenAI, Azure Search)
- API Management
- Web Apps and Bot Services
- Teams Integration

## Features

- Generate complete deployment scripts for different environments (dev, test, preprd, prod)
- Customizable resource names and configurations
- Interactive UI with input validation
- Downloadable scripts in bash and markdown formats
- Deployment checklist to track your progress

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/azure-anpi-bot-generator.git
cd azure-anpi-bot-generator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
project/
├── app.py            # Main entry point
├── utils.py          # Utility functions
├── generators.py     # Script generation functions
├── ui.py             # UI components and rendering
├── state.py          # State management
└── requirements.txt  # Project dependencies
```

## Usage

1. Fill in the required parameters in each tab
2. Click "Generate CLI Commands"
3. Review the generated scripts
4. Download as bash script or markdown
5. Execute the commands on your Azure environment

## Requirements

- Python 3.7+
- Streamlit
- Azure CLI (for executing the generated commands)

## License

MIT