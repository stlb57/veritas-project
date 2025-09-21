
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
from dotenv import load_dotenv
load_dotenv()

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found or is empty.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("✅ Gemini text analysis model loaded successfully.")

except Exception as e:
    print(f"❌ Error initializing Gemini: {e}")
    model = None


def analyze_text_content(content: str):
    if model is None:
        raise RuntimeError("Gemini model is not available due to an initialization error.")
        
    if not content.strip():
        return {"decision": "Error", "confidence": 0.0, "reason": "Input cannot be empty."}

    # Step 1: Auto-detect URL vs text
    is_url = content.startswith("http://") or content.startswith("https://")

    if is_url:
        try:
            resp = requests.get(content, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            text_to_analyze = " ".join([p.get_text() for p in soup.find_all("p")])
            if not text_to_analyze.strip():
                return {"decision": "Error", "confidence": 0.0, "reason": "No extractable text found at URL."}
        except Exception as e:
            return {"decision": "Error", "confidence": 0.0, "reason": f"Failed to fetch or parse URL: {e}"}
    else:
        text_to_analyze = content

    prompt = f"""
    You are an expert fact-checking system. Your sole purpose is to analyze the provided text and determine its factual accuracy.

    Input Text:
    ---
    {text_to_analyze}
    ---

    Task:
    1.  Decide if the claim or news in the input text is "Real" or "Fake".
    2.  Provide a confidence score between 0.00 and 1.00 for your decision.
    3.  You MUST respond ONLY with a single, clean JSON object in the following format and nothing else:
    {{"decision": "Real/Fake", "confidence": 0.xx, "reason": "A brief one-sentence explanation for your decision."}}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        result_dict = json.loads(cleaned_response)
        return result_dict
    except Exception as e:
        print(f"Error processing Gemini response: {e}")
        return {"decision": "Error", "confidence": 0.0, "reason": "Failed to get a valid analysis from the AI model."}