import matplotlib
matplotlib.use('Agg') # Set the non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import google.generativeai as genai
import librosa
import librosa.display
import numpy as np
import json
import re
import os
from PIL import Image

# --- CONFIGURATION ---
# ⚠️ IMPORTANT: Replace "YOUR_GEMINI_API_KEY" with your actual key.
# For better security, it's recommended to load this from an environment variable.
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY") 
genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("✅ Gemini analysis model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading Gemini model. Check your API key. Error: {e}")
    model = None

# --- Helper Function to Create Spectrogram ---
def create_spectrogram(audio_path, output_path="temp_spectrogram.png"):
    """Generates and saves a spectrogram image from an audio file."""
    try:
        y, sr = librosa.load(audio_path, sr=22050)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=256, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)

        plt.figure(figsize=(10, 4))
        librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', fmax=8000)
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        return output_path
    except Exception as e:
        print(f"Error creating spectrogram: {e}")
        return None

# --- Main Analysis Function ---
def analyze_audio_content(audio_path: str):
    """
    Analyzes an audio file by creating a spectrogram and using the Gemini API.
    """
    if model is None:
        return {"error": "Gemini model is not available. Please check configuration."}

    # The prompt instructs the model on how to behave and what to look for
    prompt = """
    You are an expert audio forensic analyst. Analyze this spectrogram for signs of AI voice cloning or synthesis.
    Look for unnatural harmonics, lack of noise, or overly smooth frequency transitions.
    Is the audio Real (human) or Fake (AI-generated)?
    Respond ONLY with a JSON object in this format:
    {"decision": "Real/Fake", "confidence": 0.xx, "reason": "A brief explanation."}
    """
    
    spectrogram_path = create_spectrogram(audio_path)
    if not spectrogram_path:
        return {"error": "Could not create a spectrogram from the audio file."}

    try:
        # Using "with" ensures the image file is properly closed after use, fixing the error
        with Image.open(spectrogram_path) as img:
            response = model.generate_content([prompt, img])

        # Clean the response to extract only the JSON part
        json_text_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if not json_text_match:
            return {"error": "No valid JSON found in the model's response.", "raw_response": response.text}

        json_text = json_text_match.group(0)
        data = json.loads(json_text)
        
        return {
            "decision": data.get("decision", "Uncertain"),
            "confidence": data.get("confidence", 0.0),
            "reason": data.get("reason", "No reason provided.")
        }

    except FileNotFoundError:
        return {"error": "Spectrogram image not found."}
    except (json.JSONDecodeError, AttributeError):
        return {"error": "Failed to parse the model's JSON response.", "raw_response": response.text}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
    finally:
        # This cleanup step will now work because the file is no longer locked
        if os.path.exists(spectrogram_path):
            os.remove(spectrogram_path)