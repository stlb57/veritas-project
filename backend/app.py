import os
import shutil
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

print("--- Starting Server Initialization ---")

# --- Import all analyzer functions ---
from image_analyzer import analyze_image_content
from text_analyzer import analyze_text_content
from audio_analyzer import analyze_audio_content
from video_analyzer import analyze_video_from_url
from video_analyzer_local import analyze_video_from_file

# --- App and CORS Configuration ---
app = Flask(__name__)
# --- THIS IS THE CORRECTED LINE ---
CORS(app, origins="https://veritas-project.netlify.app", supports_credentials=True)

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'veritas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Uploads Folder Configuration ---
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database Model ---
class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_type = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'result': self.result,
            'confidence': self.confidence,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

# --- API Routes ---

@app.route('/analyze/text', methods=['POST'])
def handle_text_analysis():
    data = request.json
    content = data.get('text') or data.get('url')
    if not content:
        return jsonify({"error": "No text or URL provided"}), 400

    try:
        result = analyze_text_content(content)
        if 'error' not in result:
            analysis_entry = Analysis(analysis_type='Text', result=result['decision'], confidence=result['confidence'])
            db.session.add(analysis_entry)
            db.session.commit()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze/image', methods=['POST'])
def handle_image_analysis():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(filepath)
        result = analyze_image_content(filepath)
        
        if 'error' not in result:
            analysis_entry = Analysis(analysis_type='Image', result=result['decision'], confidence=result['confidence'])
            db.session.add(analysis_entry)
            db.session.commit()
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/analyze/audio', methods=['POST'])
def handle_audio_analysis():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(filepath)
        result = analyze_audio_content(filepath)
        
        if 'error' not in result:
            analysis_entry = Analysis(analysis_type='Audio', result=result['decision'], confidence=result['confidence'])
            db.session.add(analysis_entry)
            db.session.commit()

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/analyze/video-url', methods=['POST'])
def handle_video_url_analysis():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        result = analyze_video_from_url(url)
        if 'error' not in result:
            analysis_entry = Analysis(
                analysis_type='Video (URL)',
                result=result['decision'],
                confidence=result['overall_confidence']
            )
            db.session.add(analysis_entry)
            db.session.commit()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze/video-file', methods=['POST'])
def handle_video_file_analysis():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(filepath)
        result = analyze_video_from_file(filepath)
        
        if 'error' not in result:
            analysis_entry = Analysis(
                analysis_type='Video (File)',
                result=result['decision'],
                confidence=result['overall_confidence']
            )
            db.session.add(analysis_entry)
            db.session.commit()

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists('temp_frames'):
            shutil.rmtree('temp_frames')
        if os.path.exists('temp_audio.wav'):
            os.remove('temp_audio.wav')

@app.route('/history', methods=['GET'])
def get_history():
    analyses = Analysis.query.order_by(Analysis.timestamp.desc()).all()
    return jsonify([a.to_dict() for a in analyses])

@app.route('/stats', methods=['GET'])
def get_stats():
    total_analyses = Analysis.query.count()
    real_analyses = Analysis.query.filter(Analysis.result.ilike('%real%')).all()
    avg_confidence = 0.94 # Default value
    if real_analyses:
        avg_confidence = sum(a.confidence for a in real_analyses) / len(real_analyses)
    
    return jsonify({
        "totalAnalyses": total_analyses,
        "accuracyRate": avg_confidence
    })

# --- Run the App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
