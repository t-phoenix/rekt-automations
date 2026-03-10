"""Test LLM connection."""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing LLM connections...\n")

# Test Google API Key
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    print(f"✓ GOOGLEAPI_KEY found: {google_key[:10]}...")
else:
    print("✗ GOOGLE_API_KEY not found")

# Test OpenAI API Key  
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"✓ OPENAI_API_KEY found: {openai_key[:10]}...")
else:
    print("✗ OPENAI_API_KEY not found")

print("\n" + "="*50)
if google_key:
    print("Testing Google Gemini...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Hello from Gemini!'")
        print(f"✓ Gemini works: {response.text}")
    except Exception as e:
        print(f"✗ Gemini failed: {e}")

if openai_key:
    print("\nTesting OpenAI...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello from OpenAI!'"}]
        )
        print(f"✓ OpenAI works: {response.choices[0].message.content}")
    except Exception as e:
        print(f"✗ OpenAI failed: {e}")
