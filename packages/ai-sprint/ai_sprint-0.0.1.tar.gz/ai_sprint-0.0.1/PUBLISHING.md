# Publishing ai-sprint to PyPI

## Prerequisites
- PyPI account (create at  )
- API token from PyPI (Account Settings > API tokens)

## Steps

### 1. Update Package Name (if needed)
If HITL provides a different name, update `pyproject.toml`:
```toml
name = "your-package-name"
```

### 2. Update Version (if needed)
Update version in `pyproject.toml`:
```toml
version = "0.0.1"
```

### 3. Build the Package
```bash
cd ai-sprint
uv build --clear
```

### 4. Install Twine
```bash
pip install twine
```

### 5. Upload to PyPI
```bash
twine upload dist/*
```

When prompted, enter your PyPI username and password (or use API token as password).

For automated uploads, set environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
twine upload dist/*
```

## Verification
After upload, verify at https://pypi.org/project/your-package-name/

Users can install with:
```bash
pip install your-package-name
```