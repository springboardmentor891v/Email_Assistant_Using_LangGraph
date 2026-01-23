"""
Email Assistant - Main Application
Runs the complete LangGraph agent workflow
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import run_agent, visualize_graph

# Sample test emails covering all triage categories
test_emails = [
    {
        "subject": "Limited Time Offer!!!",
        "body": "Buy one get one free. Offer valid today. Click here now!"
    },
    {
        "subject": "Meeting Request for Tomorrow",
        "body": "Hi, can we schedule a meeting tomorrow at 2 PM to discuss the Q1 project roadmap? Let me know if you're available."
    },
    {
        "subject": "Invoice approval required",
        "body": "Please review and approve the attached invoice for $5,000. This requires your authorization before we can proceed with payment."
    },
    {
        "subject": "Quick question about calendar",
        "body": "Do you have any availability next week? I'd like to set up a brief call to discuss the new feature requirements."
    }
]


def main():
    """Run the email assistant on test emails"""
    
    print("\n" + "="*70)
    print(" "*20 + "EMAIL ASSISTANT DEMO")
    print("="*70)
    
    # Show graph structure
    visualize_graph()
    
    # Process each test email
    for i, email in enumerate(test_emails, 1):
        print(f"\n{'#'*70}")
        print(f"# TEST EMAIL {i}/{len(test_emails)}")
        print(f"{'#'*70}")
        print(f"\nSubject: {email['subject']}")
        print(f"Body: {email['body']}\n")
        
        try:
            # Run agent
            result = run_agent(
                email_subject=email["subject"],
                email_body=email["body"],
                thread_id=f"test-email-{i}"
            )
            
            # Display results
            print(f"\n{'='*70}")
            print(f"RESULTS:")
            print(f"{'='*70}")
            print(f"Triage Decision: {result['triage_decision']}")
            print(f"\nFinal Output:")
            print(f"{result['final_output']}")
            
            if result.get('react_result'):
                print(f"\nReAct Summary:")
                print(f"  - Iterations: {result['react_result']['iterations']}")
                print(f"  - Actions Taken: {len(result['react_result']['actions_taken'])}")
            
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"\n❌ Error processing email: {str(e)}\n")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✓ All test emails processed!")
    print("="*70)
    print("\nTo view traces and monitoring:")
    print("1. Sign up at https://smith.langchain.com/")
    print("2. Add your LANGCHAIN_API_KEY to .env")
    print("3. Re-run this script to see traces in LangSmith dashboard")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
