# Installation Guide

## System Requirements

- Python 3.8 or higher
- macOS / Linux / Windows
- Internet connection

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/zstmfhy/zlibrary-to-notebooklm.git
cd zlibrary-to-notebooklm
```

### 2. Install the Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install the Playwright browser

```bash
playwright install chromium
```

### 4. Make sure the NotebookLM CLI is installed

```bash
# Check whether the notebooklm command is available
notebooklm --version

# If it is not installed, install the NotebookLM CLI first
npm install -g @google-notebooklm/cli
```

## Verify the Installation

```bash
# Test the login script (does not actually log in)
python3 scripts/login.py --help

# Test the upload script (does not actually upload)
python3 scripts/upload.py --help
```

## Troubleshooting

### Playwright installation fails

```bash
# Download the browser manually
playwright install --with-deps chromium
```

### Python version issues

```bash
# Install Python 3.8+ with pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

### Permission issues

```bash
# macOS/Linux: add execute permission
chmod +x scripts/*.py
```

## Next Steps

Once installation is complete, see [Quick Start](README.md#-use-as-claude-skill-recommended)
