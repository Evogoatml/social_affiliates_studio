"""
Web Dashboard Server for Autonomous Influencer System
Provides Human-In-The-Loop (HITL) approval and monitoring interface
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import json
from threading import Thread

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
pending_approvals = []
approval_settings = {
    "require_content_approval": True,
    "require_strategy_approval": True,
    "require_posting_approval": True,
    "auto_approve_after_hours": 24,
    "notification_enabled": True
}

# Load approval settings
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

load_approval_settings()

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        # Get content stats
        pending_content = db.get_pending_content(limit=100)
        
        # Get viral content stats
        viral_stats = db.get_viral_content_stats(days=7)
        
        # Get recent posts
        scheduled_posts = db.get_scheduled_posts()
        
        # Get insights
        insights = db.get_content_insights(limit=10)
        
        # Get trending hashtags
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
    """Get content pending approval"""
    try:
        content = db.get_pending_content(limit=50)
        return jsonify(content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/viral-content')
def get_viral_content():
    """Get viral content data"""
    try:
        platform = request.args.get('platform')
        niche = request.args.get('niche')
        limit = int(request.args.get('limit', 20))
        
        viral_content = db.get_viral_content(
            platform=platform,
            niche=niche,
            limit=limit
        )
        return jsonify(viral_content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trending-hashtags')
def get_trending_hashtags_api():
    """Get trending hashtags"""
    try:
        platform = request.args.get('platform')
        limit = int(request.args.get('limit', 20))
        
        hashtags = db.get_trending_hashtags(platform=platform, limit=limit)
        return jsonify(hashtags)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/insights')
def get_insights():
    """Get AI insights"""
    try:
        platform = request.args.get('platform')
        niche = request.args.get('niche')
        limit = int(request.args.get('limit', 10))
        
        insights = db.get_content_insights(
            platform=platform,
            niche=niche,
            limit=limit
        )
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scheduled-posts')
def get_scheduled_posts():
    """Get scheduled posts"""
    try:
        posts = db.get_scheduled_posts()
        return jsonify(posts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/approval-settings', methods=['GET', 'POST'])
def approval_settings_api():
    """Get or update approval settings"""
    global approval_settings
    
    if request.method == 'GET':
        return jsonify(approval_settings)
    
    elif request.method == 'POST':
        try:
            new_settings = request.json
            approval_settings.update(new_settings)
            save_approval_settings()
            
            # Broadcast settings update
            socketio.emit('settings_updated', approval_settings)
            
            return jsonify({"success": True, "settings": approval_settings})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/pending-approvals')
def get_pending_approvals():
    """Get items pending approval"""
    return jsonify(pending_approvals)

@app.route('/api/approve/<approval_id>', methods=['POST'])
def approve_item(approval_id):
    """Approve a pending item"""
    global pending_approvals
    
    try:
        # Find the approval
        approval = next((a for a in pending_approvals if a['id'] == approval_id), None)
        
        if not approval:
            return jsonify({"error": "Approval not found"}), 404
        
        # Process approval
        approval['status'] = 'approved'
        approval['approved_at'] = datetime.now().isoformat()
        approval['approved_by'] = request.json.get('user', 'admin')
        
        # Execute the approved action
        result = execute_approval(approval)
        
        # Remove from pending
        pending_approvals = [a for a in pending_approvals if a['id'] != approval_id]
        
        # Broadcast update
        socketio.emit('approval_processed', {
            'id': approval_id,
            'status': 'approved',
            'result': result
        })
        
        return jsonify({"success": True, "result": result})
    
    except Exception as e:
        logger.error(f"Error approving item: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reject/<approval_id>', methods=['POST'])
def reject_item(approval_id):
    """Reject a pending item"""
    global pending_approvals
    
    try:
        # Find the approval
        approval = next((a for a in pending_approvals if a['id'] == approval_id), None)
        
        if not approval:
            return jsonify({"error": "Approval not found"}), 404
        
        # Process rejection
        approval['status'] = 'rejected'
        approval['rejected_at'] = datetime.now().isoformat()
        approval['rejected_by'] = request.json.get('user', 'admin')
        approval['rejection_reason'] = request.json.get('reason', '')
        
        # Remove from pending
        pending_approvals = [a for a in pending_approvals if a['id'] != approval_id]
        
        # Broadcast update
        socketio.emit('approval_processed', {
            'id': approval_id,
            'status': 'rejected'
        })
        
        return jsonify({"success": True})
    
    except Exception as e:
        logger.error(f"Error rejecting item: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/manual-post', methods=['POST'])
def create_manual_post():
    """Create a manual post"""
    try:
        data = request.json
        
        # Create content object
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
        
        # Save to database
        db.save_content(content)
        
        # If approval required, add to pending
        if approval_settings.get("require_content_approval"):
            request_approval("content", content, "Manual content creation")
        
        return jsonify({"success": True, "content": content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/status')
def get_system_status():
    """Get system operational status"""
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

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected to dashboard")
    emit('connected', {'data': 'Connected to dashboard'})

@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    emit('stats_update', get_stats().json)

# Helper functions
def request_approval(approval_type: str, item: dict, description: str):
    """Request approval for an action"""
    global pending_approvals
    
    approval = {
        "id": f"approval_{len(pending_approvals)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": approval_type,
        "item": item,
        "description": description,
        "requested_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    pending_approvals.append(approval)
    
    # Broadcast to all connected clients
    socketio.emit('new_approval_request', approval)
    
    logger.info(f"📋 Approval requested: {approval_type} - {description}")
    
    return approval['id']

def execute_approval(approval: dict):
    """Execute an approved action"""
    approval_type = approval['type']
    item = approval['item']
    
    try:
        if approval_type == "content":
            # Approve content for posting
            db.save_content({**item, "status": "approved"})
            return {"message": "Content approved for posting"}
        
        elif approval_type == "strategy":
            # Approve strategy change
            db.save_strategy(item)
            return {"message": "Strategy updated"}
        
        elif approval_type == "post":
            # Approve immediate posting
            # This would trigger the actual post
            return {"message": "Post scheduled"}
        
        else:
            return {"message": f"Approval executed for {approval_type}"}
    
    except Exception as e:
        logger.error(f"Error executing approval: {e}")
        return {"error": str(e)}

# Run server
def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run the dashboard server"""
    logger.info(f"🌐 Starting dashboard server on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_dashboard(debug=True)
