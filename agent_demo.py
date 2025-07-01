import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from calendar_tools import calendar_tools
from utils import extract_datetime_info, format_response
import re

class TailorTalkAgent:
    """Conversational AI agent for appointment scheduling"""
    
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()
        try:
            self.llm = self._initialize_llm()
            self.demo_mode = False
        except Exception as e:
            print(f"⚠️ LLM initialization failed: {e}")
            print("📝 Running in demo mode with simulated responses")
            self.llm = None
            self.demo_mode = True
    
    def _initialize_llm(self):
        """Initialize the language model"""
        # Try OpenAI first since user provided that key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            return ChatOpenAI(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                temperature=0.1
            )
        
        # Fallback to Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",  # Using stable model
                temperature=0.1
            )
        
        raise ValueError("No valid API key found. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return f"""You are TailorTalk, an intelligent AI assistant specialized in appointment scheduling and calendar management. 

Your capabilities include:
- Understanding natural language requests for booking, checking, and managing appointments
- Extracting dates, times, and appointment details from conversational text
- Checking calendar availability and suggesting optimal time slots
- Booking appointments with proper conflict detection
- Cancelling and rescheduling existing appointments
- Providing clear, friendly responses with appointment confirmations

Guidelines:
1. Always be conversational and helpful
2. Ask for clarification when appointment details are unclear
3. Confirm appointment details before booking
4. Provide clear success/error messages
5. Suggest alternatives when requested times are unavailable
6. Use available tools to interact with the calendar system

Current date and time: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Available tools:
- check_availability: Check available time slots for a date
- book_appointment: Create a new appointment
- list_upcoming_appointments: Show upcoming appointments
- cancel_appointment: Cancel an existing appointment

Remember to be natural and conversational while being precise about appointment details."""
    
    def _get_demo_response(self, user_message: str) -> str:
        """Generate demo responses when LLM is not available"""
        message_lower = user_message.lower()
        
        # Analyze intent
        if any(word in message_lower for word in ['book', 'schedule', 'appointment', 'meeting']):
            if 'tomorrow' in message_lower:
                return "I'd be happy to help you schedule that meeting for tomorrow! Since this is demo mode, I can't access your real calendar, but here's what I would do:\n\n📅 I would check your availability for tomorrow\n⏰ Look for the requested time slot (2 PM)\n✅ Book the meeting if the slot is free\n📧 Send you a confirmation\n\nTo enable real calendar booking, please set up your Google Calendar integration using the setup guide in the sidebar."
            else:
                return "I can help you schedule appointments! Please let me know when you'd like to book it. For example, you could say 'Book a meeting tomorrow at 2 PM' or 'Schedule a call next Friday at 10 AM'.\n\nNote: This is currently demo mode. Set up Google Calendar integration for real appointment booking."
        
        elif any(word in message_lower for word in ['available', 'availability', 'free', 'check']):
            return "I can check availability for you! In demo mode, I would typically:\n\n📅 Look at your calendar for the requested date\n⏰ Show you free time slots\n💡 Suggest the best meeting times\n\nExample available slots for tomorrow might be:\n• 9:00 AM - 10:00 AM\n• 2:00 PM - 4:00 PM\n• 5:00 PM - 6:00 PM\n\nTo check your real availability, please connect Google Calendar."
        
        elif any(word in message_lower for word in ['cancel', 'delete', 'remove']):
            return "I can help you cancel appointments! In demo mode, I would:\n\n🔍 Find the appointment you want to cancel\n❌ Remove it from your calendar\n📧 Send cancellation confirmation\n\nTo cancel real appointments, please set up Google Calendar integration."
        
        elif any(word in message_lower for word in ['list', 'show', 'upcoming']):
            return "Here's what your upcoming appointments might look like:\n\n📅 **Upcoming Appointments (Demo)**\n• Tomorrow 10:00 AM - Team Standup\n• Friday 2:00 PM - Client Meeting\n• Monday 9:00 AM - Project Review\n\nTo see your real appointments, please connect Google Calendar using the setup guide."
        
        elif any(word in message_lower for word in ['hello', 'hi', 'help']):
            return "Hello! I'm TailorTalk, your AI appointment scheduling assistant. I can help you:\n\n📅 **Book appointments** - 'Schedule a meeting tomorrow at 2 PM'\n🔍 **Check availability** - 'What's free this Friday?'\n📋 **List appointments** - 'Show my upcoming meetings'\n❌ **Cancel bookings** - 'Cancel my 3 PM appointment'\n\nCurrently running in demo mode. Connect Google Calendar for real appointment management!"
        
        else:
            return "I'm TailorTalk, your appointment scheduling assistant! I can help you book, check, list, or cancel appointments using natural language.\n\nTry saying something like:\n• 'Book a meeting tomorrow at 2 PM'\n• 'Check my availability Friday'\n• 'Show upcoming appointments'\n\nCurrently in demo mode - connect Google Calendar for real functionality."
    
    def process_message(self, user_message: str) -> str:
        """Main entry point for processing user messages"""
        try:
            # Add to conversation history
            self.conversation_history.append(HumanMessage(content=user_message))
            
            if self.demo_mode or not self.llm:
                response = self._get_demo_response(user_message)
            else:
                # Create messages for LLM with system prompt and conversation history
                messages = [
                    SystemMessage(content=self.system_prompt),
                    *self.conversation_history[-10:],  # Keep last 10 messages for context
                ]
                
                # Bind tools to the model
                llm_with_tools = self.llm.bind_tools(calendar_tools)
                
                # Get response from LLM
                response_obj = llm_with_tools.invoke(messages)
                
                # Handle tool calls if present
                if hasattr(response_obj, 'tool_calls') and response_obj.tool_calls:
                    tool_responses = []
                    for tool_call in response_obj.tool_calls:
                        tool_result = self._execute_tool_call(tool_call)
                        tool_responses.append(tool_result)
                    
                    # Create follow-up message with tool results
                    tool_message = f"Tool execution results: {'; '.join(tool_responses)}"
                    follow_up_messages = messages + [
                        response_obj,
                        HumanMessage(content=tool_message)
                    ]
                    
                    # Get final response incorporating tool results
                    final_response = self.llm.invoke(follow_up_messages)
                    response = final_response.content
                else:
                    response = response_obj.content
            
            # Add assistant response to history
            self.conversation_history.append(AIMessage(content=response))
            
            # Format and return response
            return format_response(str(response))
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an unexpected error: {str(e)}"
            self.conversation_history.append(AIMessage(content=error_message))
            return error_message
    
    def _execute_tool_call(self, tool_call) -> str:
        """Execute a tool call and return the result"""
        try:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Find and execute the appropriate tool
            for tool in calendar_tools:
                if tool.name == tool_name:
                    result = tool.invoke(tool_args)
                    return f"{tool_name}: {result}"
            
            return f"Tool {tool_name} not found"
            
        except Exception as e:
            return f"Error executing {tool_call.get('name', 'unknown tool')}: {str(e)}"
    
    @property
    def calendar_service(self):
        """Property to check if calendar service is available"""
        from calendar_tools import calendar_manager
        return calendar_manager.service is not None