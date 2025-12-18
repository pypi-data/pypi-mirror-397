# API Key Setup Guide

## For Testing (No API Key Required)

**Good news!** You can run all tests without an OpenAI API key.

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# All tests use mocked responses - no API calls!
```

The tests use `unittest.mock` to simulate API responses, so they:
- ✅ Run without API keys
- ✅ Cost nothing
- ✅ Work offline
- ✅ Are fast and reproducible

## For Running the Application (API Key Required)

To actually use the AI Scientist system, you need an OpenAI API key.

### Step 1: Get an API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-...`)

### Step 2: Configure the Key

**Option A: Using Python Code (Recommended)**
```python
import aibioagent as aba

# Set API key - automatically saves to .env file
aba.set_api_key("sk-your-key-here")
# ✅ API key set and saved to .env
```

This method:
- ✅ Automatically creates `.env` file in current directory
- ✅ Persists across sessions
- ✅ No manual file editing needed

**Option B: Manual .env File**
```bash
# Create .env file in current directory
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Option C: System Environment Variable**
```bash
# For macOS/Linux (add to ~/.bashrc or ~/.zshrc)
export OPENAI_API_KEY="sk-your-key-here"

# For Windows
setx OPENAI_API_KEY "sk-your-key-here"
```

### Step 3: Verify Setup

```python
import aibioagent as aba

# Check if API key is configured
key = aba.get_api_key()
if key:
    print(f"✅ API key configured: {key[:10]}...")
else:
    print("❌ No API key found")
```

### Step 4: Run the Application

```python
import aibioagent as aba

# For interactive web interface
aba.chat()

# Or use programmatically
response = aba.ask("What is adaptive optics in microscopy?")
print(response)
```

## Cost Considerations

OpenAI API usage is pay-per-use
For test purposes, could choose cheaper models.


**Budget tip:** Set usage limits in OpenAI dashboard

## Troubleshooting

### "OpenAI API key not found"
- Use `aba.set_api_key("sk-your-key")` to configure it programmatically
- Check `.env` file exists in current working directory (not project root)
- Verify key starts with `sk-`
- Test with: `aba.get_api_key()`

### "Invalid API key"
- Key may be revoked - create new one
- Check for extra spaces/quotes
- Verify account has billing set up

### "Rate limit exceeded"
- OpenAI has usage limits
- Wait a few minutes
- Consider upgrading your OpenAI tier

### Tests fail with "No API key"
- Tests shouldn't need API key!
- Make sure you have `pytest` and `pytest-mock` installed
- Check that tests use `@patch` decorators



Modify `core/llm_client.py` to use your preferred provider.

## Security Best Practices

⚠️ **Never:**
- Commit API keys to Git
- Share keys publicly
