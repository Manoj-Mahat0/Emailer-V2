# How the Configuration System Works

## Architecture

```
Application Startup
    ↓
config.py imports configuration
    ↓
Does st.secrets exist? (Streamlit Cloud)
    ├─ YES → Use st.secrets values
    ├─ NO → Check environment variables (.env file)
    └─ NOT FOUND → Return default or raise error
    ↓
Application uses config values
```

## Code Example

### Old Way (Only Local)
```python
from config import Config

class Config:
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')  # Always from .env or environment
```

### New Way (Local + Cloud)
```python
from config import config

class Config:
    @property
    def GMAIL_EMAIL(self):
        # Check Streamlit secrets first
        if 'GMAIL_EMAIL' in st.secrets:
            return st.secrets['GMAIL_EMAIL']
        # Fall back to environment variables
        return os.getenv('GMAIL_EMAIL')
```

## Configuration Resolution

When you use `config.GMAIL_EMAIL`:

### On Streamlit Cloud
```
1. Check st.secrets['GMAIL_EMAIL'] → Found ✓
2. Return value from secrets
```

### Locally
```
1. Check st.secrets['GMAIL_EMAIL'] → Not found
2. Check os.getenv('GMAIL_EMAIL') → Found from .env ✓
3. Return value from environment
```

## Usage in Your Code

All files use the same pattern:

```python
# Import the config instance (not the class)
from config import config

# Use it just like before
class EmailService:
    def __init__(self):
        self.email = config.GMAIL_EMAIL  # Works everywhere
        self.password = config.GMAIL_APP_PASSWORD
```

## Adding New Configuration Values

### Step 1: Add to config.py
```python
@property
def NEW_SETTING(self):
    return self._get_config_value('NEW_SETTING', 'default_value')
```

### Step 2: Use in your code
```python
from config import config

value = config.NEW_SETTING  # Works locally and on Streamlit Cloud
```

### Step 3: Set value
- **Locally**: Add to `.env` file
  ```
  NEW_SETTING=value
  ```
- **Streamlit Cloud**: Add to App settings → Secrets
  ```toml
  NEW_SETTING = "value"
  ```

## How Streamlit Detects Secrets

Streamlit automatically:
1. Looks for `.streamlit/secrets.toml` in your project (local development)
2. Exposes it via `st.secrets` dictionary
3. On Streamlit Cloud, loads secrets from dashboard instead

## Why This Approach?

✓ **Single code base** - Works locally and on cloud  
✓ **Secure** - No hardcoded credentials  
✓ **Flexible** - Easy to add/change configuration  
✓ **No code changes** - Just update secrets when credentials change  
✓ **Backward compatible** - Still works with `.env` files  

## Order of Precedence

When looking for a configuration value:

1. **Streamlit Secrets** (highest priority)
   - Used on Streamlit Cloud
   - Used locally if `.streamlit/secrets.toml` exists

2. **Environment Variables** (fallback)
   - Read from `.env` file (python-dotenv)
   - Read from OS environment

3. **Default Value** (lowest priority)
   - Hardcoded in code (if provided)

Example: `config._get_config_value('RATE_LIMIT', '30')`
- Check `st.secrets['RATE_LIMIT']`
- Check `os.getenv('RATE_LIMIT')`
- Use `'30'` as default

## Testing Configuration Locally

### Option 1: Using .env (Current)
Keep your existing `.env` file - it works!

### Option 2: Using Streamlit Secrets
Create `.streamlit/secrets.toml`:
```toml
GMAIL_EMAIL = "test@gmail.com"
GMAIL_APP_PASSWORD = "password"
# ... etc
```

Both options work identically locally.

## Production Best Practices

1. **Never commit secrets to Git**
   - `.env` is in `.gitignore` ✓
   - `.streamlit/` is in `.gitignore` ✓

2. **Rotate credentials regularly**
   - Update in Streamlit Cloud dashboard
   - Update `.env` locally
   - No code changes needed

3. **Use strong app passwords**
   - Gmail: Generate app-specific password
   - MongoDB: Use strong password with special chars

4. **Monitor configuration errors**
   - Logs show which configuration values are missing
   - Easy to debug configuration issues

---

The configuration system is designed to be **transparent** - you don't need to think about it. Just use `config.VALUE_NAME` and it works everywhere!
