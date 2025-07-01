# TailorTalk - AI Appointment Scheduler

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

A conversational AI agent that handles appointment scheduling through natural language chat with Google Calendar integration.

## 🚀 Live Demo

**Deployed URL**: [Will be added after deployment]

## ✨ Features

- **Natural Language Booking**: Schedule appointments using everyday language
- **Google Calendar Integration**: Real-time calendar synchronization
- **Intelligent Conversation**: Contextual chat with memory
- **Availability Checking**: Smart conflict detection
- **Multi-Platform Deployment**: Ready for Railway, Render, Fly.io

## 🏗️ Architecture

- **Frontend**: Streamlit web interface with chat UI
- **Backend**: Python with LangGraph for conversation flow
- **AI Models**: Anthropic Claude 4.0 + OpenAI GPT-4o fallback
- **Calendar**: Google Calendar API with service account authentication
- **Deployment**: Docker containerized for cloud platforms

## 🔧 Quick Deploy

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click "Deploy on Railway"
2. Set environment variables:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
3. Upload your `credentials.json` file
4. Deploy!

### Render
1. Fork this repository
2. Connect to Render
3. Set environment variables
4. Deploy from `render.yaml`

### Fly.io
```bash
fly launch
fly secrets set ANTHROPIC_API_KEY=your_key
fly secrets set OPENAI_API_KEY=your_key
fly deploy
```

## 📋 Local Setup

### Prerequisites
- Python 3.8+
- API keys (Anthropic, OpenAI)
- Google Calendar service account

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/tailortalk.git
cd tailortalk

# Install dependencies
pip install -r local_requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"

# Run application
streamlit run app.py --server.port 5000
```

## 🔑 API Keys Setup

### Anthropic API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create account and get API key
3. Set as `ANTHROPIC_API_KEY` environment variable

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create account and get API key
3. Set as `OPENAI_API_KEY` environment variable

### Google Calendar Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Calendar API
3. Create service account and download JSON
4. Share your calendar with service account email
5. Replace `credentials.json` with your service account data

Detailed setup: [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## 💬 Usage Examples

```
User: "Book a meeting tomorrow at 2 PM"
TailorTalk: "I'll schedule a meeting for tomorrow at 2:00 PM. What should I call this meeting?"

User: "What's my availability Friday?"
TailorTalk: "You're available Friday from 9 AM to 12 PM and 2 PM to 5 PM."

User: "Cancel my 3 PM appointment today"
TailorTalk: "I found your 3 PM appointment and cancelled it successfully."
```

## 🛠️ Development

### Project Structure
```
tailortalk/
├── app.py                 # Streamlit frontend
├── agent_simple.py        # Main AI agent
├── calendar_tools.py      # Google Calendar integration
├── utils.py              # Utility functions
├── credentials.json      # Google service account
├── Dockerfile           # Container configuration
├── railway.toml         # Railway deployment
├── render.yaml          # Render deployment
└── fly.toml            # Fly.io deployment
```

### Key Components
- **TailorTalkAgent**: Conversational AI with LangGraph
- **CalendarManager**: Google Calendar API operations
- **Streamlit UI**: Professional chat interface
- **Natural Language Processing**: Date/time extraction

## 📊 System Requirements

### Minimum
- RAM: 512MB
- CPU: 1 core
- Storage: 1GB

### Recommended
- RAM: 1GB
- CPU: 2 cores
- Storage: 2GB

## 🔒 Security

- Environment variables for API keys
- Service account authentication
- No user data storage
- Secure calendar access controls

## 📈 Performance

- Intelligent API fallbacks
- Memory-efficient conversation handling
- Optimized calendar queries
- Graceful error handling

## 🧪 Testing

```bash
# Test Google Calendar connection
python setup_google_calendar.py

# Test AI agent functionality
python -c "from agent_simple import TailorTalkAgent; agent = TailorTalkAgent(); print(agent.process_message('Hello'))"
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- Review troubleshooting guide

## 🏆 Deployment Status

- ✅ **Code Complete**: Full functionality implemented
- ✅ **Google Calendar**: Integration tested and working
- ✅ **AI Agent**: Conversational booking system active
- ✅ **Docker Ready**: Containerized for deployment
- ⏳ **Live URL**: Deployment in progress

---

Built with ❤️ using Python, Streamlit, LangGraph, and Google Calendar API