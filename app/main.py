"""
Email Assistant - Production Mode
Live Gmail Integration with Human-in-the-Loop
"""
import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import run_agent, visualize_graph
from agent.memory import MemoryStore
from tools.email_tools import list_unread_emails, read_email, send_email, mark_as_read

# Initialize memory
memory = MemoryStore()


def main(poll_interval=60, max_emails=5):
    """
    Continuously poll Gmail inbox and process unread emails.
    
    Args:
        poll_interval: Seconds between polls (default: 60)
        max_emails: Maximum emails to process per poll (default: 5)
    """
    print("="*70)
    print("EMAIL ASSISTANT - LIVE MODE")
    print("="*70)
    print(f"📊 Polling every {poll_interval} seconds")
    print(f"📧 Processing up to {max_emails} emails per poll")
    print(f"⚠️  Human approval required for important emails")
    print(f"🛑 Press Ctrl+C to stop\n")
    
    visualize_graph()
    
    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"\n{'#'*70}")
            print(f"# POLL #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'#'*70}\n")
            
            # Get unread emails
            unread_ids = list_unread_emails(max_results=max_emails)
            
            if not unread_ids:
                print("📭 No unread emails")
            else:
                print(f"📬 Found {len(unread_ids)} unread email(s)\n")
                
                for i, msg_id in enumerate(unread_ids, 1):
                    print(f"\n{'='*70}")
                    print(f"PROCESSING EMAIL {i}/{len(unread_ids)}")
                    print(f"{'='*70}\n")
                    
                    try:
                        # Read email
                        email_data = read_email(msg_id)
                        
                        if not email_data:
                            print(f"⚠️ Could not read email {msg_id}")
                            continue
                        
                        print(f"From: {email_data.get('from', 'Unknown')}")
                        print(f"Subject: {email_data.get('subject', '(no subject)')}")
                        print(f"Date: {email_data.get('date', 'Unknown')}")
                        print(f"\nBody preview:")
                        print(f"{email_data.get('body', '')[:200]}...")
                        print()
                        
                        # Process through agent (includes HITL for important emails)
                        result = run_agent(
                            email_subject=email_data.get('subject', '(no subject)'),
                            email_body=email_data.get('body', ''),
                            thread_id=f"email-{msg_id}"
                        )
                        
                        # Save to memory
                        memory.save(
                            intent=result.get("triage_decision", "unknown"),
                            content={
                                "subject": email_data.get('subject'),
                                "from": email_data.get('from'),
                                "final_output": result.get("final_output")
                            }
                        )
                        
                        # Mark as read
                        mark_as_read(msg_id)
                        print(f"\n✅ Email processed and marked as read")
                        
                    except KeyboardInterrupt:
                        raise  # Allow Ctrl+C to propagate
                    except Exception as e:
                        print(f"❌ Error processing email: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Wait before next poll
            print(f"\n💤 Sleeping {poll_interval} seconds until next poll...")
            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down email assistant...")
        print("✓ Goodbye!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Assistant - Live Mode')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Poll interval in seconds (default: 60)')
    parser.add_argument('--max-emails', type=int, default=5, 
                       help='Max emails to process per poll (default: 5)')
    
    args = parser.parse_args()
    
    try:
        main(poll_interval=args.interval, max_emails=args.max_emails)
    except KeyboardInterrupt:
        print("\n\n✓ Email assistant stopped")
