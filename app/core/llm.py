def load_llm():
    from dotenv import load_dotenv
    import os
    from langchain_google_genai import ChatGoogleGenerativeAI

    load_dotenv()

    # LangChain prefers GOOGLE_API_KEY
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not GOOGLE_API_KEY:
        raise ValueError("Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env")

    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",   # ✅ WORKING MODEL
        temperature=0,
        google_api_key=GOOGLE_API_KEY
    )

    return llm
