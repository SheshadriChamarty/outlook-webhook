import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load the environment variables
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file.")
else:
    print(f"✅ Key found: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("\nQuerying Google for available models...")
        
        models = list(genai.list_models())
        chat_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
        
        if chat_models:
            print(f"\n✅ SUCCESS! Found {len(chat_models)} available models:")
            for m in chat_models:
                print(f"   - {m.name}")
            
            print("\nRecommended Action:")
            print(f"Copy the name '{chat_models[0].name.replace('models/', '')}' and use that in your agent files.")
        else:
            print("\n❌ Connected to Google, but no Chat models were found for this API Key.")
            print("Check if the 'Gemini API' is enabled in your Google Cloud Console.")

    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")