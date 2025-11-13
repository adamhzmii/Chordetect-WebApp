from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple chord templates (major and minor chords)
CHORD_TEMPLATES = {
    'C': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    'C#': [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    'D': [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    'D#': [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    'E': [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    'F': [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    'F#': [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    'G': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    'G#': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    'A': [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    'A#': [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    'B': [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    # Minor chords
    'Cm': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    'Dm': [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    'Em': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    'Fm': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    'Gm': [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    'Am': [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
}

def detect_chord_from_chroma(chroma_vector):
    """Match chroma vector to closest chord template"""
    chroma_vector = np.array(chroma_vector)
    chroma_vector = chroma_vector / (np.sum(chroma_vector) + 1e-10)  # Normalize
    
    best_match = 'N'  # No chord
    best_score = 0
    
    for chord_name, template in CHORD_TEMPLATES.items():
        template = np.array(template)
        # Calculate correlation
        score = np.dot(chroma_vector, template)
        if score > best_score:
            best_score = score
            best_match = chord_name
    
    return best_match if best_score > 0.5 else 'N'

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/detect-chords', methods=['POST'])
def detect_chords():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Load audio file
        y, sr = librosa.load(filepath, sr=22050)
        
        # Extract chroma features (captures the 12 pitch classes)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=4096)
        
        # Detect chords every ~0.5 seconds
        times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr, hop_length=4096)
        
        chords = []
        prev_chord = None
        
        for i, time in enumerate(times):
            chord = detect_chord_from_chroma(chroma[:, i])
            
            # Only add if chord changed
            if chord != prev_chord:
                chords.append({
                    "time": float(time),
                    "chord": chord
                })
                prev_chord = chord
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "chords": chords,
            "duration": float(librosa.get_duration(y=y, sr=sr))
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)