# Setting up LLM with Retry Logic and Error Handling
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pathlib import Path
from google.api_core import exceptions as google_exceptions

base_dir = Path(__file__).resolve().parent.parent
dotenv_path = base_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY1"))

# List of models to try in order (fallback mechanism)
MODELS = [
    "gemini-2.0-flash-exp",      # Latest experimental model - often has better quotas
    "gemini-1.5-flash",          # Stable flash model
    "gemini-1.5-flash-8b",       # Smaller, faster model
    "gemini-1.5-pro",            # Pro model (might have different quotas)
]

def llm_call(prompt: str, max_retries: int = 3, retry_delay: int = 2) -> str:
    """
    Call LLM with retry logic and model fallback.
    
    Args:
        prompt: The prompt to send to the model
        max_retries: Maximum number of retries per model
        retry_delay: Initial delay between retries (doubles each time)
    
    Returns:
        The model's response text
    
    Raises:
        Exception: If all models and retries fail
    """
    last_exception = None
    
    # Try each model in sequence
    for model_name in MODELS:
        print(f"🤖 Trying model: {model_name}")
        
        # Retry logic for current model
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                print(f"✅ Success with {model_name}")
                return response.text
                
            except Exception as e:
                last_exception = e
                error_str = str(e)
                
                # Handle quota exceeded errors
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"⚠️  Quota exceeded for {model_name}")
                    
                    # Extract retry delay from error if available
                    if "retry in" in error_str.lower():
                        try:
                            # Try to parse the suggested retry delay
                            import re
                            match = re.search(r'retry in ([\d.]+)s', error_str)
                            if match:
                                suggested_delay = float(match.group(1))
                                if suggested_delay < 60:  # Only wait if less than 60 seconds
                                    print(f"⏳ Waiting {suggested_delay:.1f}s as suggested...")
                                    time.sleep(suggested_delay)
                                    continue  # Try this model again
                        except:
                            pass
                    
                    # Move to next model instead of retrying the same one
                    print(f"↪️  Trying next model...")
                    break  # Break retry loop, try next model
                    
                # Handle rate limit errors (too many requests per minute)
                elif "rate limit" in error_str.lower():
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"⏳ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue  # Retry same model
                    
                # Handle other errors
                else:
                    print(f"❌ Error with {model_name}: {error_str[:100]}")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"⏳ Retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        break  # Try next model
    
    # If all models failed, raise the last exception
    print(f"\n❌ All models exhausted. Last error: {str(last_exception)[:200]}")
    raise Exception(f"All Gemini models failed. Last error: {str(last_exception)}")


def llm_call_simple(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Simple LLM call without JSON formatting (for regular text responses).
    
    Args:
        prompt: The prompt to send
        model: Specific model to use
    
    Returns:
        The model's text response
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"❌ Error in simple LLM call: {e}")
        # Fallback to llm_call with retry logic
        return llm_call(prompt)


def generate_structured_json(prompt: str, schema=None, model: str = "gemini-1.5-flash") -> str:
    """
    Forces JSON output (used in Triage & Draft).
    
    Args:
        prompt: The prompt to send
        schema: Optional JSON schema to enforce
        model: Model to use
    
    Returns:
        JSON formatted response
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )
    
    if schema:
        config.response_schema = schema
        
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        print(f"❌ Error in structured JSON call: {e}")
        # Fallback to regular llm_call with retry logic
        return llm_call(prompt)


# Test function (commented out for production)
# if __name__ == "__main__":
#     print(llm_call("Say hello in JSON format with a 'message' field"))