"""
models.py
---------
Defines the database tables using SQLAlchemy's ORM (Object Relational Mapper).

An ORM lets us work with Python classes instead of writing raw SQL. Each
class below becomes a table, and each attribute becomes a column.

Tables:
1. ModerationRecord - every piece of content that was checked, and the result
2. UserReport       - content that users manually reported/flagged
3. AuditLog         - a simple trail of every action taken, for compliance
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ModerationRecord(db.Model):
    """Stores the outcome of every automated moderation check."""

    __tablename__ = "moderation_records"

    id = db.Column(db.Integer, primary_key=True)

    # 'text' or 'image'
    content_type = db.Column(db.String(20), nullable=False)

    # The actual text, OR the filename/path for images
    content_reference = db.Column(db.Text, nullable=False)

    # A short preview so moderators don't need to open the full content
    preview = db.Column(db.String(300))

    # Decision made by the automated system: 'approved', 'flagged', 'rejected'
    decision = db.Column(db.String(20), nullable=False)

    # Confidence score from 0.0 to 1.0 (how sure the system is)
    confidence_score = db.Column(db.Float, default=0.0)

    # Comma-separated list of reasons/categories, e.g. "profanity,spam"
    categories = db.Column(db.String(200))

    # Has a human moderator reviewed this yet?
    human_reviewed = db.Column(db.Boolean, default=False)

    # Final decision after human review: 'approved', 'rejected', or None
    human_decision = db.Column(db.String(20), nullable=True)

    # Which platform/API client submitted this content
    source_platform = db.Column(db.String(100), default="default")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Convert this row into a plain dictionary (handy for JSON responses)."""
        return {
            "id": self.id,
            "content_type": self.content_type,
            "preview": self.preview,
            "decision": self.decision,
            "confidence_score": self.confidence_score,
            "categories": self.categories.split(",") if self.categories else [],
            "human_reviewed": self.human_reviewed,
            "human_decision": self.human_decision,
            "source_platform": self.source_platform,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class UserReport(db.Model):
    """Stores content that end-users have manually reported as inappropriate."""

    __tablename__ = "user_reports"

    id = db.Column(db.Integer, primary_key=True)
    moderation_record_id = db.Column(
        db.Integer, db.ForeignKey("moderation_records.id"), nullable=True
    )
    reported_content = db.Column(db.Text, nullable=False)
    reason = db.Column(db.String(300))
    reporter_id = db.Column(db.String(100), default="anonymous")
    status = db.Column(db.String(20), default="pending")  # pending/resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "moderation_record_id": self.moderation_record_id,
            "reported_content": self.reported_content,
            "reason": self.reason,
            "reporter_id": self.reporter_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """
    A simple, append-only trail of every important action taken by the
    system or a moderator. This exists purely for transparency/compliance,
    as required by the project brief.
    """

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    actor = db.Column(db.String(100), default="system")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "details": self.details,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
