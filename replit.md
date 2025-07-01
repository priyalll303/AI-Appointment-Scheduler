# TailorTalk - AI Appointment Scheduler

## Overview

TailorTalk is an intelligent AI-powered appointment scheduling system that combines natural language processing with Google Calendar integration. The application provides a conversational interface for users to schedule, manage, and query appointments using everyday language. Built with Streamlit for the web interface and LangGraph for AI orchestration, it leverages both Anthropic's Claude and OpenAI's GPT models for natural language understanding.

## System Architecture

The system follows a modular architecture with clear separation of concerns:

**Frontend Layer**: Streamlit-based web interface providing a chat-like user experience
**AI Agent Layer**: LangGraph-powered conversational agent with memory management
**Integration Layer**: Google Calendar API integration for appointment management
**Utility Layer**: Natural language processing utilities for date/time extraction

The architecture prioritizes flexibility by supporting multiple AI providers and maintaining conversation state across user sessions.

## Key Components

### 1. TailorTalkAgent (agent.py)
- **Purpose**: Core conversational AI agent handling user interactions
- **Technology**: LangGraph with LangChain integration
- **Features**: 
  - Multi-provider LLM support (Anthropic Claude, OpenAI GPT)
  - Memory management for conversation context
  - Specialized system prompts for appointment scheduling
- **Design Decision**: Fallback mechanism ensures service availability when one provider fails

### 2. Streamlit Web Interface (app.py)
- **Purpose**: User-facing web application with chat interface
- **Technology**: Streamlit with custom CSS styling
- **Features**:
  - Real-time chat interface
  - Session state management
  - Error handling and user feedback
- **Design Decision**: Chat-based interface chosen for natural user interaction

### 3. Calendar Integration (calendar_tools.py)
- **Purpose**: Google Calendar API operations
- **Technology**: Google Calendar API v3 with service account authentication
- **Features**:
  - Event creation, retrieval, and management
  - Timezone handling with pytz
  - Conflict detection and availability checking
- **Design Decision**: Service account authentication chosen for simplified deployment

### 4. Natural Language Processing (utils.py)
- **Purpose**: Extract structured data from natural language input
- **Technology**: Regular expressions and dateutil parsing
- **Features**:
  - Date/time extraction from text
  - Support for relative dates ("tomorrow", "next week")
  - Multiple date format recognition
- **Design Decision**: Regex-based approach for reliable pattern matching

## Data Flow

1. **User Input**: User enters natural language request via Streamlit interface
2. **Agent Processing**: TailorTalkAgent processes request using LLM
3. **Intent Recognition**: System identifies scheduling intent and extracts parameters
4. **Calendar Operations**: Calendar tools perform Google Calendar API operations
5. **Response Generation**: Agent formulates natural language response
6. **User Feedback**: Streamlit interface displays response to user

The system maintains conversation context through LangGraph's memory management, allowing for multi-turn conversations about appointment scheduling.

## External Dependencies

### AI Providers
- **Anthropic Claude**: Primary LLM provider (claude-sonnet-4-20250514)
- **OpenAI GPT**: Fallback LLM provider (gpt-4o)

### Google Services
- **Google Calendar API**: Core calendar functionality
- **Service Account Authentication**: Simplified credential management

### Python Libraries
- **Streamlit**: Web interface framework
- **LangGraph**: AI agent orchestration
- **LangChain**: LLM integration framework
- **pytz**: Timezone handling
- **dateutil**: Date parsing utilities

## Deployment Strategy

The application is designed for cloud deployment with the following considerations:

**Authentication**: Service account credentials stored in credentials.json file
**Environment Variables**: API keys managed through environment variables
**Scalability**: Stateless design with external state management
**Error Handling**: Graceful degradation when services are unavailable

The system requires:
- Google Cloud project with Calendar API enabled
- Service account with calendar permissions
- Either Anthropic or OpenAI API key

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- July 01, 2025: Complete TailorTalk system implementation
  - Built conversational AI agent with OpenAI GPT-4o integration
  - Implemented Streamlit web interface with chat functionality  
  - Added Google Calendar API integration with service account authentication
  - Created comprehensive setup guide and automated testing script
  - Added demo mode for quota-limited scenarios
  - Implemented natural language processing for appointment scheduling

- July 01, 2025: Deployment preparation complete
  - Created Docker containerization for cloud deployment
  - Added Railway, Render, and Fly.io deployment configurations
  - Prepared comprehensive deployment documentation
  - Created local setup requirements guide
  - System fully ready for cloud hosting and GitHub submission

## User Preferences

- Prefers simple, everyday language for communication
- Wants fully functional system with both AI and calendar integration
- Expects demo mode to work when API quotas are exceeded

## Deployment Notes

The application is designed for easy deployment with:
- Environment variable configuration for API keys
- Graceful fallback to demo mode when quotas exceeded
- Clear setup instructions for Google Calendar integration
- Automated testing scripts for verifying connections