"""
Email Tools for Email Assistant
These tools handle email operations including sending and drafting responses.
"""

from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for draft generation
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    temperature=0.7
)


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email to the specified recipient.
    This is a mock implementation that simulates sending.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Confirmation message
    """
    # Mock implementation - in production, this would use Gmail API
    print("\n" + "="*60)
    print("📧 EMAIL SENT (MOCK)")
    print("="*60)
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print("="*60 + "\n")
    
    return (
        f"✓ Email sent successfully!\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"Status: Delivered (mock)"
    )


@tool
def draft_response(original_subject: str, original_body: str, response_type: str = "polite") -> str:
    """
    Generate a draft email response using AI.
    
    Args:
        original_subject: Subject of the email being replied to
        original_body: Body of the email being replied to
        response_type: Type of response (polite, brief, detailed, meeting_acceptance, meeting_decline)
        
    Returns:
        Generated draft email text
    """
    # Define response templates based on type
    templates = {
        "polite": """
You are a helpful email assistant. Generate a polite and professional email response.

Original Email:
Subject: {subject}
Body: {body}

Generate a polite, professional response that:
1. Acknowledges the email
2. Addresses the main points
3. Is warm and courteous
4. Ends with an appropriate closing

Response:
""",
        "brief": """
You are a helpful email assistant. Generate a brief, concise email response.

Original Email:
Subject: {subject}
Body: {body}

Generate a brief, to-the-point response that:
1. Directly addresses the request
2. Uses minimal words
3. Remains professional

Response:
""",
        "detailed": """
You are a helpful email assistant. Generate a detailed email response.

Original Email:
Subject: {subject}
Body: {body}

Generate a comprehensive response that:
1. Addresses all points raised
2. Provides thorough explanations
3. Includes relevant details
4. Maintains professional tone

Response:
""",
        "meeting_acceptance": """
You are a helpful email assistant. Generate a meeting acceptance response.

Original Email:
Subject: {subject}
Body: {body}

Generate a response that:
1. Confirms acceptance of the meeting
2. Confirms the time and date mentioned
3. Expresses enthusiasm
4. Offers to prepare if needed

Response:
""",
        "meeting_decline": """
You are a helpful email assistant. Generate a polite meeting decline response.

Original Email:
Subject: {subject}
Body: {body}

Generate a response that:
1. Politely declines the meeting
2. Provides a brief, professional reason
3. Offers alternative times if appropriate
4. Maintains positive relationship

Response:
"""
    }
    
    # Select template
    template_text = templates.get(response_type, templates["polite"])
    
    # Create prompt
    prompt = PromptTemplate(
        input_variables=["subject", "body"],
        template=template_text
    )
    
    # Generate response
    chain = prompt | llm
    response = chain.invoke({
        "subject": original_subject,
        "body": original_body
    })
    
    draft = response.content.strip()
    
    return f"📝 DRAFT RESPONSE ({response_type}):\n\n{draft}"


# Export all tools
ALL_EMAIL_TOOLS = [
    send_email,
    draft_response
]
