"""
routes/dashboard.py
--------------------
Serves the human-moderator dashboard: a web page where a person can see
content the automated system flagged, and approve or reject it.

This maps to the "Provide a dashboard for human moderators to review
automated decisions" objective from the project brief.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import db, ModerationRecord, UserReport, AuditLog

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/dashboard")
def dashboard():
    """Main dashboard page: shows flagged content queue + recent activity."""
    flagged_items = (
        ModerationRecord.query.filter_by(decision="flagged", human_reviewed=False)
        .order_by(ModerationRecord.created_at.desc())
        .all()
    )
    recent_items = (
        ModerationRecord.query.order_by(ModerationRecord.created_at.desc()).limit(20).all()
    )
    pending_reports = UserReport.query.filter_by(status="pending").all()

    stats = {
        "total": ModerationRecord.query.count(),
        "approved": ModerationRecord.query.filter_by(decision="approved").count(),
        "flagged": ModerationRecord.query.filter_by(decision="flagged").count(),
        "rejected": ModerationRecord.query.filter_by(decision="rejected").count(),
    }

    return render_template(
        "dashboard.html",
        flagged_items=flagged_items,
        recent_items=recent_items,
        pending_reports=pending_reports,
        stats=stats,
    )


@dashboard_bp.route("/review/<int:record_id>/<string:decision>", methods=["POST"])
def review(record_id, decision):
    """A human moderator clicks 'Approve' or 'Reject' on a flagged item."""
    if decision not in ("approved", "rejected"):
        flash("Invalid decision.", "error")
        return redirect(url_for("dashboard.dashboard"))

    record = ModerationRecord.query.get_or_404(record_id)
    record.human_reviewed = True
    record.human_decision = decision
    record.reviewed_at = datetime.utcnow()
    db.session.commit()

    log = AuditLog(
        action="human_review",
        details=f"record_id={record_id} human_decision={decision}",
        actor="moderator",
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Record #{record_id} marked as {decision}.", "success")
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/reports/<int:report_id>/resolve", methods=["POST"])
def resolve_report(report_id):
    """Marks a user report as resolved."""
    report = UserReport.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()

    log = AuditLog(
        action="report_resolved", details=f"report_id={report_id}", actor="moderator"
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Report #{report_id} resolved.", "success")
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/audit-log")
def audit_log():
    """Shows the full audit trail (for transparency/compliance)."""
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return render_template("audit_log.html", logs=logs)


@dashboard_bp.route("/try-it")
def try_it():
    """A simple page to manually test text/image moderation from the browser."""
    return render_template("try_it.html")
