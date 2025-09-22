import os
import cv2
import shutil
import json
from moviepy.editor import VideoFileClip
from transformers import pipeline
import yt_dlp

# --- LAZY LOADING IMPLEMENTATION ---
# Initialize models as None. They will be loaded on first use.
face_detector = None
audio_detector = None
models_loaded = False

def load_models():
    """Loads the ML models only when needed."""
    global face_detector, audio_detector, models_loaded
    if not models_loaded:
        try:
            print("Loading video analysis models for the first time...")
            face_detector = pipeline("image-classification", model="prithivMLmods/Deep-Fake-Detector-v2-Model")
            audio_detector = pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection-V2")
            models_loaded = True
            print("Video analysis models loaded successfully.")
        except Exception as e:
            print(f"Error loading video models: {e}")
            # Ensure they remain None if loading fails
            face_detector = None
            audio_detector = None
    # If already loaded, this function does nothing.

def download_youtube_video(url, output_path="downloaded_video.mp4"):
    if "shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'format': 'mp4', 'outtmpl': output_path, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

def extract_frames(video_path, output_folder="temp_frames", fps=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with VideoFileClip(video_path) as clip:
        for i, frame in enumerate(clip.iter_frames(fps=fps)):
            frame_path = f"{output_folder}/frame_{i}.jpg"
            cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    return output_folder

def extract_audio(video_path, audio_path="temp_audio.wav"):
    with VideoFileClip(video_path) as clip:
        if clip.audio:
            clip.audio.write_audiofile(audio_path, logger=None)
            return audio_path
    return None

def check_face(frames_folder):
    load_models() # Ensure models are loaded before use
    if not face_detector:
        return "error", 0.0, "Face detection model is not available."

    scores, labels = [], []
    image_files = [f for f in os.listdir(frames_folder) if f.endswith(('.jpg', '.png'))]
    if not image_files:
        return "neutral", 0.0, "No frames to analyze"

    for frame_file in image_files:
        img_path = os.path.join(frames_folder, frame_file)
        preds = face_detector(img_path)
        best = max(preds, key=lambda x: x['score'])
        labels.append(best['label'])
        scores.append(best['score'])

    avg_score = sum(scores) / len(scores) if scores else 0
    majority_label = max(set(labels), key=labels.count) if labels else "neutral"
    reason = f"Face analysis determined the majority of frames as '{majority_label.upper()}'."
    return majority_label, avg_score, reason

def check_audio(audio_path):
    load_models() # Ensure models are loaded before use
    if not audio_detector:
        return "error", 0.0, "Audio detection model is not available."

    if not audio_path or not os.path.exists(audio_path):
        return "neutral", 0.0, "No audio track found in the video."
    preds = audio_detector(audio_path)
    best = max(preds, key=lambda x: x['score'])
    reason = f"Audio analysis classified the track as '{best['label'].upper()}'."
    return best['label'], best['score'], reason

def analyze_video_from_url(url):
    video_path = download_youtube_video(url)
    # The functions below will trigger model loading if needed
    frames_folder = extract_frames(video_path)
    audio_path = extract_audio(video_path)

    face_label, face_conf, face_reason = check_face(frames_folder)
    audio_label, audio_conf, audio_reason = check_audio(audio_path)

    shutil.rmtree(frames_folder)
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)
    if os.path.exists(video_path):
        os.remove(video_path)

    face_is_real = face_label.lower() == "real"
    audio_is_real = audio_label.lower() == "bonafide"
    overall_confidence = (face_conf + audio_conf) / 2 if audio_path else face_conf

    if face_is_real and audio_is_real:
        decision = "Real"
        final_reason = "Both visual and audio components appear authentic."
    # ... (rest of the logic is the same)
    elif not face_is_real and audio_is_real:
        decision = "Fake"
        final_reason = "Altered visual content (deepfake face) detected, but audio is authentic."
    elif face_is_real and not audio_is_real:
        decision = "Fake"
        final_reason = "Visuals appear authentic, but the audio is likely synthetic or altered."
    else:
        decision = "Fake"
        final_reason = "Both visual and audio components show signs of manipulation."

    return {
        "decision": decision,
        "overall_confidence": overall_confidence,
        "reason": final_reason,
        "details": {
            "face_analysis": {"result": face_label, "confidence": face_conf, "reason": face_reason},
            "audio_analysis": {"result": audio_label, "confidence": audio_conf, "reason": audio_reason},
        }
    }
