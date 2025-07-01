# TailorTalk Local Setup Requirements

Complete requirements to run TailorTalk on your local computer.

## Programming Languages Required

### Python 3.8+
- **Required**: Python 3.8 or higher
- **Download**: https://python.org/downloads
- **Check version**: `python --version` or `python3 --version`

## Package Manager

### pip (Python Package Installer)
- Usually comes with Python installation
- **Check**: `pip --version`
- **Alternative**: Use `pip3` if `pip` doesn't work

## Required Python Libraries

Install these using pip:

```bash
pip install streamlit
pip install anthropic
pip install openai
pip install langchain-anthropic
pip install langchain-openai
pip install langchain-core
pip install langgraph
pip install langgraph-checkpoint
pip install google-api-python-client
pip install google-auth
pip install google-auth-httplib2
pip install google-auth-oauthlib
pip install python-dateutil
pip install pytz
```

### Alternative: Install from requirements file

Create a `requirements.txt` file with this content:

```
streamlit>=1.28.0
anthropic>=0.7.0
openai>=1.3.0
langchain-anthropic>=0.1.0
langchain-openai>=0.1.0
langchain-core>=0.1.0
langgraph>=0.1.0
langgraph-checkpoint>=1.0.0
google-api-python-client>=2.100.0
google-auth>=2.22.0
google-auth-httplib2>=0.1.1
google-auth-oauthlib>=1.0.0
python-dateutil>=2.8.2
pytz>=2023.3
```

Then install all at once:
```bash
pip install -r requirements.txt
```

## Environment Variables Required

You need to set these environment variables with your API keys:

### Option 1: Environment Variables
```bash
# Windows Command Prompt
set ANTHROPIC_API_KEY=your_anthropic_key_here
set OPENAI_API_KEY=your_openai_key_here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_anthropic_key_here"
$env:OPENAI_API_KEY="your_openai_key_here"

# macOS/Linux
export ANTHROPIC_API_KEY="your_anthropic_key_here"
export OPENAI_API_KEY="your_openai_key_here"
```

### Option 2: .env file (Recommended)
Create a `.env` file in your project folder:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

## Files You Need to Copy

Copy these files from your Replit project to your local computer:

### Core Application Files
- `app.py` - Main Streamlit application
- `agent_simple.py` - AI agent with full functionality
- `agent_demo.py` - Demo mode fallback
- `calendar_tools.py` - Google Calendar integration
- `utils.py` - Utility functions

### Configuration Files
- `credentials.json` - Your Google service account credentials
- `.streamlit/config.toml` - Streamlit configuration

### Setup and Documentation
- `setup_google_calendar.py` - Setup testing script
- `SETUP_INSTRUCTIONS.md` - Google Calendar setup guide
- `LOCAL_SETUP_REQUIREMENTS.md` - This file

## Google Calendar Setup

### Prerequisites
- Google account
- Google Cloud Console project
- Service account with Calendar API access
- Calendar shared with service account

### Your credentials.json file
Make sure your `credentials.json` contains your actual Google service account data (not the placeholder).

## Running the Application

### 1. Open Terminal/Command Prompt
Navigate to your project folder:
```bash
cd path/to/your/tailortalk/folder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test Google Calendar Connection
```bash
python setup_google_calendar.py
```

### 4. Start the Application
```bash
streamlit run app.py --server.port 5000
```

### 5. Access the Application
Open your browser to: http://localhost:5000

## System Requirements

### Minimum Hardware
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **CPU**: Any modern processor
- **Internet**: Required for AI API calls and Google Calendar

### Operating Systems Supported
- **Windows**: 10/11
- **macOS**: 10.14+
- **Linux**: Ubuntu 18.04+, CentOS 7+, or equivalent

## API Keys Required

### Anthropic API Key
- **Get it**: https://console.anthropic.com/
- **Usage**: Primary AI conversation engine
- **Cost**: Pay-per-use (Claude models)

### OpenAI API Key
- **Get it**: https://platform.openai.com/api-keys
- **Usage**: Fallback AI engine
- **Cost**: Pay-per-use (GPT models)

### Google Calendar API
- **Setup**: Through Google Cloud Console
- **Cost**: Free (with usage limits)
- **Required**: Service account JSON credentials

## Port Configuration

### Default Port
- Application runs on port 5000
- Access via: http://localhost:5000

### Custom Port
To use a different port:
```bash
streamlit run app.py --server.port 8080
```

## Firewall Settings

### Windows Firewall
- Allow Python/Streamlit through firewall
- Port 5000 should be accessible

### macOS Firewall
- Allow incoming connections for Python
- No additional configuration usually needed

### Linux Firewall
```bash
# Ubuntu/Debian
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

## Troubleshooting

### Common Issues

#### "Module not found" error
```bash
pip install [missing_module_name]
```

#### "Permission denied" on calendar
- Check Google Calendar sharing settings
- Verify service account email is correct
- Run `python setup_google_calendar.py` to test

#### "API key not found" error
- Check environment variables are set
- Verify .env file is in correct location
- Restart terminal after setting variables

#### Port already in use
```bash
# Kill process on port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID [PID_NUMBER] /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

## Performance Optimization

### For Better Performance
- Use Python virtual environment
- Close unnecessary applications
- Ensure stable internet connection
- Consider upgrading to paid API tiers for faster responses

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv tailortalk_env

# Activate it
# Windows
tailortalk_env\Scripts\activate
# macOS/Linux
source tailortalk_env/bin/activate

# Install packages
pip install -r requirements.txt

# Run application
streamlit run app.py --server.port 5000
```

## Security Considerations

### Protect Your API Keys
- Never commit .env files to version control
- Keep credentials.json secure
- Use environment variables in production
- Regularly rotate API keys

### Network Security
- Run on localhost for development
- Use HTTPS in production
- Consider VPN for remote access
- Keep dependencies updated

## Production Deployment

For production deployment, consider:
- **Cloud platforms**: AWS, Google Cloud, Azure
- **Containerization**: Docker
- **Process management**: PM2, systemd
- **Reverse proxy**: Nginx, Apache
- **SSL certificates**: Let's Encrypt
- **Environment management**: Docker Compose, Kubernetes

This covers everything you need to run TailorTalk locally on your computer!