import streamlit as st
import json
from datetime import datetime, timedelta
from agent_demo import TailorTalkAgent
import traceback

# Page configuration
st.set_page_config(
    page_title="TailorTalk - AI Appointment Scheduler",
    page_icon="📅",
    layout="wide"
)

# Custom CSS for chat interface
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}
.chat-message.user {
    background-color: #2e7bcf;
    color: white;
    margin-left: 20%;
}
.chat-message.assistant {
    background-color: #f0f2f6;
    color: black;
    margin-right: 20%;
}
.chat-message .message-content {
    margin: 0;
}
.chat-message .timestamp {
    font-size: 0.8em;
    opacity: 0.7;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        try:
            st.session_state.agent = TailorTalkAgent()
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.session_state.agent = None

def display_chat_message(message, is_user=False):
    """Display a chat message with styling"""
    message_class = "user" if is_user else "assistant"
    timestamp = datetime.now().strftime("%H:%M")
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-content">{message}</div>
        <div class="timestamp">{timestamp}</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.title("📅 TailorTalk - AI Appointment Scheduler")
    st.markdown("*Your intelligent assistant for booking appointments through natural conversation*")
    
    # Initialize session state
    initialize_session_state()
    
    if st.session_state.agent is None:
        st.error("⚠️ Agent initialization failed. Please check your configuration and API keys.")
        st.info("""
        **Required Environment Variables:**
        - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: Your LLM API key ✅ (Configured)
        - `GOOGLE_CALENDAR_ID`: Your Google Calendar ID (optional, defaults to primary)
        
        **Required Files:**
        - `credentials.json`: Google Service Account credentials file
        """)
        return
    
    # Sidebar with information
    with st.sidebar:
        st.header("📋 How to Use")
        st.markdown("""
        Simply chat naturally to:
        - **Book appointments**: "I need to schedule a meeting tomorrow at 2 PM"
        - **Check availability**: "What's available this Friday afternoon?"
        - **Cancel bookings**: "Cancel my 3 PM appointment today"
        
        The AI will understand your request and help you manage your calendar!
        """)
        
        st.header("🔧 System Status")
        if st.session_state.agent:
            st.success("✅ AI Agent Active")
            if hasattr(st.session_state.agent, 'demo_mode') and st.session_state.agent.demo_mode:
                st.info("🎯 Running in Demo Mode")
            if hasattr(st.session_state.agent, 'calendar_service') and st.session_state.agent.calendar_service:
                st.success("✅ Google Calendar Connected")
            else:
                st.warning("⚠️ Google Calendar Not Connected")
                st.info("📝 Currently using demo responses. Connect Google Calendar for real integration.")
        else:
            st.error("❌ AI Agent Inactive")
        
        st.header("🛠️ Google Calendar Integration")
        with st.expander("📅 Connect Your Calendar (Click to Expand)"):
            st.markdown("""
            **Quick Setup Steps:**
            
            1. **Create Google Cloud Project**
               - Go to [Google Cloud Console](https://console.cloud.google.com/)
               - Create new project or select existing one
            
            2. **Enable API & Create Credentials**
               - Enable Google Calendar API
               - Create service account credentials
               - Download JSON credentials file
            
            3. **Update TailorTalk**
               - Replace `credentials.json` with your downloaded file
               - Share your calendar with the service account email
            
            4. **Test Connection**
               - Run: `python setup_google_calendar.py`
               - Follow the verification steps
            
            📖 **[Detailed Setup Guide](./GOOGLE_CALENDAR_SETUP.md)**
            """)
            
            if st.button("🧪 Test Calendar Connection"):
                st.info("Run `python setup_google_calendar.py` in terminal to test your Google Calendar setup.")
        
        with st.expander("📝 Current Features"):
            st.markdown("""
            **Available Now (Demo Mode):**
            - Natural language appointment scheduling
            - Conversation-based calendar management
            - Smart date/time extraction
            - Professional chat interface
            
            **With Google Calendar Connected:**
            - Real appointment booking
            - Actual availability checking
            - Live calendar synchronization
            - Event conflict detection
            """)
        
        with st.expander("Quick Test Commands"):
            st.markdown("""
            **Try these example commands:**
            - "What's my availability tomorrow?"
            - "Book a team meeting tomorrow at 2 PM"
            - "Show my upcoming appointments"
            - "Cancel my meeting on Friday"
            
            **Note:** Calendar integration shows placeholder responses until Google Calendar is connected.
            """)
        
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Chat interface
    st.header("💬 Chat with TailorTalk")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            display_chat_message(message['content'], message['role'] == 'user')
    
    # Chat input
    user_input = st.chat_input("Type your message here... (e.g., 'Book a meeting tomorrow at 2 PM')")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Display user message
        with chat_container:
            display_chat_message(user_input, is_user=True)
        
        # Get agent response
        try:
            with st.spinner("TailorTalk is thinking..."):
                response = st.session_state.agent.process_message(user_input)
            
            # Add assistant response to history
            st.session_state.messages.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Display assistant response
            with chat_container:
                display_chat_message(response, is_user=False)
                
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.error(error_message)
            
            # Add error to message history
            st.session_state.messages.append({
                'role': 'assistant',
                'content': error_message,
                'timestamp': datetime.now().isoformat()
            })
    
    # Auto-scroll to bottom
    if st.session_state.messages:
        st.rerun()

if __name__ == "__main__":
    main()
