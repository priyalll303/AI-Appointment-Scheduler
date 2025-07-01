import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.func import entrypoint, task
from langgraph.types import StreamWriter
from langgraph.checkpoint.memory import MemorySaver
from calendar_tools import calendar_tools
from utils import extract_datetime_info, format_response
import re

class TailorTalkAgent:
    """Conversational AI agent for appointment scheduling"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.checkpointer = MemorySaver()
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()
    
    def _initialize_llm(self):
        """Initialize the language model"""
        # Try Anthropic first
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            return ChatAnthropic(
                model="claude-sonnet-4-20250514",  # Latest model as of 2025
                api_key=anthropic_key,
                temperature=0.1
            )
        
        # Fallback to OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            return ChatOpenAI(
                model="gpt-4o",  # Latest OpenAI model
                api_key=openai_key,
                temperature=0.1
            )
        
        raise ValueError("No valid API key found. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are TailorTalk, an intelligent AI assistant specialized in appointment scheduling and calendar management. 

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

Current date and time: {current_datetime}

Available tools:
- check_availability: Check available time slots for a date
- book_appointment: Create a new appointment
- list_upcoming_appointments: Show upcoming appointments
- cancel_appointment: Cancel an existing appointment

Remember to be natural and conversational while being precise about appointment details.""".format(
            current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    
    @task
    def analyze_request(self, user_message: str) -> Dict[str, Any]:
        """Analyze user request and extract intent and details"""
        try:
            # Extract datetime information
            datetime_info = extract_datetime_info(user_message)
            
            # Determine intent
            intent = self._determine_intent(user_message)
            
            return {
                'intent': intent,
                'datetime_info': datetime_info,
                'original_message': user_message,
                'extracted_details': self._extract_appointment_details(user_message)
            }
        except Exception as e:
            return {
                'intent': 'error',
                'error': str(e),
                'original_message': user_message
            }
    
    def _determine_intent(self, message: str) -> str:
        """Determine user intent from message"""
        message_lower = message.lower()
        
        booking_keywords = ['book', 'schedule', 'appointment', 'meeting', 'reserve', 'set up']
        checking_keywords = ['available', 'free', 'check', 'availability', 'when']
        cancelling_keywords = ['cancel', 'delete', 'remove', 'reschedule']
        listing_keywords = ['list', 'show', 'upcoming', 'appointments', 'schedule']
        
        if any(keyword in message_lower for keyword in booking_keywords):
            return 'book'
        elif any(keyword in message_lower for keyword in checking_keywords):
            return 'check'
        elif any(keyword in message_lower for keyword in cancelling_keywords):
            return 'cancel'
        elif any(keyword in message_lower for keyword in listing_keywords):
            return 'list'
        else:
            return 'general'
    
    def _extract_appointment_details(self, message: str) -> Dict[str, str]:
        """Extract appointment details from message"""
        details = {}
        
        # Extract potential appointment title/summary
        title_patterns = [
            r'(?:book|schedule)\s+(?:a\s+)?([^.!?]+?)(?:\s+on|\s+for|\s+at|$)',
            r'(?:meeting|appointment)\s+(?:about\s+|for\s+|with\s+)?([^.!?]+?)(?:\s+on|\s+at|$)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                details['summary'] = match.group(1).strip()
                break
        
        # Extract location if mentioned
        location_patterns = [
            r'(?:at|in)\s+([A-Za-z0-9\s,]+?)(?:\s+on|\s+at|\s+for|$)',
            r'location[:\s]+([^.!?]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match and not any(time_word in match.group(1).lower() for time_word in ['morning', 'afternoon', 'evening', 'pm', 'am']):
                details['location'] = match.group(1).strip()
                break
        
        return details
    
    @entrypoint(checkpointer=MemorySaver())
    def process_message(self, user_message: str, writer: Optional[StreamWriter] = None) -> str:
        """Main entry point for processing user messages"""
        try:
            # Add to conversation history
            self.conversation_history.append(HumanMessage(content=user_message))
            
            # Analyze the request
            analysis = self.analyze_request(user_message)
            
            if analysis['intent'] == 'error':
                return f"I'm sorry, I encountered an error analyzing your request: {analysis['error']}"
            
            # Create messages for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                *self.conversation_history[-10:],  # Keep last 10 messages for context
            ]
            
            # Bind tools to the model
            llm_with_tools = self.llm.bind_tools(calendar_tools)
            
            # Get response from LLM
            response = llm_with_tools.invoke(messages)
            
            # Handle tool calls if present
            if response.tool_calls:
                tool_responses = []
                for tool_call in response.tool_calls:
                    tool_result = self._execute_tool_call(tool_call)
                    tool_responses.append(tool_result)
                
                # Create follow-up message with tool results
                tool_message = f"Tool execution results: {'; '.join(tool_responses)}"
                follow_up_messages = messages + [
                    response,
                    HumanMessage(content=tool_message)
                ]
                
                # Get final response incorporating tool results
                final_response = self.llm.invoke(follow_up_messages)
                assistant_message = final_response.content
            else:
                assistant_message = response.content
            
            # Add assistant response to history
            self.conversation_history.append(AIMessage(content=assistant_message))
            
            # Format and return response
            return format_response(assistant_message)
            
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
