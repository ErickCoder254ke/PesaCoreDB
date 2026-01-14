#!/usr/bin/env python3
"""
Test script to verify Gemini API key is valid
Run this locally to check if your API key works
"""

import requests
import json
import sys

# Your Gemini API key from backend/.env
GEMINI_API_KEY = "AIzaSyAUsWq2fV5yawso5PxuWaFu3BslVoEwxNA"
GEMINI_MODEL = "gemini-flash-latest"

def test_gemini_api_key():
    """Test if the Gemini API key is valid"""
    
    print("=" * 60)
    print("🔍 Testing Gemini API Key")
    print("=" * 60)
    print(f"API Key: {GEMINI_API_KEY[:20]}...{GEMINI_API_KEY[-10:]}")
    print(f"Model: {GEMINI_MODEL}")
    print()
    
    # Gemini API endpoint
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    
    # Test request
    payload = {
        "contents": [{
            "parts": [{
                "text": "Say 'Hello, I am working!' if you can read this."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 50
        }
    }
    
    try:
        print("📡 Sending test request to Gemini API...")
        response = requests.post(
            f"{api_url}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ SUCCESS! API key is VALID and working!")
            print()
            
            data = response.json()
            if data.get("candidates"):
                text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                print(f"🤖 AI Response: {text}")
            
            print()
            print("=" * 60)
            print("✅ Your Gemini API key is configured correctly!")
            print("   The issue must be with Render environment variables.")
            print("   Make sure to set GEMINI_API_KEY on Render backend.")
            print("=" * 60)
            return True
            
        elif response.status_code == 400:
            print("❌ BAD REQUEST (400)")
            print("   The request format is invalid.")
            print()
            print("Response:", response.text)
            return False
            
        elif response.status_code == 403:
            print("❌ FORBIDDEN (403) - API Key is INVALID!")
            print()
            print("Possible causes:")
            print("1. API key is incorrect or expired")
            print("2. API key has restrictions (IP, HTTP referrer, etc.)")
            print("3. Gemini API is not enabled for this project")
            print("4. Billing is not set up (if required)")
            print()
            print("Response:", response.text)
            print()
            print("=" * 60)
            print("🔧 How to fix:")
            print("1. Go to: https://aistudio.google.com/app/apikey")
            print("2. Create a NEW API key")
            print("3. Make sure 'Generative Language API' is enabled")
            print("4. Update backend/.env with the new key")
            print("5. Update GEMINI_API_KEY on Render backend")
            print("=" * 60)
            return False
            
        elif response.status_code == 429:
            print("❌ RATE LIMIT EXCEEDED (429)")
            print("   You've hit the API rate limit.")
            print()
            print("This actually means your API key IS valid!")
            print("Just too many requests. Wait a moment and try again.")
            return True
            
        elif response.status_code == 404:
            print("❌ NOT FOUND (404)")
            print(f"   Model '{GEMINI_MODEL}' not found.")
            print()
            print("Try using a different model:")
            print("- gemini-pro")
            print("- gemini-1.5-flash")
            print("- gemini-1.5-pro")
            return False
            
        else:
            print(f"❌ UNEXPECTED ERROR ({response.status_code})")
            print()
            print("Response:", response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ REQUEST TIMED OUT")
        print("   Check your internet connection.")
        return False
        
    except requests.exceptions.RequestException as e:
        print("❌ NETWORK ERROR")
        print(f"   {str(e)}")
        return False
        
    except Exception as e:
        print("❌ UNEXPECTED ERROR")
        print(f"   {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api_key()
    sys.exit(0 if success else 1)
