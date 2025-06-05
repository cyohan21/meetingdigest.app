from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..utils.transcribe import transcribe_audio
from ..utils.summarize import summarize_transcript
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Record
from app.extensions import db
import os
from openai import OpenAIError

transcribe_bp = Blueprint("transcribe", __name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'm4a', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@transcribe_bp.route("/transcribe", methods=["POST"], endpoint="transcribe")
@jwt_required()
def upload_and_process():
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(filepath)

        try:
            transcript = transcribe_audio(filepath) # Transcribe
            summary = summarize_transcript(transcript) # Summarize
        except OpenAIError as e:
            return jsonify({"error": "OpenAI failed: " + str(e)}), 502
        except Exception as e:
            return jsonify({"error": "Unexpected error: " + str(e)}), 500

        # Save to DB
        new_record = Record(
            user_id=user_id,
            filename=filename,
            transcript=transcript,
            summary=summary
        )
        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            "record_id": new_record.id,
            "transcript": transcript,
            "summary": summary
        }), 200

    return jsonify({"error": "File type not allowed"}), 400