"""
Mock Calendar Tools for Email Assistant
These tools simulate calendar operations with in-memory data.
Real Google Calendar API integration will be added in later milestones.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from langchain.tools import tool

# Mock calendar data (in-memory storage)
MOCK_CALENDAR = {
    "meetings": [
        {
            "id": 1,
            "title": "Team Standup",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "09:00",
            "duration": 30,
            "attendees": ["team@company.com"]
        },
        {
            "id": 2,
            "title": "Project Review",
            "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "time": "14:00",
            "duration": 60,
            "attendees": ["manager@company.com", "stakeholder@company.com"]
        }
    ]
}


@tool
def get_available_slots(date: str) -> str:
    """
    Get available time slots for a given date.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        String listing available time slots
    """
    try:
        # Parse the date
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Check if date is in the past
        if target_date.date() < datetime.now().date():
            return f"Cannot check availability for past dates. Today is {datetime.now().strftime('%Y-%m-%d')}"
        
        # Get meetings for this date
        meetings_on_date = [
            m for m in MOCK_CALENDAR["meetings"] 
            if m["date"] == date
        ]
        
        # Standard working hours: 9 AM to 5 PM
        all_slots = [
            "09:00", "10:00", "11:00", "12:00", 
            "13:00", "14:00", "15:00", "16:00"
        ]
        
        # Remove booked slots
        booked_slots = [m["time"] for m in meetings_on_date]
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        if not available_slots:
            return f"No available slots on {date}. All time slots are booked."
        
        return f"Available slots on {date}: {', '.join(available_slots)}"
        
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2026-01-25)"


@tool
def schedule_meeting(date: str, time: str, duration: int, title: str, attendees: str) -> str:
    """
    Schedule a meeting in the calendar.
    
    Args:
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        duration: Duration in minutes
        title: Meeting title
        attendees: Comma-separated email addresses
        
    Returns:
        Confirmation message
    """
    try:
        # Validate date
        target_date = datetime.strptime(date, "%Y-%m-%d")
        if target_date.date() < datetime.now().date():
            return f"Cannot schedule meetings in the past. Today is {datetime.now().strftime('%Y-%m-%d')}"
        
        # Validate time format
        datetime.strptime(time, "%H:%M")
        
        # Check if slot is available
        meetings_on_date = [
            m for m in MOCK_CALENDAR["meetings"] 
            if m["date"] == date
        ]
        
        if any(m["time"] == time for m in meetings_on_date):
            return f"Time slot {time} on {date} is already booked. Please choose another time."
        
        # Parse attendees
        attendee_list = [email.strip() for email in attendees.split(",")]
        
        # Create new meeting
        new_meeting = {
            "id": len(MOCK_CALENDAR["meetings"]) + 1,
            "title": title,
            "date": date,
            "time": time,
            "duration": duration,
            "attendees": attendee_list
        }
        
        # Add to calendar
        MOCK_CALENDAR["meetings"].append(new_meeting)
        
        return (
            f"✓ Meeting scheduled successfully!\n"
            f"Title: {title}\n"
            f"Date: {date} at {time}\n"
            f"Duration: {duration} minutes\n"
            f"Attendees: {', '.join(attendee_list)}\n"
            f"Meeting ID: {new_meeting['id']}"
        )
        
    except ValueError as e:
        return f"Invalid format. Please use correct date (YYYY-MM-DD) and time (HH:MM) formats. Error: {str(e)}"


@tool
def list_upcoming_meetings(days_ahead: int = 7) -> str:
    """
    List all upcoming meetings within the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        String listing upcoming meetings
    """
    try:
        if days_ahead < 1:
            return "Please specify at least 1 day ahead."
        
        # Calculate date range
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        # Filter meetings in range
        upcoming = []
        for meeting in MOCK_CALENDAR["meetings"]:
            meeting_date = datetime.strptime(meeting["date"], "%Y-%m-%d").date()
            if today <= meeting_date <= end_date:
                upcoming.append(meeting)
        
        # Sort by date and time
        upcoming.sort(key=lambda m: (m["date"], m["time"]))
        
        if not upcoming:
            return f"No meetings scheduled in the next {days_ahead} days."
        
        # Format output
        result = [f"Upcoming meetings in the next {days_ahead} days:\n"]
        for meeting in upcoming:
            result.append(
                f"• {meeting['title']}\n"
                f"  Date: {meeting['date']} at {meeting['time']}\n"
                f"  Duration: {meeting['duration']} min\n"
                f"  Attendees: {', '.join(meeting['attendees'])}\n"
            )
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error retrieving meetings: {str(e)}"


# Export all tools
ALL_CALENDAR_TOOLS = [
    get_available_slots,
    schedule_meeting,
    list_upcoming_meetings
]
