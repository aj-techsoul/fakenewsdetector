/**
 * admin.js — Admin Portal Control actions
 * ========================================
 * Implements tab controls, suspend/activate API actions,
 * and asynchronous model retraining triggers.
 */

// ─── Control tab switcher ────────────────────────────────────────────────────

function switchAdminTab(tabId) {
    // Hide all contents
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    // De-activate all triggers
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    // Show target
    document.getElementById(tabId).classList.add('active');
    
    // Activate clicked button
    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(
        btn => btn.getAttribute('onclick').includes(tabId)
    );
    if (activeBtn) activeBtn.classList.add('active');
}

// ─── User Profile Actions ───────────────────────────────────────────────────

function toggleUserStatus(userId, action) {
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;

    fetch(`/admin/users/${userId}/action`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            
            // Update table status labels dynamically
            const badge = document.getElementById(`userStatusBadge-${userId}`);
            const suspendBtn = document.getElementById(`suspendBtn-${userId}`);
            const activateBtn = document.getElementById(`activateBtn-${userId}`);
            
            if (action === 'suspend') {
                badge.className = 'status-badge inactive';
                badge.textContent = 'Suspended';
                suspendBtn.style.display = 'none';
                activateBtn.style.display = 'inline-block';
            } else {
                badge.className = 'status-badge active';
                badge.textContent = 'Active';
                suspendBtn.style.display = 'inline-block';
                activateBtn.style.display = 'none';
            }
        } else {
            showToast(data.error || 'Failed to update user', 'danger');
        }
    })
    .catch(err => {
        console.error(err);
        showToast('System request failed.', 'danger');
    });
}

function deleteUserAccount(userId) {
    if (!confirm('Are you sure you want to delete this user? This will delete all predictions linked to this account.')) return;

    fetch(`/admin/users/${userId}/action`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'delete' })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            // Remove row from table
            const row = document.getElementById(`userRow-${userId}`);
            if (row) row.remove();
        } else {
            showToast(data.error || 'Failed to delete user', 'danger');
        }
    })
    .catch(err => {
        console.error(err);
        showToast('System request failed.', 'danger');
    });
}

// ─── Asynchronous ML Retraining ─────────────────────────────────────────────

function triggerModelRetrain() {
    if (!confirm('Trigger comparison training across all 5 models? This takes a few moments and updates the active predictor.')) return;

    const loader = document.getElementById('retrainLoader');
    const display = document.getElementById('metricsDisplay');
    const retrainBtn = document.getElementById('btnRetrain');

    if (loader) loader.classList.remove('hidden');
    if (display) display.classList.add('hidden');
    if (retrainBtn) retrainBtn.disabled = true;

    fetch('/admin/model/retrain', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (loader) loader.classList.add('hidden');
        if (retrainBtn) retrainBtn.disabled = false;

        if (data.success) {
            showToast('Model retraining complete!', 'success');
            // Reload page to refresh metrics graphs instantly
            location.reload();
        } else {
            if (display) display.classList.remove('hidden');
            showToast(data.error || 'Retraining failed.', 'danger');
        }
    })
    .catch(err => {
        if (loader) loader.classList.add('hidden');
        if (display) display.classList.remove('hidden');
        if (retrainBtn) retrainBtn.disabled = false;
        console.error(err);
        showToast('Server training request timed out or failed.', 'danger');
    });
}
