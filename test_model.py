"""
Quick script to test available Gemini models
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Try different model names
models_to_try = [
    "models/gemini-pro",
    "models/gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-pro",
    "gemini-1.5-pro",
]

for model_name in models_to_try:
    try:
        print(f"\n🧪 Testing: {model_name}")
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        response = llm.invoke("Say hello")
        print(f"✅ SUCCESS! Model '{model_name}' is working")
        print(f"Response: {response.content[:50]}...")
        break
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}")

print("\n✓ Test complete")
