# Veritas 🛡️

***"Latin for 'Truth', powered by AI"***

Veritas is a full-stack web application designed to combat digital misinformation. It leverages cutting-edge AI to analyze text, audio, images, and video content, helping users distinguish between authentic and AI-generated (deepfake) media.

---

## Features ✨

* **Multi-Modal Analysis** — Detects manipulation across different content types:

  * **Text:** Analyzes articles and messages for AI-written content.
  * **Audio:** Detects AI-cloned voices and synthetic audio.
  * **Image:** Scans images for signs of AI generation.
  * **Video:** Uncovers deepfake videos by analyzing both visual frames and audio tracks.

* **AI-Powered** — Built on Google Gemini 1.5 Flash for fast and accurate analysis.

* **Web Dashboard** — Intuitive UI for uploading content and viewing analysis reports with confidence scores.

* **Analysis History** — Saves all results locally for future reference.

---

## Tech Stack 💻

* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python, Flask, Flask-SQLAlchemy
* **AI/ML:** Google Gemini API
* **Multimedia Processing:** FFmpeg, MoviePy, Librosa, Pillow
* **Database:** SQLite

---

## Setup & Installation 🚀

### 1. Clone the Repository

```bash
git clone https://github.com/stlb57/veritas-project.git
cd veritas-project
```

### 2. Set Up the Backend

Navigate to the backend directory and create a virtual environment:

```bash
cd backend
python -m venv venv
```

Activate the environment:

* **Windows:**

  ```bash
  .\venv\Scripts\activate
  ```
* **macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `backend/` folder with the following:

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

Replace with your actual Google Gemini API key.

### 4. Install FFmpeg

Veritas relies on FFmpeg for audio/video analysis:

* Download from [FFmpeg builds](https://www.gyan.dev/ffmpeg/builds/).
* Extract to a location (e.g., `C:\ffmpeg`).
* Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your system PATH.

### 5. Run the Application

Start the backend server:

```bash
python app.py
```

Server runs at: `http://127.0.0.1:5000`

To launch the frontend, open `frontend/index.html` in your browser.

---

## How It Works ⚙️

1. User uploads content via the web UI.
2. The Flask backend routes the content to the appropriate analyzer module.
3. Media (text, audio, images, or video) is pre-processed — e.g., spectrograms for audio.
4. Gemini AI is used to analyze the content’s authenticity.
5. Results (with confidence scores) are stored in the SQLite database.
6. The analysis report is displayed to the user in the dashboard.

---

## License 📜

This project is released under the **MIT License**.
