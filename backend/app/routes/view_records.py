from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Record
from ..extensions import db

view_records_bp = Blueprint("view_records", __name__)

@view_records_bp.route("/records/view/<int:record_id>", methods=["GET", "DELETE"])
@jwt_required()
def get_record(record_id):
    user_id = int(get_jwt_identity())
    record = Record.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({"error": "Record not found"}), 404
    
    if request.method == "DELETE":
        db.session.delete(record)
        db.session.commit()
        return jsonify({"msg": "Record deleted."}), 200

    return jsonify({
        "id": record.id,
        "filename": record.filename,
        "transcript": record.transcript,
        "summary": record.summary,
        "created_at": record.created_at.isoformat()
    })


@view_records_bp.route("/records/view", methods=["GET"])
@jwt_required()
def get_all_records():
    user_id = int(get_jwt_identity())
    records = Record.query.filter_by(user_id=user_id).order_by(Record.created_at.desc()).all()

    if not records:
        return jsonify({"msg": "No records found."}), 200  # only for backend. Replace when you add the frontend.
    
    return jsonify([
        {
            "id": r.id,
            "filename": r.filename,
            "summary": r.summary,
            "created_at": r.created_at.isoformat()
        } for r in records
    ])
