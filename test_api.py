#!/usr/bin/env python
"""
Simple script to test API connection with the current configuration.
"""

import os
import json
import sys
from dotenv import load_dotenv
import requests

def test_api_connection():
    """Test the API connection with the current configuration."""
    # Load environment variables
    load_dotenv()
    
    print("===== API Configuration Test =====")
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.strip() == "sk-":
        print("❌ API key is not properly set in .env file")
        print(f"Current value: '{api_key}'")
        print("Please update your .env file with a valid API key.")
        return False
    else:
        print("✅ API key is set")
    
    # Check API base URL
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("❌ API base URL is not set in .env file")
        return False
    else:
        print(f"✅ API base URL is set to: {api_base}")
    
    # Check model
    model = os.getenv("AI_MODEL")
    if not model:
        print("⚠️ AI_MODEL is not set in .env file, will use default")
        model = "gpt-4"
    else:
        print(f"✅ Using model: {model}")
    
    # Attempt to make a simple API call
    print("\nTesting API connection...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello! This is a test message. Please respond with 'API test successful'."}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # Set timeout to 30 seconds
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print("✅ API call successful!")
            print("Response:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            return True
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print("Error response:")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    if success:
        print("\n✅ All tests passed! Your configuration is working correctly.")
    else:
        print("\n❌ Test failed. Please check your configuration and try again.")
        sys.exit(1) 