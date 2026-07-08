"""
routes/api.py
-------------
This is the REST API that other platforms/apps would call to submit
content for moderation. This maps to the "Integrate with various content
platforms through APIs" requirement from the project brief.

Endpoints:
  POST /api/moderate/text     -> submit a text string for moderation
  POST /api/moderate/image    -> submit an image file for moderation
  POST /api/report            -> a user reports a piece of content
  GET  /api/records           -> list all moderation records (with filters)
  GET  /api/stats             -> summary statistics for the dashboard
"""

import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from models import db, ModerationRecord, UserReport, AuditLog
from moderation.text_moderator import analyze_text
from moderation.image_moderator import analyze_image

api_bp = Blueprint("api", __name__, url_prefix="/api")

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _log_action(action, details, actor="system"):
    entry = AuditLog(action=action, details=details, actor=actor)
    db.session.add(entry)
    db.session.commit()


@api_bp.route("/moderate/text", methods=["POST"])
def moderate_text():
    """
    Expects JSON: { "text": "...", "platform": "optional-name" }
    Returns the moderation decision immediately (real-time analysis).
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    platform = data.get("platform", "default")

    if not text:
        return jsonify({"error": "The 'text' field is required."}), 400

    threshold = current_app.config["TEXT_TOXICITY_THRESHOLD"]
    result = analyze_text(text, toxicity_threshold=threshold)

    record = ModerationRecord(
        content_type="text",
        content_reference=text,
        preview=text[:150],
        decision=result["decision"],
        confidence_score=result["confidence_score"],
        categories=",".join(result["categories"]),
        source_platform=platform,
    )
    db.session.add(record)
    db.session.commit()

    _log_action(
        "text_moderated",
        f"record_id={record.id} decision={result['decision']}",
    )

    return jsonify({"record_id": record.id, **result}), 200


@api_bp.route("/moderate/image", methods=["POST"])
def moderate_image():
    """
    Expects a multipart/form-data upload with field name 'image'.
    Optional form field: 'platform'.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided (field name must be 'image')."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    platform = request.form.get("platform", "default")

    # Save with a random name to avoid collisions/overwrites
    ext = os.path.splitext(file.filename)[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(save_path)

    size_limit = current_app.config["IMAGE_SIZE_FLAG_MB"]
    result = analyze_image(save_path, size_flag_mb=size_limit)

    record = ModerationRecord(
        content_type="image",
        content_reference=save_path,
        preview=file.filename,
        decision=result["decision"],
        confidence_score=result["confidence_score"],
        categories=",".join(result["categories"]),
        source_platform=platform,
    )
    db.session.add(record)
    db.session.commit()

    _log_action(
        "image_moderated",
        f"record_id={record.id} decision={result['decision']}",
    )

    return jsonify({"record_id": record.id, **result}), 200


@api_bp.route("/report", methods=["POST"])
def report_content():
    """
    Lets a user flag content that they believe is inappropriate.
    Expects JSON: { "content": "...", "reason": "...", "reporter_id": "optional",
                    "moderation_record_id": optional int }
    """
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    reason = data.get("reason", "").strip()

    if not content or not reason:
        return jsonify({"error": "'content' and 'reason' are required."}), 400

    report = UserReport(
        reported_content=content,
        reason=reason,
        reporter_id=data.get("reporter_id", "anonymous"),
        moderation_record_id=data.get("moderation_record_id"),
    )
    db.session.add(report)
    db.session.commit()

    _log_action("user_report_submitted", f"report_id={report.id}", actor=report.reporter_id)

    return jsonify({"message": "Report submitted. A moderator will review it.", "report_id": report.id}), 201


@api_bp.route("/records", methods=["GET"])
def list_records():
    """
    Returns moderation records, newest first.
    Optional query params: ?decision=flagged  ?content_type=text  ?limit=50
    """
    query = ModerationRecord.query

    decision = request.args.get("decision")
    if decision:
        query = query.filter_by(decision=decision)

    content_type = request.args.get("content_type")
    if content_type:
        query = query.filter_by(content_type=content_type)

    limit = int(request.args.get("limit", 100))
    records = query.order_by(ModerationRecord.created_at.desc()).limit(limit).all()

    return jsonify([r.to_dict() for r in records])


@api_bp.route("/stats", methods=["GET"])
def stats():
    """Returns summary numbers used by the dashboard's stat cards/charts."""
    total = ModerationRecord.query.count()
    approved = ModerationRecord.query.filter_by(decision="approved").count()
    flagged = ModerationRecord.query.filter_by(decision="flagged").count()
    rejected = ModerationRecord.query.filter_by(decision="rejected").count()
    pending_reports = UserReport.query.filter_by(status="pending").count()

    return jsonify(
        {
            "total": total,
            "approved": approved,
            "flagged": flagged,
            "rejected": rejected,
            "pending_reports": pending_reports,
        }
    )
