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
            showSection(this.dataset.section);
        });
    });
}

function showSection(section) {
    document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
    document.getElementById(`${section}-section`).style.display = 'block';
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    currentSection = section;
    loadSectionData(section);
}

// WebSocket
function initializeWebSocket() {
    socket.on('connected', () => console.log('Connected to server'));

    socket.on('new_approval_request', (approval) => {
        pendingApprovals.push(approval);
        updateApprovalsBadge();
        renderApprovals();
        showNotification('New approval request', 'warning');
    });

    socket.on('approval_processed', (data) => {
        pendingApprovals = pendingApprovals.filter(a => a.id !== data.id);
        updateApprovalsBadge();
        renderApprovals();
        showNotification(`Approval ${data.status}`, data.status === 'approved' ? 'success' : 'info');
        if (currentSection === 'dashboard') loadRecentActivity();
    });

    socket.on('stats_update', (data) => {
        stats = data;
        updateDashboard();
    });

    socket.on('settings_updated', () => showNotification('Settings saved', 'success'));
}

// Forms
function initializeForms() {
    document.getElementById('settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveSettings();
    });

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
    loadRecentActivity();
}

function refreshData() {
    loadData();
    if (currentSection !== 'dashboard') loadSectionData(currentSection);
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

async function loadRecentActivity() {
    try {
        const response = await fetch('/api/recent-activity');
        const activity = await response.json();
        renderRecentActivity(activity);
    } catch (error) {
        console.error('Error loading activity:', error);
    }
}

async function loadSectionData(section) {
    switch(section) {
        case 'content':   await loadContent(); break;
        case 'viral':     await loadViralContent(); await loadTrendingHashtags(); break;
        case 'schedule':  await loadSchedule(); break;
        case 'insights':  await loadInsights(); break;
    }
}

async function loadContent() {
    try {
        const response = await fetch('/api/pending-content');
        renderContent(await response.json());
    } catch (error) { console.error('Error loading content:', error); }
}

async function loadViralContent() {
    try {
        const response = await fetch('/api/viral-content?limit=10');
        renderViralContent(await response.json());
    } catch (error) { console.error('Error loading viral content:', error); }
}

async function loadTrendingHashtags() {
    try {
        const response = await fetch('/api/trending-hashtags?limit=20');
        renderTrendingHashtags(await response.json());
    } catch (error) { console.error('Error loading hashtags:', error); }
}

async function loadSchedule() {
    try {
        const response = await fetch('/api/scheduled-posts');
        renderSchedule(await response.json());
    } catch (error) { console.error('Error loading schedule:', error); }
}

async function loadInsights() {
    try {
        const response = await fetch('/api/insights?limit=20');
        renderInsights(await response.json());
    } catch (error) { console.error('Error loading insights:', error); }
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
    document.getElementById('pending-badge').innerHTML =
        `<span class="badge bg-warning">${count}</span> Pending Approvals`;
    document.getElementById('approvals-count').textContent = count;
}

function platformIcon(platform) {
    const icons = { instagram: 'fa-instagram', twitter: 'fa-twitter', tiktok: 'fa-tiktok' };
    const icon = icons[(platform || '').toLowerCase()] || 'fa-globe';
    return `<i class="fab ${icon}"></i>`;
}

function renderApprovals() {
    const container = document.getElementById('approvals-list');

    if (!pendingApprovals.length) {
        container.innerHTML = '<div class="alert alert-info"><i class="fas fa-check-circle me-2"></i>No pending approvals — all clear!</div>';
        return;
    }

    container.innerHTML = pendingApprovals.map(approval => {
        const item = approval.item || {};
        const requested = new Date(approval.requested_at).toLocaleString();

        // Build a human-readable preview of the item
        let preview = '';
        if (item.caption) {
            preview += `
                <div class="mb-2">
                    <span class="text-muted small fw-semibold">CAPTION</span>
                    <p class="mb-1">${escHtml(item.caption)}</p>
                </div>`;
        }
        if (item.hashtags && item.hashtags.length) {
            const tags = Array.isArray(item.hashtags) ? item.hashtags : JSON.parse(item.hashtags || '[]');
            preview += `
                <div class="mb-2">
                    <span class="text-muted small fw-semibold">HASHTAGS</span><br>
                    ${tags.map(t => `<span class="badge bg-info me-1">#${escHtml(t)}</span>`).join('')}
                </div>`;
        }
        if (item.platform) {
            preview += `
                <div class="mb-2">
                    <span class="text-muted small fw-semibold">PLATFORM</span>&nbsp;
                    ${platformIcon(item.platform)} ${escHtml(item.platform)}
                </div>`;
        }
        if (item.type) {
            preview += `
                <div class="mb-2">
                    <span class="text-muted small fw-semibold">TYPE</span>&nbsp;
                    <span class="badge bg-secondary">${escHtml(item.type)}</span>
                </div>`;
        }
        // Fall back to a collapsible JSON view for unknown item shapes
        if (!preview) {
            const colId = `raw-${approval.id}`;
            preview = `
                <a class="btn btn-sm btn-outline-secondary mb-2" data-bs-toggle="collapse" href="#${colId}">
                    Show raw data
                </a>
                <div class="collapse" id="${colId}">
                    <pre class="small">${escHtml(JSON.stringify(item, null, 2))}</pre>
                </div>`;
        }

        return `
            <div class="card mb-3 border-warning" id="approval-card-${approval.id}">
                <div class="card-header d-flex justify-content-between align-items-center bg-warning bg-opacity-10">
                    <div>
                        <span class="badge bg-warning text-dark me-2">${escHtml(approval.type.toUpperCase())}</span>
                        <strong>${escHtml(approval.description || '')}</strong>
                    </div>
                    <span class="badge bg-warning text-dark">Pending</span>
                </div>
                <div class="card-body">
                    ${preview}
                    <small class="text-muted"><i class="fas fa-clock me-1"></i>Requested: ${requested}</small>
                </div>
                <div class="card-footer d-flex gap-2">
                    <button class="btn btn-success btn-sm" onclick="approveItem('${approval.id}')">
                        <i class="fas fa-check me-1"></i>Approve
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="rejectItem('${approval.id}')">
                        <i class="fas fa-times me-1"></i>Reject
                    </button>
                </div>
            </div>`;
    }).join('');
}

function renderRecentActivity(activity) {
    const container = document.getElementById('recent-activity');
    if (!activity || !activity.length) {
        container.innerHTML = '<div class="text-muted text-center py-3">No recent activity</div>';
        return;
    }

    const statusBadge = (s) => {
        const map = { pending: 'warning', approved: 'success', rejected: 'danger' };
        return `<span class="badge bg-${map[s] || 'secondary'}">${s}</span>`;
    };

    container.innerHTML = activity.map(a => `
        <div class="list-group-item d-flex justify-content-between align-items-start py-2">
            <div>
                <span class="badge bg-secondary me-2">${escHtml(a.type || '')}</span>
                <span class="small">${escHtml(a.description || a.id)}</span>
            </div>
            <div class="text-end">
                ${statusBadge(a.status)}
                <br><small class="text-muted">${new Date(a.requested_at).toLocaleString()}</small>
            </div>
        </div>
    `).join('');
}

function renderContent(content) {
    const container = document.getElementById('content-list');
    if (!content.length) {
        container.innerHTML = '<div class="alert alert-info">No content available</div>';
        return;
    }
    container.innerHTML = '<div class="row">' + content.map(item => {
        let tags = [];
        try { tags = JSON.parse(item.hashtags || '[]'); } catch(_) {}
        return `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-header">
                        <span class="badge bg-primary">${escHtml(item.type)}</span>
                        <span class="badge bg-secondary">${escHtml(item.theme || 'General')}</span>
                    </div>
                    <div class="card-body">
                        <p><strong>Caption:</strong> ${escHtml(item.caption || 'No caption')}</p>
                        <p><strong>Hashtags:</strong> ${tags.map(t => `<span class="badge bg-info me-1">#${escHtml(t)}</span>`).join('')}</p>
                        <small class="text-muted">Created: ${new Date(item.created_at).toLocaleString()}</small>
                    </div>
                </div>
            </div>`;
    }).join('') + '</div>';
}

function renderViralContent(content) {
    const container = document.getElementById('viral-content-list');
    if (!content.length) {
        container.innerHTML = '<p class="text-muted">No viral content data</p>';
        return;
    }
    container.innerHTML = content.slice(0, 5).map(item => `
        <div class="mb-3 p-2 border-bottom">
            <div class="d-flex justify-content-between">
                <strong>${escHtml(item.platform.toUpperCase())}</strong>
                <span class="badge bg-danger">${item.engagement_rate}% engagement</span>
            </div>
            <p class="small mb-1">${escHtml((item.caption || '').substring(0, 100))}…</p>
            <div class="small text-muted">
                <i class="fas fa-heart"></i> ${item.likes || 0}
                <i class="fas fa-comment ms-2"></i> ${item.comments || 0}
                <i class="fas fa-eye ms-2"></i> ${item.views || 0}
            </div>
        </div>`).join('');
}

function renderTrendingHashtags(hashtags) {
    const container = document.getElementById('trending-hashtags');
    if (!hashtags.length) {
        container.innerHTML = '<p class="text-muted">No trending hashtags</p>';
        return;
    }
    container.innerHTML = hashtags.map(tag => `
        <span class="badge bg-info me-2 mb-2">
            #${escHtml(tag.hashtag)}
            <span class="badge bg-light text-dark">${tag.usage_count}</span>
        </span>`).join('');
}

function renderSchedule(schedule) {
    const container = document.getElementById('schedule-list');
    if (!schedule.length) {
        container.innerHTML = '<div class="alert alert-info">No scheduled posts</div>';
        return;
    }
    container.innerHTML = '<div class="list-group">' + schedule.map(post => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between">
                <h6>${escHtml(post.platform.toUpperCase())}</h6>
                <span class="badge ${post.posted ? 'bg-success' : 'bg-warning'}">${escHtml(post.status)}</span>
            </div>
            <p class="small">Scheduled: ${new Date(post.scheduled_time).toLocaleString()}</p>
            ${post.posted ? `<p class="small text-success">Posted: ${new Date(post.posted_time).toLocaleString()}</p>` : ''}
        </div>`).join('') + '</div>';
}

function renderInsights(insights) {
    const container = document.getElementById('insights-list');
    if (!insights.length) {
        container.innerHTML = '<div class="alert alert-info">No insights available</div>';
        return;
    }
    container.innerHTML = insights.map(insight => `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between">
                <strong>${escHtml(insight.insight_type.toUpperCase())}</strong>
                <span class="badge bg-info">${Math.round(insight.confidence_score * 100)}% confidence</span>
            </div>
            <div class="card-body">
                <p><strong>Pattern:</strong> ${escHtml(insight.pattern_description || '')}</p>
                <div class="alert alert-success">
                    <i class="fas fa-lightbulb"></i> <strong>Recommendation:</strong> ${escHtml(insight.recommendation || '')}
                </div>
                <small class="text-muted">${escHtml(insight.platform || 'All platforms')} | ${escHtml(insight.niche || 'All niches')}</small>
            </div>
        </div>`).join('');
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
            document.getElementById(`approval-card-${approvalId}`)?.remove();
            showNotification('Item approved', 'success');
            loadRecentActivity();
        } else {
            showNotification('Error approving item', 'danger');
        }
    } catch (error) {
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
            document.getElementById(`approval-card-${approvalId}`)?.remove();
            showNotification('Item rejected', 'info');
            loadRecentActivity();
        } else {
            showNotification('Error rejecting item', 'danger');
        }
    } catch (error) {
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
        showNotification(result.success ? 'Settings saved' : 'Error saving settings',
                         result.success ? 'success' : 'danger');
    } catch (error) {
        showNotification('Error saving settings', 'danger');
    }
}

async function createContent() {
    const data = {
        type: document.getElementById('content-type').value,
        platform: document.getElementById('content-platform').value,
        caption: document.getElementById('content-caption').value,
        hashtags: document.getElementById('content-hashtags').value.split(',').map(t => t.trim()).filter(Boolean)
    };
    try {
        const response = await fetch('/api/manual-post', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            showNotification('Content created', 'success');
            document.getElementById('create-content-form').reset();
            bootstrap.Modal.getInstance(document.getElementById('createContentModal')).hide();
            loadContent();
            loadApprovals();
        } else {
            showNotification('Error creating content', 'danger');
        }
    } catch (error) {
        showNotification('Error creating content', 'danger');
    }
}

function triggerViralScrape() {
    showNotification('Viral scrape triggered — this may take a few minutes', 'info');
}

// Utilities
function escHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3 shadow`;
    toast.style.zIndex = 9999;
    toast.innerHTML = `<i class="fas fa-bell me-2"></i>${escHtml(message)}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}
