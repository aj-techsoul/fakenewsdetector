/**
 * history.js — Prediction History Page
 * ======================================
 * Handles fetching, rendering, searching, filtering, sorting,
 * and deleting prediction history entries.
 */

// ─── State ──────────────────────────────────────────────────────────────────

let currentSearch = '';
let currentFilter = 'all';
let currentSort = 'date_desc';

// ─── DOM Elements ───────────────────────────────────────────────────────────

const searchInput = document.getElementById('searchInput');
const filterSelect = document.getElementById('filterSelect');
const sortSelect = document.getElementById('sortSelect');
const historyList = document.getElementById('historyList');
const emptyState = document.getElementById('emptyState');

// ─── Fetch & Render ─────────────────────────────────────────────────────────

async function loadHistory() {
    try {
        const params = new URLSearchParams({
            search: currentSearch,
            filter: currentFilter,
            sort: currentSort,
            limit: 50,
            offset: 0
        });

        const response = await fetch(`/api/history?${params}`);
        const data = await response.json();

        renderHistory(data.predictions);
    } catch (err) {
        console.error('Failed to load history:', err);
        showToast('Failed to load history', 'error');
    }
}

function renderHistory(predictions) {
    if (!predictions || predictions.length === 0) {
        historyList.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    historyList.innerHTML = predictions.map(p => `
        <div class="glass-card history-item" onclick="window.location.href='/result/${p.id}'">
            <span class="history-prediction-badge ${p.prediction.toLowerCase()}">
                ${p.prediction}
            </span>
            <div class="history-details">
                <div class="history-preview">${escapeHtml(truncateText(p.text_preview, 120))}</div>
                <div class="history-meta">
                    <span><i class="fas fa-percentage"></i> ${p.confidence}%</span>
                    <span><i class="fas fa-clock"></i> ${formatDate(p.created_at)}</span>
                    <span><i class="fas fa-stopwatch"></i> ${p.prediction_time}s</span>
                </div>
            </div>
            <div class="history-actions">
                <button class="btn btn-icon btn-secondary" onclick="event.stopPropagation(); deletePrediction(${p.id})" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// ─── Event Listeners ────────────────────────────────────────────────────────

// Search with debounce
searchInput.addEventListener('input', debounce((e) => {
    currentSearch = e.target.value;
    loadHistory();
}, 300));

// Filter change
filterSelect.addEventListener('change', (e) => {
    currentFilter = e.target.value;
    loadHistory();
});

// Sort change
sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    loadHistory();
});

// ─── Delete Prediction ──────────────────────────────────────────────────────

async function deletePrediction(id) {
    if (!confirm('Are you sure you want to delete this prediction?')) return;

    try {
        const response = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showToast('Prediction deleted', 'success');
            loadHistory();
        } else {
            showToast('Failed to delete prediction', 'error');
        }
    } catch (err) {
        showToast('Error deleting prediction', 'error');
    }
}

// ─── Utility ────────────────────────────────────────────────────────────────

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Initialize ─────────────────────────────────────────────────────────────

loadHistory();
