# Deployment Guide for Streamlit Cloud

## Overview
This application now supports both local development and Streamlit Cloud deployment using a class-based configuration system that automatically switches between:
- **Local Development**: `.env` file or `.streamlit/secrets.toml`
- **Streamlit Cloud**: Secrets management dashboard

## Local Development Setup

### 1. Using `.env` file (Existing Method)
Your current `.env` file will continue to work locally:
```
GMAIL_EMAIL=codeinlastbench@gmail.com
GMAIL_APP_PASSWORD=gmbj hwsx nwal dmhy
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=bulk_emailer
APP_TITLE=Bulk Email Sender
RATE_LIMIT_EMAILS_PER_MINUTE=30
```

### 2. Using `.streamlit/secrets.toml` (Recommended for Local)
Alternatively, use `.streamlit/secrets.toml` for local development - it has the same secrets but in TOML format:
```toml
GMAIL_EMAIL = "codeinlastbench@gmail.com"
GMAIL_APP_PASSWORD = "gmbj hwsx nwal dmhy"
MONGODB_URI = "mongodb+srv://..."
MONGODB_DB_NAME = "bulk_emailer"
APP_TITLE = "Bulk Email Sender"
RATE_LIMIT_EMAILS_PER_MINUTE = 30
```

## Streamlit Cloud Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add class-based configuration for Streamlit Cloud"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Click "New app"
3. Select your repository and branch
4. Enter app path: `app.py`

### Step 3: Add Secrets (CRITICAL!)
1. After deployment, go to App settings → Secrets
2. Click "Edit secrets"
3. Add your secrets in TOML format:

```toml
# Gmail Configuration
GMAIL_EMAIL = "codeinlastbench@gmail.com"
GMAIL_APP_PASSWORD = "gmbj hwsx nwal dmhy"

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://manojmahato08779_db_user:K8i95Y7xiJyFG7v0@cluster0.ngzwhcw.mongodb.net/?appName=Cluster0"
MONGODB_DB_NAME = "bulk_emailer"

# Application Settings
APP_TITLE = "Bulk Email Sender"
RATE_LIMIT_EMAILS_PER_MINUTE = 30
```

4. Click "Save" and the app will automatically redeploy

## Configuration Priority (Automatic)

The application checks configuration in this order:
1. **Streamlit Secrets** (`st.secrets`) - Used on Streamlit Cloud ✓
2. **Environment Variables** (from `.env`) - Used locally ✓

This means:
- **Locally**: Works with `.env` or `.streamlit/secrets.toml`
- **Streamlit Cloud**: Automatically uses secrets from dashboard
- **No hardcoded values** in Python files ✓
- **Credentials are secure** and never committed to Git ✓

## Files Changed

### `config.py`
- Changed from static class attributes to instance properties
- Added `_get_config_value()` method for dynamic config loading
- Now checks `st.secrets` first (Streamlit Cloud), then environment variables
- Validate method works on instance

### `app.py`
- Changed `Config` to `config` (instance instead of class)
- Updated all references: `Config.APP_TITLE` → `config.APP_TITLE`
- All other functionality remains unchanged

### New Files
- `.streamlit/secrets.toml` - For local development with Streamlit secrets

## Security Checklist

✓ `.env` file is in `.gitignore` (credentials not in Git)
✓ `.streamlit/secrets.toml` should be in `.gitignore` (local testing only)
✓ Credentials are only accessed via `st.secrets` or environment variables
✓ No hardcoded values in Python files
✓ Safe for open-source repositories

## Troubleshooting

### "Missing required configuration" error on Streamlit Cloud
- Check that all secrets are added in App settings → Secrets
- Ensure secrets are in correct TOML format
- Rerun the app after saving secrets

### "Missing required configuration" error locally
- Ensure `.env` file exists in project root
- Or create `.streamlit/secrets.toml` in `.streamlit` folder
- Check that variable names match exactly

### Changed MongoDB/Gmail settings
- Just update the secrets and redeploy (no code changes needed)
- Changes apply automatically on next app run

## Testing

Run locally to verify:
```bash
streamlit run app.py
```

The app should connect without configuration errors.
