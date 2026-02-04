# 🚨 Gemini API Model Compatibility Guide

## ✅ Current Configuration

**Model:** `gemini-2.0-flash-exp` (Experimental)  
**API Version:** v1beta  
**Status:** Working ✅

---

## Available Models for v1beta API

### ✅ Working Models

| Model Name | Rate Limit (Free) | Status | Speed | Quality |
|------------|------------------|--------|-------|---------|
| **gemini-2.0-flash-exp** ✅ | Good | Experimental | Very Fast | Excellent |
| **gemini-2.5-flash-lite** | 20/day | Stable | Fastest | Good |
| **gemini-exp-1206** | Good | Experimental | Fast | Excellent |

### ❌ Models NOT Available in v1beta

- ❌ `gemini-1.5-flash` - Use older SDK or different API version
- ❌ `gemini-1.5-pro` - Use older SDK or different API version

---

## Why Model Names Matter

The `google-genai` Python SDK uses **v1beta API** by default, which only supports certain model names. The model names changed between API versions.

### API Version Differences

```python
# v1beta API (current SDK):
✅ "gemini-2.0-flash-exp"
✅ "gemini-2.5-flash-lite"  
❌ "gemini-1.5-flash"  # Not available

# v1 API (older/different SDK):
✅ "gemini-1.5-flash"
✅ "gemini-1.5-pro"
❌ "gemini-2.0-flash-exp"  # Not available
```

---

## Current Fix Applied ✅

**File:** `src/gemini.py` (Line 16)

```python
# BEFORE (404 error):
model="gemini-1.5-flash"

# AFTER (working):
model="gemini-2.0-flash-exp"  ✅
```

---

## How to Check Available Models

```python
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY1"))

# List all available models
for model in client.models.list():
    print(f"Model: {model.name}")
    print(f"  Supports: {model.supported_generation_methods}")
    print()
```

---

## Rate Limit Strategy

### Option 1: Use Experimental Models (Current)
- ✅ `gemini-2.0-flash-exp` - High limits, cutting edge
- ⚠️ May change or be deprecated
- ✅ Best for development and testing

### Option 2: Use Stable Models
- ✅ `gemini-2.5-flash-lite` - Stable, proven
- ❌ Only 20 requests/day on free tier
- ✅ Best for production with paid tier

### Option 3: Upgrade to Paid Tier
- ✅ Much higher rate limits
- ✅ All models available
- ✅ Production SLA
- 💰 Costs money

---

## Troubleshooting Model Errors

### Error: "models/X is not found for API version v1beta"

**Solution:**
1. Check model name is valid for v1beta
2. Use `gemini-2.0-flash-exp` or `gemini-2.5-flash-lite`
3. OR switch to different Python SDK version

### Error: "429 RESOURCE_EXHAUSTED"

**Solution:**
1. Wait for rate limit to reset
2. Switch to experimental model (higher limits)
3. Upgrade to paid tier

### Error: "Invalid API key"

**Solution:**
1. Check `.env` has `GEMINI_API_KEY1` set
2. Verify API key is valid at https://makersuite.google.com/app/apikey
3. Check API key has no extra spaces

---

## Recommended Configuration

### For Development
```python
model = "gemini-2.0-flash-exp"  # ✅ Best choice
```

### For Production (Free Tier)
```python
model = "gemini-2.5-flash-lite"  # Limited but stable
# Implement caching and rate limiting!
```

### For Production (Paid Tier)
```python
model = "gemini-2.0-flash-exp"  # Or latest stable
# With billing enabled, all limits are much higher
```

---

## API Documentation

- **Gemini API Docs:** https://ai.google.dev/gemini-api/docs
- **Model Catalog:** https://ai.google.dev/gemini-api/docs/models
- **Python SDK:** https://github.com/google/generative-ai-python
- **Rate Limits:** https://ai.google.dev/gemini-api/docs/rate-limits

---

## Changes History

1. **Initial:** `gemini-2.5-flash-lite` (20 req/day) ✅
2. **Upgrade Attempt:** `gemini-1.5-flash` (404 error) ❌
3. **Final Fix:** `gemini-2.0-flash-exp` (working) ✅

---

**Current model working correctly with v1beta API!** 🎉
