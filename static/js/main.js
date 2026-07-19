/**
 * main.js — Main script for FakeGuard AI
 * ========================================
 * Implements sidebar toggling, live user notifications checks,
 * clear alerts, and global toast alerts.
 */

// ─── Sidebar responsive toggle ───────────────────────────────────────────────

const sidebarToggle = document.getElementById('sidebarToggle');
const appSidebar = document.getElementById('appSidebar');

if (sidebarToggle && appSidebar) {
    sidebarToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        appSidebar.classList.toggle('expanded');
    });

    // Close expanded sidebar when clicking outside on mobile viewports
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 992 && appSidebar.classList.contains('expanded')) {
            if (!appSidebar.contains(e.target) && e.target !== sidebarToggle) {
                appSidebar.classList.remove('expanded');
            }
        }
    });
}

// ─── Real-time user notification audits ──────────────────────────────────────

const bellBadge = document.getElementById('bellBadge');
const notifBellDropdown = document.getElementById('notifBellDropdown');
const notifDropdown = document.getElementById('notifDropdown');
const notifList = document.getElementById('notifList');
const clearNotifBtn = document.getElementById('clearNotifBtn');

function fetchNotifications() {
    if (!bellBadge) return; // Exit if not logged in
    
    fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
            const list = data.notifications || [];
            
            if (list.length > 0) {
                bellBadge.textContent = list.length;
                bellBadge.classList.remove('hidden');
                
                notifList.innerHTML = list.map(n => `
                    <div class="notif-dropdown-item notif-${n.type}">
                        <span class="title"><strong>${n.title}</strong></span>
                        <span class="body">${n.message}</span>
                        <span class="time font-sm">${formatDate(n.created_at)}</span>
                    </div>
                `).join('');
            } else {
                bellBadge.classList.add('hidden');
                notifList.innerHTML = '<p class="empty-notif text-muted">No new notifications</p>';
            }
        })
        .catch(err => console.error('Failed to audit notifications:', err));
}

if (notifBellDropdown && notifDropdown) {
    // Toggle dropdown visibility
    notifBellDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
        notifDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
        notifDropdown.classList.add('hidden');
    });
}

if (clearNotifBtn) {
    clearNotifBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fetch('/api/notifications/read', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    bellBadge.classList.add('hidden');
                    notifList.innerHTML = '<p class="empty-notif text-muted">No new notifications</p>';
                    showToast('All notifications cleared', 'success');
                }
            })
            .catch(err => console.error('Failed to clear notifications:', err));
    });
}

// ─── Dynamic Toast notifications helper ─────────────────────────────────────

function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: 'fas fa-check-circle',
        warning: 'fas fa-circle-exclamation',
        danger: 'fas fa-circle-xmark',
        info: 'fas fa-circle-info'
    };

    toast.innerHTML = `
        <i class="${icons[type] || icons.info}" style="margin-right: 10px;"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Fade out and remove
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// ─── Format helper utilities ────────────────────────────────────────────────

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait = 300) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Start audits on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchNotifications();
    // Poll notifications list every 30 seconds
    setInterval(fetchNotifications, 30000);
});
