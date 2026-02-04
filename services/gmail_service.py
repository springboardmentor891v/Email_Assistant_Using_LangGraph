"""
Gmail Service Layer

Wraps Gmail API functionality for the web interface.
Provides clean methods for fetching, searching, and sending emails.
"""

import sys
import os
import base64
from email.mime.text import MIMEText

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tools import fetch_recent_emails, search_gmail, extract_email_parts


class GmailService:
    """
    Service class for Gmail operations.
    """
    
    @staticmethod
    def get_recent_emails(service, max_results=10):
        """
        Fetch recent emails from inbox.
        
        Args:
            service: Gmail API service instance
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries with parsed content
        """
        try:
            raw_emails = fetch_recent_emails(service, max_results)
            parsed_emails = []
            
            for email in raw_emails:
                sender, subject, body = extract_email_parts(email)
                
                parsed_emails.append({
                    'id': email['id'],
                    'sender': sender,
                    'subject': subject,
                    'body': body,
                    'snippet': email.get('snippet', ''),
                    'date': GmailService._get_email_date(email),
                    'labels': email.get('labelIds', [])
                })
            
            return parsed_emails
        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    @staticmethod
    def _get_email_date(email):
        """Extract and format email date"""
        headers = email.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name', '').lower() == 'date':
                return header.get('value', '')
        return 'Unknown date'
    
    @staticmethod
    def get_unread_count(service):
        """
        Get count of unread emails.
        
        Args:
            service: Gmail API service instance
            
        Returns:
            Count of unread emails
        """
        try:
            results = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=1
            ).execute()
            
            return results.get('resultSizeEstimate', 0)
        
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
    
    @staticmethod
    def search_emails(service, query, max_results=10):
        """
        Search emails using Gmail query syntax.
        
        Args:
            service: Gmail API service instance
            query: Gmail search query
            max_results: Maximum results to return
            
        Returns:
            List of matching emails
        """
        try:
            emails, count = search_gmail(service, query, max_results)
            
            parsed_emails = []
            for email in emails:
                sender, subject, body = extract_email_parts(email)
                
                parsed_emails.append({
                    'id': email['id'],
                    'sender': sender,
                    'subject': subject,
                    'body': body[:200] + '...' if len(body) > 200 else body,
                    'date': GmailService._get_email_date(email)
                })
            
            return parsed_emails
        
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    @staticmethod
    def send_email(service, to: str, subject: str, body: str):
        """
        Send an email via Gmail API.
        
        Args:
            service: Gmail API service instance
            to: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            dict with success status and message
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            send_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': send_message['id'],
                'message': 'Email sent successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to send email'
            }
    
    @staticmethod
    def get_email_categories(service):
        """
        Get count of emails by category.
        
        Returns:
            dict with category counts
        """
        try:
            # Count emails in different categories
            inbox_count = GmailService._count_by_label(service, 'INBOX')
            unread_count = GmailService.get_unread_count(service)
            
            # Count by Gmail categories
            social_count = GmailService._count_by_category(service, 'social')
            promotions_count = GmailService._count_by_category(service, 'promotions')
            
            return {
                'inbox': inbox_count,
                'unread': unread_count,
                'social': social_count,
                'promotions': promotions_count
            }
        
        except Exception as e:
            print(f"Error getting categories: {e}")
            return {
                'inbox': 0,
                'unread': 0,
                'social': 0,
                'promotions': 0
            }
    
    @staticmethod
    def _count_by_label(service, label):
        """Count emails with specific label"""
        try:
            results = service.users().messages().list(
                userId='me',
                labelIds=[label],
                maxResults=1
            ).execute()
            return results.get('resultSizeEstimate', 0)
        except:
            return 0
    
    @staticmethod
    def _count_by_category(service, category):
        """Count emails in Gmail category"""
        try:
            results = service.users().messages().list(
                userId='me',
                q=f'category:{category}',
                maxResults=1
            ).execute()
            return results.get('resultSizeEstimate', 0)
        except:
            return 0
