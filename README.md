# Veritas 🛡️

**"Latin by 'Truth', powered by AI"**

Veritas is a full-stack web application designed to combat digital misinformation. It leverages cutting-edge AI to analyze text, audio, images, and video content, helping users distinguish between authentic and AI-generated (deepfake) media.

---

## Features ✨

* **Multi-Modal Analysis:** Detects manipulation in various media formats:
    * **Text:** Analyzes articles and messages for AI-written content.
    * **Audio:** Detects AI-cloned voices and synthetic audio.
    * **Image:** Scans images for signs of AI generation.
    * **Video:** Uncovers deepfake videos by analyzing both visual frames and audio tracks.
* **AI-Powered:** Utilizes the Google Gemini 1.5 Flash model for fast and accurate analysis.
* **Web Dashboard:** An intuitive user interface for uploading content and viewing clear, concise analysis reports with confidence scores.
* **Analysis History:** Automatically saves all analysis results to a local database for future reference.

---

## Tech Stack 💻

* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python, Flask, Flask-SQLAlchemy
* **AI/ML:** Google Gemini API
* **Multimedia Processing:** FFmpeg, MoviePy, Librosa, Pillow
* **Database:** SQLite

---

## Setup and Installation 🚀

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/stlb57/veritas-project.git](https://github.com/stlb57/veritas-project.git)
cd veritas-project
