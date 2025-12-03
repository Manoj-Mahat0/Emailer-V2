# Quick Reference: Configuration for Streamlit Cloud

## TL;DR - Deploy in 3 Steps

### Step 1: Push to GitHub
```powershell
git add .
git commit -m "Add Streamlit Cloud configuration"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io/)
- Click "New app" → Select your repo and branch
- App path: `app.py` → Deploy

### Step 3: Add Secrets (CRITICAL!)
1. After deployment, click "App settings" (⚙️)
2. Click "Secrets"
3. Paste this and replace with your values:
```toml
GMAIL_EMAIL = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
MONGODB_URI = "mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0"
MONGODB_DB_NAME = "bulk_emailer"
APP_TITLE = "Bulk Email Sender"
RATE_LIMIT_EMAILS_PER_MINUTE = 30
```
4. Click "Save" → App redeploys automatically

## What Changed?

**Before**: Only worked locally with `.env` file  
**After**: Works on both local AND Streamlit Cloud

- Code automatically detects environment
- No configuration changes needed
- Just add secrets to dashboard on Streamlit Cloud

## Testing Locally

```bash
streamlit run app.py
```

Works with your existing `.env` file (no changes needed).

## Troubleshooting

### "Missing required configuration" error on Streamlit Cloud?
- ✓ Check secrets in App settings → Secrets
- ✓ Verify all 3 required fields are present and filled
- ✓ Make sure no typos in secret names
- ✓ Click "Save" after editing secrets
- ✓ Wait for app to redeploy (about 30 seconds)

### Works locally but not on Streamlit Cloud?
- ✓ Go to App settings → Secrets
- ✓ Verify secrets are added correctly
- ✓ Check app logs for error messages

### Want to change credentials?
- Just update secrets in App settings → Secrets
- No code changes needed
- No need to redeploy (changes apply on next run)

---

**Files with configuration support:**
- `config.py` - Configuration manager
- `app.py` - Main app
- `services/email_service.py` - Email sending
- `database/mongodb.py` - Database connection

**New files for secrets:**
- `.streamlit/secrets.toml` - Local testing with Streamlit
- `.streamlit/config.toml` - (Optional) Streamlit settings
