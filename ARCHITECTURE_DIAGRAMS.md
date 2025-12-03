# Configuration System Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Application                              │
│                      (app.py, etc.)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ imports
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   config.py (Configuration Manager)              │
│                                                                   │
│  from config import config                                       │
│  value = config.GMAIL_EMAIL    ← Works everywhere!              │
└────────────────┬──────────────────────────┬──────────────────────┘
                 │                          │
         ┌───────┴────────┐         ┌──────┴─────────┐
         │ LOCAL          │         │ STREAMLIT CLOUD│
         │ DEVELOPMENT    │         │ DEPLOYMENT     │
         ↓                ↓         ↓                ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  st.secrets?     │  │  st.secrets?     │  │  st.secrets?     │
│  (None)          │  │  (secrets.toml)  │  │  (Dashboard)     │
│      ↓           │  │      ↓           │  │      ↓           │
│  Check .env file │  │  Use secrets     │  │  Use secrets     │
│      ✓ FOUND     │  │      ✓ FOUND     │  │      ✓ FOUND     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         ✓                     ✓                     ✓
   Works Locally         Works Locally        Works on Cloud
```

## Configuration Resolution Flow

```
config.GMAIL_EMAIL requested
           │
           ↓
Check st.secrets dict
           │
    ┌──────┴──────┐
    │             │
   YES            NO
    │             │
    ↓             ↓
Return      Check os.getenv('.env')
value           │
                │
            ┌───┴────┐
            │        │
           YES      NO
            │        │
            ↓        ↓
        Return   Return
        value    default
```

## Deployment Flow

```
┌─────────────────┐
│  Local Machine  │
│                 │
│  $ git push     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  GitHub Repo    │
│                 │
│  Stores code    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────┐
│ Streamlit Cloud                 │
│                                 │
│ - Clones repo                   │
│ - Runs app.py                   │
│ - Needs configuration!          │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ App Settings → Secrets Dashboard│
│                                 │
│ Add your secrets:               │
│ GMAIL_EMAIL = "..."             │
│ GMAIL_APP_PASSWORD = "..."      │
│ MONGODB_URI = "..."             │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ App Redeploys Automatically     │
│                                 │
│ st.secrets populated from       │
│ Dashboard                       │
└────────┬────────────────────────┘
         │
         ↓
┌─────────────────────────────────┐
│ ✓ Application Running           │
│                                 │
│ config reads from st.secrets    │
│ Everything works!               │
└─────────────────────────────────┘
```

## File Structure After Migration

```
Emailer V2/
├── .env                          ← Your credentials (local)
├── .gitignore                    ← Already ignores .env and .streamlit/
├── app.py                        ← Updated: uses config instance
├── config.py                     ← Updated: dynamic configuration
├── requirements.txt
├── README.md
│
├── .streamlit/
│   ├── secrets.toml              ← NEW: Local Streamlit secrets
│   └── config.toml               ← (Optional) Streamlit settings
│
├── database/
│   ├── __init__.py
│   └── mongodb.py                ← Updated: uses config instance
│
├── services/
│   ├── __init__.py
│   ├── email_service.py          ← Updated: uses config instance
│   └── template_service.py
│
├── pages/
│   ├── __init__.py
│   ├── history.py
│   ├── new_campaign.py
│   └── templates.py
│
├── utils/
│   ├── __init__.py
│   └── csv_parser.py
│
└── Documentation/ (NEW)
    ├── README_CONFIGURATION.md       ← Overview
    ├── DEPLOYMENT_QUICK_START.md    ← 3-step guide
    ├── STREAMLIT_DEPLOYMENT.md      ← Detailed guide
    ├── CONFIGURATION_MIGRATION.md   ← What changed
    └── CONFIGURATION_ARCHITECTURE.md ← Technical details
```

## Configuration Priority Hierarchy

```
                    Configuration Request
                            │
                    ┌───────┴────────┐
                    │                │
            ENVIRONMENT          LOCAL APP
                    │                │
         ┌──────────┴──────────┐     │
         │                     │     │
      CLOUD              DEVELOPMENT │
         │                     │     │
         ↓                     ↓     ↓
    ┌─────────────┐      ┌──────────────┐
    │ st.secrets  │      │ st.secrets?  │
    │ (Dashboard) │      │              │
    └──────┬──────┘      └──┬──┬───────┘
           │                │  │
        Value            Yes  No
           │                │  │
           ↓                ↓  ↓
        ✓ DONE          Use    Check
                      secrets  .env
                        │      │
                     Value  Value?
                        │      │
                        ↓      ↓
                     ✓ DONE  ✓ DONE
                             OR
                           Default
```

## Security Architecture

```
┌──────────────────────────────────────────────────────┐
│              Git Repository (GitHub)                 │
│                                                      │
│  ✓ Code files (can be public)                      │
│  ✓ Configuration logic                             │
│  ✗ No .env file                                    │
│  ✗ No .streamlit/ directory                        │
└──────────────────────────────────────────────────────┘
              (Excluded by .gitignore)

┌──────────────────────────────────────────────────────┐
│            Local Development Machine                 │
│                                                      │
│  .env (PRIVATE)                                     │
│  .streamlit/secrets.toml (PRIVATE)                  │
│  Only you see these!                                │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│          Streamlit Cloud Dashboard                   │
│                                                      │
│  Secrets Management (ENCRYPTED)                     │
│  ├── GMAIL_EMAIL                                    │
│  ├── GMAIL_APP_PASSWORD                             │
│  ├── MONGODB_URI                                    │
│  └── ... (other secrets)                           │
│                                                      │
│  Only accessible via web interface                 │
│  Never shown in logs or code                       │
└──────────────────────────────────────────────────────┘
```

## How It All Fits Together

```
Developer
    │
    ├─ Local: streamlit run app.py
    │         ↓
    │    Reads from .env
    │    Works fine!
    │
    ├─ Push to GitHub
    │
    ├─ Deploy on Streamlit Cloud
    │         ↓
    │    Add secrets to dashboard
    │         ↓
    │    Streamlit loads st.secrets
    │    from dashboard
    │         ↓
    │    config.py uses st.secrets
    │    App works fine!
    │
    └─ Change credentials?
         Just update secrets
         No code changes needed!
```

---

**Key Insight:** The same Python code works in both environments because it intelligently checks both configuration sources and uses what's available!
