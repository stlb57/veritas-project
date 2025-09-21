import os
import cv2
import shutil
import json
from moviepy.editor import VideoFileClip # This line was also corrected
from transformers import pipeline

from video_analyzer import face_detector, audio_detector, extract_frames, extract_audio, check_face, check_audio

def analyze_video_from_file(video_path):
    if not face_detector or not audio_detector:
        raise RuntimeError("Video analysis models are not available.")

    frames_folder = extract_frames(video_path)
    audio_path = extract_audio(video_path)

    face_label, face_conf, face_reason = check_face(frames_folder)
    audio_label, audio_conf, audio_reason = check_audio(audio_path)

    if os.path.exists(frames_folder):
        shutil.rmtree(frames_folder)
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)

    face_is_real = face_label.lower() == "real"
    audio_is_real = audio_label.lower() == "bonafide"
    overall_confidence = (face_conf + audio_conf) / 2 if audio_path else face_conf

    if face_is_real and audio_is_real:
        decision = "Real"
        final_reason = "Both visual and audio components appear authentic."
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
