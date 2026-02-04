"""
Test script to verify Gemini API configuration and quota handling
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gemini import llm_call

def test_gemini_api():
    """Test the Gemini API with retry logic"""
    
    print("=" * 60)
    print("🧪 TESTING GEMINI API WITH QUOTA HANDLING")
    print("=" * 60)
    print()
    
    test_prompt = """
    Return a simple JSON response: 
    {
        "status": "working",
        "message": "Gemini API is functioning correctly"
    }
    """
    
    try:
        print("📤 Sending test prompt...")
        print()
        
        response = llm_call(test_prompt)
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! API is working correctly")
        print("=" * 60)
        print()
        print("📥 Response:")
        print(response)
        print()
        
        # Parse and validate
        import json
        data = json.loads(response)
        
        if data.get("status") == "working":
            print("✅ Response validation: PASSED")
            print("✅ JSON parsing: PASSED")
            print()
            print("🎉 All systems operational!")
            return True
        else:
            print("⚠️  Response validation: UNEXPECTED FORMAT")
            return False
            
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Possible causes:")
        print("  1. All Gemini models have quota exceeded")
        print("  2. Invalid API key in .env file")
        print("  3. Network connectivity issue")
        print()
        print("Solutions:")
        print("  - Wait a few minutes for quota to reset")
        print("  - Check GEMINI_API_KEY1 in .env file")
        print("  - Check internet connection")
        print("  - See QUOTA_FIX_GUIDE.md for details")
        return False


if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)
