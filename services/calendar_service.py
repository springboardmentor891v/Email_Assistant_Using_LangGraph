"""
Calendar Service Layer

Wraps Google Calendar API functionality for the web interface.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tools import check_availability, add_event, delete_event


class CalendarService:
    """
    Service class for Google Calendar operations.
    """
    
    @staticmethod
    def get_upcoming_events(service, days_ahead=7, max_results=10):
        """
        Get upcoming calendar events.
        
        Args:
            service: Calendar API service instance
            days_ahead: Number of days to look ahead
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_date = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_date,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            parsed_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                parsed_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', [])
                })
            
            return parsed_events
        
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
    
    @staticmethod
    def check_time_availability(service, start_time_iso):
        """
        Check if a specific time slot is available.
        
        Args:
            service: Calendar API service instance
            start_time_iso: ISO format time string
            
        Returns:
            dict with status and conflicting event if busy
        """
        try:
            return check_availability(service, start_time_iso)
        except Exception as e:
            print(f"Error checking availability: {e}")
            return {
                'status': 'ERROR',
                'event': None
            }
    
    @staticmethod
    def create_event(service, summary, start_time_iso, duration_hours=1):
        """
        Create a new calendar event.
        
        Args:
            service: Calendar API service instance
            summary: Event title
            start_time_iso: Start time in ISO format
            duration_hours: Event duration in hours
            
        Returns:
            Success status and message
        """
        try:
            result = add_event(service, summary, start_time_iso)
            
            return {
                'success': 'Success' in result,
                'message': result
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error creating event: {str(e)}"
            }
    
    @staticmethod
    def remove_event(service, event_id):
        """
        Delete a calendar event.
        
        Args:
            service: Calendar API service instance
            event_id: ID of event to delete
            
        Returns:
            Success status
        """
        try:
            success = delete_event(service, event_id)
            return success
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    @staticmethod
    def get_event_count(service, days_ahead=7):
        """
        Get count of upcoming events.
        
        Args:
            service: Calendar API service instance
            days_ahead: Number of days to look ahead
            
        Returns:
            Count of events
        """
        events = CalendarService.get_upcoming_events(service, days_ahead)
        return len(events)
    
    @staticmethod
    def format_event_for_display(event):
        """
        Format event data for display in templates.
        
        Args:
            event: Event dictionary
            
        Returns:
            Formatted event dict
        """
        try:
            # Parse datetime
            start_dt = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            
            return {
                'id': event['id'],
                'title': event['summary'],
                'date': start_dt.strftime('%B %d, %Y'),
                'time': start_dt.strftime('%I:%M %p'),
                'description': event.get('description', 'No description'),
                'location': event.get('location', 'No location')
            }
        except:
            return event
