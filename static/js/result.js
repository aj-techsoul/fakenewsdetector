/**
 * result.js — Verification Result Page Controller
 * ==================================================
 * Renders static highlights viewer and probability pie charts
 * on saved prediction details reports.
 */

// Helper to escape HTML safely
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Highlights splicing renderer
function renderReportHighlights(text, highlights) {
    if (!highlights || highlights.length === 0) {
        return escapeHtml(text).replace(/\n/g, '<br>');
    }
    
    // Sort in descending order to avoid index shifts
    const sorted = [...highlights].sort((a, b) => b.start - a.start);
    let result = text;

    for (let h of sorted) {
        if (h.start >= 0 && h.end <= result.length) {
            const before = result.substring(0, h.start);
            const word = result.substring(h.start, h.end);
            const after = result.substring(h.end);

            result = before + `<span class="highlight highlight-${h.type}" title="${h.type.toUpperCase()}">${escapeHtml(word)}</span>` + after;
        }
    }

    return result.replace(/\n/g, '<br>');
}

// Initialize Result page assets
document.addEventListener('DOMContentLoaded', () => {
    const resultViewer = document.getElementById('resultTextViewer');
    
    // Render text with highlight offsets
    if (resultViewer && typeof RESULT_TEXT !== 'undefined') {
        // Re-generate local highlights from rules client-side to ensure rendering if DB list is empty
        let localHighlights = [];
        try {
            // Find Clickbait phrases
            const phrases = [
                "you won't believe", "shocking secret", "leaked report", "wake up people",
                "what they don't want", "big pharma", "deep state", "hidden agenda",
                "mainstream media", "censored truth", "miracle cure", "proven truth",
                "share this widely", "must read", "official cover-up", "mind-blowing"
            ];
            const text_lower = RESULT_TEXT.toLowerCase();
            for (let p of phrases) {
                let index = text_lower.indexOf(p);
                while (index !== -1) {
                    localHighlights.push({
                        start: index,
                        end: index + p.length,
                        type: 'clickbait'
                    });
                    index = text_lower.indexOf(p, index + 1);
                }
            }

            // Find Caps words
            const capsRegex = /\b[A-Z]{4,}\b/g;
            let match;
            while ((match = capsRegex.exec(RESULT_TEXT)) !== null) {
                if (!['NATO', 'USPS', 'OPEC', 'UNICEF', 'NASA', 'HTML', 'HTTP', 'JSON', 'WIFI'].includes(match[0])) {
                    localHighlights.push({
                        start: match.index,
                        end: match.index + match[0].length,
                        type: 'caps'
                    });
                }
            }

            // Double Punctuation
            const puncRegex = /[!?]{2,}/g;
            while ((match = puncRegex.exec(RESULT_TEXT)) !== null) {
                localHighlights.push({
                    start: match.index,
                    end: match.index + match[0].length,
                    type: 'punctuation'
                });
            }

            // Merge with database highlights if available, removing duplicates
            if (typeof RESULT_HIGHLIGHTS !== 'undefined' && RESULT_HIGHLIGHTS.length > 0) {
                localHighlights = [...localHighlights, ...RESULT_HIGHLIGHTS];
            }
        } catch(e) {
            console.error('Highlight processing error:', e);
        }

        resultViewer.innerHTML = renderReportHighlights(RESULT_TEXT, localHighlights);
    }

    // Chart.js render
    const ctx = document.getElementById('resultProbChart');
    if (ctx && typeof PROB_REAL !== 'undefined' && typeof PROB_FAKE !== 'undefined') {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Real Probability', 'Fake Probability'],
                datasets: [{
                    data: [PROB_REAL, PROB_FAKE],
                    backgroundColor: ['#00b894', '#e17055'],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 10,
                            font: { family: 'Inter', size: 11 },
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
});
