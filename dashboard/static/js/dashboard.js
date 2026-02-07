// Dashboard JavaScript
const socket = io();

// State
let currentSection = 'dashboard';
let stats = {};
let pendingApprovals = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeWebSocket();
    initializeForms();
    loadData();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshData, 30000);
});

// Navigation
function initializeNavigation() {
    document.querySelectorAll('[data-section]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            showSection(section);
        });
    });
}

function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(s => {
        s.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(`${section}-section`).style.display = 'block';
    
    // Update active nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    
    currentSection = section;
    
    // Load section data
    loadSectionData(section);
}

// WebSocket
function initializeWebSocket() {
    socket.on('connected', (data) => {
        console.log('Connected to server:', data);
    });
    
    socket.on('new_approval_request', (approval) => {
        console.log('New approval request:', approval);
        pendingApprovals.push(approval);
        updateApprovalsBadge();
        loadApprovals();
        showNotification('New approval request', 'warning');
    });
    
    socket.on('approval_processed', (data) => {
        console.log('Approval processed:', data);
        loadApprovals();
        showNotification(`Approval ${data.status}`, 'success');
    });
    
    socket.on('stats_update', (data) => {
        stats = data;
        updateDashboard();
    });
    
    socket.on('settings_updated', (settings) => {
        console.log('Settings updated:', settings);
        showNotification('Settings saved', 'success');
    });
}

// Forms
function initializeForms() {
    // Settings form
    document.getElementById('settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveSettings();
    });
    
    // Create content form
    document.getElementById('create-content-form').addEventListener('submit', function(e) {
        e.preventDefault();
        createContent();
    });
}

// Data Loading
function loadData() {
    loadStats();
    loadApprovals();
    loadSettings();
}

function refreshData() {
    console.log('Refreshing data...');
    loadData();
    if (currentSection !== 'dashboard') {
        loadSectionData(currentSection);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        stats = await response.json();
        updateDashboard();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadApprovals() {
    try {
        const response = await fetch('/api/pending-approvals');
        pendingApprovals = await response.json();
        updateApprovalsBadge();
        renderApprovals();
    } catch (error) {
        console.error('Error loading approvals:', error);
    }
}

async function loadSettings() {
    try {
        const response = await fetch('/api/approval-settings');
        const settings = await response.json();
        
        document.getElementById('require-content-approval').checked = settings.require_content_approval;
        document.getElementById('require-strategy-approval').checked = settings.require_strategy_approval;
        document.getElementById('require-posting-approval').checked = settings.require_posting_approval;
        document.getElementById('auto-approve-hours').value = settings.auto_approve_after_hours;
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function loadSectionData(section) {
    switch(section) {
        case 'content':
            await loadContent();
            break;
        case 'viral':
            await loadViralContent();
            await loadTrendingHashtags();
            break;
        case 'schedule':
            await loadSchedule();
            break;
        case 'insights':
            await loadInsights();
            break;
    }
}

async function loadContent() {
    try {
        const response = await fetch('/api/pending-content');
        const content = await response.json();
        renderContent(content);
    } catch (error) {
        console.error('Error loading content:', error);
    }
}

async function loadViralContent() {
    try {
        const response = await fetch('/api/viral-content?limit=10');
        const viralContent = await response.json();
        renderViralContent(viralContent);
    } catch (error) {
        console.error('Error loading viral content:', error);
    }
}

async function loadTrendingHashtags() {
    try {
        const response = await fetch('/api/trending-hashtags?limit=20');
        const hashtags = await response.json();
        renderTrendingHashtags(hashtags);
    } catch (error) {
        console.error('Error loading hashtags:', error);
    }
}

async function loadSchedule() {
    try {
        const response = await fetch('/api/scheduled-posts');
        const schedule = await response.json();
        renderSchedule(schedule);
    } catch (error) {
        console.error('Error loading schedule:', error);
    }
}

async function loadInsights() {
    try {
        const response = await fetch('/api/insights?limit=20');
        const insights = await response.json();
        renderInsights(insights);
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Rendering
function updateDashboard() {
    if (stats.content) {
        document.getElementById('stat-pending').textContent = stats.content.pending || 0;
        document.getElementById('stat-scheduled').textContent = stats.content.scheduled || 0;
        document.getElementById('stat-posted').textContent = stats.content.posted || 0;
    }
    document.getElementById('stat-approvals').textContent = stats.pending_approvals || 0;
}

function updateApprovalsBadge() {
    const count = pendingApprovals.length;
    document.getElementById('pending-badge').innerHTML = `<span class="badge bg-warning">${count}</span> Pending Approvals`;
    document.getElementById('approvals-count').textContent = count;
}

function renderApprovals() {
    const container = document.getElementById('approvals-list');
    
    if (pendingApprovals.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No pending approvals</div>';
        return;
    }
    
    container.innerHTML = pendingApprovals.map(approval => `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between">
                <strong>${approval.type.toUpperCase()}</strong>
                <span class="badge bg-warning">Pending</span>
            </div>
            <div class="card-body">
                <p>${approval.description}</p>
                <div class="alert alert-light">
                    <pre>${JSON.stringify(approval.item, null, 2)}</pre>
                </div>
                <small class="text-muted">Requested: ${new Date(approval.requested_at).toLocaleString()}</small>
            </div>
            <div class="card-footer">
                <button class="btn btn-success btn-sm" onclick="approveItem('${approval.id}')">
                    <i class="fas fa-check"></i> Approve
                </button>
                <button class="btn btn-danger btn-sm" onclick="rejectItem('${approval.id}')">
                    <i class="fas fa-times"></i> Reject
                </button>
            </div>
        </div>
    `).join('');
}

function renderContent(content) {
    const container = document.getElementById('content-list');
    
    if (content.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No content available</div>';
        return;
    }
    
    container.innerHTML = '<div class="row">' + content.map(item => `
        <div class="col-md-6 mb-3">
            <div class="card">
                <div class="card-header">
                    <span class="badge bg-primary">${item.type}</span>
                    <span class="badge bg-secondary">${item.theme || 'General'}</span>
                </div>
                <div class="card-body">
                    <p><strong>Caption:</strong> ${item.caption || 'No caption'}</p>
                    <p><strong>Hashtags:</strong> ${JSON.parse(item.hashtags || '[]').join(' ')}</p>
                    <small class="text-muted">Created: ${new Date(item.created_at).toLocaleString()}</small>
                </div>
            </div>
        </div>
    `).join('') + '</div>';
}

function renderViralContent(content) {
    const container = document.getElementById('viral-content-list');
    
    if (content.length === 0) {
        container.innerHTML = '<p class="text-muted">No viral content data</p>';
        return;
    }
    
    container.innerHTML = content.slice(0, 5).map(item => `
        <div class="mb-3 p-2 border-bottom">
            <div class="d-flex justify-content-between">
                <strong>${item.platform.toUpperCase()}</strong>
                <span class="badge bg-danger">${item.engagement_rate}% engagement</span>
            </div>
            <p class="small mb-1">${(item.caption || '').substring(0, 100)}...</p>
            <div class="small text-muted">
                <i class="fas fa-heart"></i> ${item.likes || 0}
                <i class="fas fa-comment ms-2"></i> ${item.comments || 0}
                <i class="fas fa-eye ms-2"></i> ${item.views || 0}
            </div>
        </div>
    `).join('');
}

function renderTrendingHashtags(hashtags) {
    const container = document.getElementById('trending-hashtags');
    
    if (hashtags.length === 0) {
        container.innerHTML = '<p class="text-muted">No trending hashtags</p>';
        return;
    }
    
    container.innerHTML = hashtags.map(tag => `
        <span class="badge bg-info me-2 mb-2">
            #${tag.hashtag} 
            <span class="badge bg-light text-dark">${tag.usage_count}</span>
        </span>
    `).join('');
}

function renderSchedule(schedule) {
    const container = document.getElementById('schedule-list');
    
    if (schedule.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No scheduled posts</div>';
        return;
    }
    
    container.innerHTML = '<div class="list-group">' + schedule.map(post => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between">
                <h6>${post.platform.toUpperCase()}</h6>
                <span class="badge ${post.posted ? 'bg-success' : 'bg-warning'}">
                    ${post.status}
                </span>
            </div>
            <p class="small">Scheduled: ${new Date(post.scheduled_time).toLocaleString()}</p>
            ${post.posted ? `<p class="small text-success">Posted: ${new Date(post.posted_time).toLocaleString()}</p>` : ''}
        </div>
    `).join('') + '</div>';
}

function renderInsights(insights) {
    const container = document.getElementById('insights-list');
    
    if (insights.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No insights available</div>';
        return;
    }
    
    container.innerHTML = insights.map(insight => `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between">
                <strong>${insight.insight_type.toUpperCase()}</strong>
                <span class="badge bg-info">${Math.round(insight.confidence_score * 100)}% confidence</span>
            </div>
            <div class="card-body">
                <p><strong>Pattern:</strong> ${insight.pattern_description}</p>
                <div class="alert alert-success">
                    <i class="fas fa-lightbulb"></i> <strong>Recommendation:</strong> ${insight.recommendation}
                </div>
                <small class="text-muted">${insight.platform || 'All platforms'} | ${insight.niche || 'All niches'}</small>
            </div>
        </div>
    `).join('');
}

// Actions
async function approveItem(approvalId) {
    if (!confirm('Approve this item?')) return;
    
    try {
        const response = await fetch(`/api/approve/${approvalId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user: 'admin'})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Item approved successfully', 'success');
            loadApprovals();
        } else {
            showNotification('Error approving item', 'danger');
        }
    } catch (error) {
        console.error('Error approving:', error);
        showNotification('Error approving item', 'danger');
    }
}

async function rejectItem(approvalId) {
    const reason = prompt('Rejection reason (optional):');
    
    try {
        const response = await fetch(`/api/reject/${approvalId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user: 'admin', reason})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Item rejected', 'info');
            loadApprovals();
        } else {
            showNotification('Error rejecting item', 'danger');
        }
    } catch (error) {
        console.error('Error rejecting:', error);
        showNotification('Error rejecting item', 'danger');
    }
}

async function saveSettings() {
    const settings = {
        require_content_approval: document.getElementById('require-content-approval').checked,
        require_strategy_approval: document.getElementById('require-strategy-approval').checked,
        require_posting_approval: document.getElementById('require-posting-approval').checked,
        auto_approve_after_hours: parseInt(document.getElementById('auto-approve-hours').value)
    };
    
    try {
        const response = await fetch('/api/approval-settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(settings)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Settings saved successfully', 'success');
        } else {
            showNotification('Error saving settings', 'danger');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('Error saving settings', 'danger');
    }
}

async function createContent() {
    const data = {
        type: document.getElementById('content-type').value,
        platform: document.getElementById('content-platform').value,
        caption: document.getElementById('content-caption').value,
        hashtags: document.getElementById('content-hashtags').value.split(',').map(t => t.trim())
    };
    
    try {
        const response = await fetch('/api/manual-post', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Content created successfully', 'success');
            document.getElementById('create-content-form').reset();
            bootstrap.Modal.getInstance(document.getElementById('createContentModal')).hide();
            loadContent();
        } else {
            showNotification('Error creating content', 'danger');
        }
    } catch (error) {
        console.error('Error creating content:', error);
        showNotification('Error creating content', 'danger');
    }
}

function triggerViralScrape() {
    showNotification('Viral scrape triggered - this may take a few minutes', 'info');
    // This would trigger a background scrape
}

// Utilities
function showNotification(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = 9999;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}
