# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Activate Conda Environment
```bash
# For Linux/macOS
conda activate azure-deployment-generator
```

```cmd
:: For Windows
conda activate azure-deployment-generator
```

- Run application: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt`
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
EOF < /dev/null
