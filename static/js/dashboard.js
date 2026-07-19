/**
 * dashboard.js — ML Dashboard Logic
 * ====================================
 * Auto-refreshes stats and handles animated counters.
 */

// Animated number counter utility
function animateValue(element, target, suffix = '', duration = 2000) {
    if (!element) return;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = (target * eased);

        if (Number.isInteger(target)) {
            element.textContent = Math.round(current).toLocaleString() + suffix;
        } else {
            element.textContent = current.toFixed(2) + suffix;
        }

        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// Refresh dashboard stats
async function refreshDashboard() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.stats) {
            const totalEl = document.getElementById('dashTotal');
            const avgConfEl = document.getElementById('dashAvgConf');
            const avgTimeEl = document.getElementById('dashAvgTime');

            if (totalEl) totalEl.textContent = data.stats.total;
            if (avgConfEl) avgConfEl.textContent = data.stats.avg_confidence + '%';
            if (avgTimeEl) avgTimeEl.textContent = data.stats.avg_time + 's';
        }
    } catch (err) {
        console.error('Failed to refresh dashboard:', err);
    }
}
