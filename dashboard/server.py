"""
Web Dashboard Server for Autonomous Influencer System
Provides Human-In-The-Loop (HITL) approval and monitoring interface
"""

import os
import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread, Timer
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from core.config import Config
from core.database import Database
from core.logger import setup_logger

logger = setup_logger(__name__)

app = Flask(__name__,
            template_folder='dashboard/templates',
            static_folder='dashboard/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'autonomous-influencer-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
config = Config()
db = Database()

# In-memory mirror of pending approvals (source of truth is the DB)
pending_approvals = []

approval_settings = {
    "require_content_approval": True,
    "require_strategy_approval": True,
    "require_posting_approval": True,
    "auto_approve_after_hours": 24,
    "notification_enabled": True
}


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------

def load_approval_settings():
    global approval_settings
    settings_file = Path("data/approval_settings.json")
    if settings_file.exists():
        with open(settings_file) as f:
            approval_settings.update(json.load(f))


def save_approval_settings():
    settings_file = Path("data/approval_settings.json")
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_file, "w") as f:
        json.dump(approval_settings, f, indent=2)


# ---------------------------------------------------------------------------
# Approval queue helpers
# ---------------------------------------------------------------------------

def _reload_pending_from_db():
    """Sync in-memory list from the DB (called on startup and after mutations)."""
    global pending_approvals
    pending_approvals = db.get_pending_approvals_db()


def request_approval(approval_type: str, item: dict, description: str) -> str:
    """Create an approval request, persist it, and broadcast to clients."""
    approval = {
        "id": str(uuid.uuid4()),
        "type": approval_type,
        "item": item,
        "description": description,
        "requested_at": datetime.now().isoformat(),
        "status": "pending",
    }

    db.save_approval(approval)
    _reload_pending_from_db()

    socketio.emit('new_approval_request', approval)
    logger.info(f"Approval requested: {approval_type} — {description}")

    # Schedule auto-approve timer
    hours = approval_settings.get("auto_approve_after_hours", 24)
    delay_seconds = hours * 3600
    t = Timer(delay_seconds, _auto_approve, args=[approval["id"]])
    t.daemon = True
    t.start()

    return approval["id"]


def _auto_approve(approval_id: str):
    """Auto-approve an item if it's still pending after the timeout."""
    approval = next((a for a in pending_approvals if a["id"] == approval_id), None)
    if approval and approval["status"] == "pending":
        logger.info(f"Auto-approving {approval_id} after timeout")
        _resolve_approval(approval_id, "approved", "auto-approve", None)


def _resolve_approval(approval_id: str, status: str, resolved_by: str, reason: str | None):
    """Mark approval resolved in DB, update memory, broadcast."""
    global pending_approvals
    now = datetime.now().isoformat()
    updates = {"status": status, "resolved_at": now, "resolved_by": resolved_by}
    if reason:
        updates["rejection_reason"] = reason
    db.update_approval(approval_id, updates)
    _reload_pending_from_db()
    socketio.emit('approval_processed', {"id": approval_id, "status": status})


def execute_approval(approval: dict) -> dict:
    """Execute side-effects for an approved action."""
    approval_type = approval['type']
    item = approval['item']
    try:
        if approval_type == "content":
            db.save_content({**item, "status": "approved"})
            return {"message": "Content approved for posting"}
        elif approval_type == "strategy":
            db.save_strategy(item)
            return {"message": "Strategy updated"}
        elif approval_type == "post":
            return {"message": "Post scheduled"}
        else:
            return {"message": f"Approval executed for {approval_type}"}
    except Exception as e:
        logger.error(f"Error executing approval: {e}")
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/stats')
def get_stats():
    try:
        pending_content = db.get_pending_content(limit=100)
        viral_stats = db.get_viral_content_stats(days=7)
        scheduled_posts = db.get_scheduled_posts()
        insights = db.get_content_insights(limit=10)
        trending_hashtags = db.get_trending_hashtags(limit=20)

        stats = {
            "content": {
                "pending": len(pending_content),
                "scheduled": len([p for p in scheduled_posts if not p.get('posted')]),
                "posted": len([p for p in scheduled_posts if p.get('posted')])
            },
            "viral": viral_stats,
            "insights": len(insights),
            "trending_hashtags": len(trending_hashtags),
            "pending_approvals": len(pending_approvals),
            "last_updated": datetime.now().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/pending-content')
def get_pending_content():
    try:
        content = db.get_pending_content(limit=50)
        return jsonify(content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/viral-content')
def get_viral_content():
    try:
        platform = request.args.get('platform')
        niche = request.args.get('niche')
        limit = int(request.args.get('limit', 20))
        viral_content = db.get_viral_content(platform=platform, niche=niche, limit=limit)
        return jsonify(viral_content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/trending-hashtags')
def get_trending_hashtags_api():
    try:
        platform = request.args.get('platform')
        limit = int(request.args.get('limit', 20))
        hashtags = db.get_trending_hashtags(platform=platform, limit=limit)
        return jsonify(hashtags)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/insights')
def get_insights():
    try:
        platform = request.args.get('platform')
        niche = request.args.get('niche')
        limit = int(request.args.get('limit', 10))
        insights = db.get_content_insights(platform=platform, niche=niche, limit=limit)
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/scheduled-posts')
def get_scheduled_posts():
    try:
        posts = db.get_scheduled_posts()
        return jsonify(posts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/approval-settings', methods=['GET', 'POST'])
def approval_settings_api():
    global approval_settings
    if request.method == 'GET':
        return jsonify(approval_settings)
    try:
        approval_settings.update(request.json)
        save_approval_settings()
        socketio.emit('settings_updated', approval_settings)
        return jsonify({"success": True, "settings": approval_settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pending-approvals')
def get_pending_approvals():
    return jsonify(pending_approvals)


@app.route('/api/approve/<approval_id>', methods=['POST'])
def approve_item(approval_id):
    try:
        approval = next((a for a in pending_approvals if a['id'] == approval_id), None)
        if not approval:
            return jsonify({"error": "Approval not found"}), 404

        result = execute_approval(approval)
        resolved_by = request.json.get('user', 'admin') if request.json else 'admin'
        _resolve_approval(approval_id, "approved", resolved_by, None)

        socketio.emit('approval_processed', {"id": approval_id, "status": "approved", "result": result})
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Error approving item: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reject/<approval_id>', methods=['POST'])
def reject_item(approval_id):
    try:
        approval = next((a for a in pending_approvals if a['id'] == approval_id), None)
        if not approval:
            return jsonify({"error": "Approval not found"}), 404

        body = request.json or {}
        resolved_by = body.get('user', 'admin')
        reason = body.get('reason', '')
        _resolve_approval(approval_id, "rejected", resolved_by, reason)

        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error rejecting item: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/request-approval', methods=['POST'])
def api_request_approval():
    """Called by the orchestrator to push items into the HITL queue."""
    try:
        data = request.json or {}
        approval_id = request_approval(
            approval_type=data.get('type', 'content'),
            item=data.get('item', {}),
            description=data.get('description', '')
        )
        return jsonify({"success": True, "approval_id": approval_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/manual-post', methods=['POST'])
def create_manual_post():
    try:
        data = request.json
        content = {
            "id": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": data.get("type", "image"),
            "caption": data["caption"],
            "hashtags": data.get("hashtags", []),
            "platform": data.get("platform", "instagram"),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "manual": True
        }
        db.save_content(content)

        if approval_settings.get("require_content_approval"):
            request_approval("content", content, "Manual content creation")

        return jsonify({"success": True, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/system/status')
def get_system_status():
    try:
        status = {
            "running": True,
            "database": "connected",
            "approval_mode": approval_settings.get("require_content_approval"),
            "pending_approvals": len(pending_approvals),
            "last_check": datetime.now().isoformat()
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recent-activity')
def get_recent_activity():
    try:
        activity = db.get_recent_activity(limit=20)
        return jsonify(activity)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# WebSocket events
# ---------------------------------------------------------------------------

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected to dashboard")
    emit('connected', {'data': 'Connected to dashboard'})


@socketio.on('request_update')
def handle_update_request():
    """Push a fresh stats payload to the requesting client."""
    try:
        pending_content = db.get_pending_content(limit=100)
        viral_stats = db.get_viral_content_stats(days=7)
        scheduled_posts = db.get_scheduled_posts()
        insights = db.get_content_insights(limit=10)
        trending_hashtags = db.get_trending_hashtags(limit=20)

        stats = {
            "content": {
                "pending": len(pending_content),
                "scheduled": len([p for p in scheduled_posts if not p.get('posted')]),
                "posted": len([p for p in scheduled_posts if p.get('posted')])
            },
            "viral": viral_stats,
            "insights": len(insights),
            "trending_hashtags": len(trending_hashtags),
            "pending_approvals": len(pending_approvals),
            "last_updated": datetime.now().isoformat()
        }
        emit('stats_update', stats)
    except Exception as e:
        logger.error(f"Error handling update request: {e}")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

load_approval_settings()
_reload_pending_from_db()


def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run the dashboard server"""
    logger.info(f"Starting dashboard server on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_dashboard(debug=True)
