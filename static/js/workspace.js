/**
 * workspace.js — Verification Workspace Controller
 * ===================================================
 * Coordinates live counters, text editor adjustments,
 * AJAX scans, skeleton loaders, and results visualization.
 */

// ─── DOM Elements ───────────────────────────────────────────────────────────

const articleEditor = document.getElementById('articleEditor');
const articleViewer = document.getElementById('articleViewer');
const charCount = document.getElementById('charCount');
const wordCount = document.getElementById('wordCount');

const btnPaste = document.getElementById('btnPaste');
const btnClear = document.getElementById('btnClear');
const btnSampleReal = document.getElementById('btnSampleReal');
const btnSampleFake = document.getElementById('btnSampleFake');
const btnVerify = document.getElementById('btnVerify');

const outputPlaceholder = document.getElementById('outputPlaceholder');
const skeletonLoader = document.getElementById('skeletonLoader');
const resultDetails = document.getElementById('resultDetails');
const errorBanner = document.getElementById('errorBanner');

let probDoughnutChart = null;

// ─── Counters live updater ──────────────────────────────────────────────────

function updateEditorCounters() {
    const txt = articleEditor.value;
    charCount.textContent = txt.length.toLocaleString();
    
    const words = txt.trim().split(/\s+/).filter(w => w.length > 0);
    wordCount.textContent = words.length.toLocaleString();
}

if (articleEditor) {
    articleEditor.addEventListener('input', updateEditorCounters);
}

// ─── Control Handlers ───────────────────────────────────────────────────────

if (btnClear) {
    btnClear.addEventListener('click', () => {
        articleEditor.value = '';
        articleEditor.classList.remove('hidden');
        articleViewer.classList.add('hidden');
        updateEditorCounters();
        hideError();
        resetResultPanels();
    });
}

if (btnPaste) {
    btnPaste.addEventListener('click', async () => {
        try {
            const clipText = await navigator.clipboard.readText();
            articleEditor.value = clipText;
            articleEditor.classList.remove('hidden');
            articleViewer.classList.add('hidden');
            updateEditorCounters();
            hideError();
            resetResultPanels();
            showToast('Text pasted from clipboard', 'success');
        } catch (e) {
            showToast('Unable to read clipboard. Please paste manually.', 'warning');
        }
    });
}

if (btnSampleReal) {
    btnSampleReal.addEventListener('click', () => {
        articleEditor.value = SAMPLE_REAL_DATA;
        articleEditor.classList.remove('hidden');
        articleViewer.classList.add('hidden');
        updateEditorCounters();
        hideError();
        resetResultPanels();
        showToast('Sample Real news loaded', 'success');
    });
}

if (btnSampleFake) {
    btnSampleFake.addEventListener('click', () => {
        articleEditor.value = SAMPLE_FAKE_DATA;
        articleEditor.classList.remove('hidden');
        articleViewer.classList.add('hidden');
        updateEditorCounters();
        hideError();
        resetResultPanels();
        showToast('Sample Fake news loaded', 'info');
    });
}

// ─── Error Handling ─────────────────────────────────────────────────────────

function showError(msg) {
    if (errorBanner) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove('hidden');
    }
}

function hideError() {
    if (errorBanner) {
        errorBanner.classList.add('hidden');
    }
}

function resetResultPanels() {
    outputPlaceholder.classList.remove('hidden');
    resultDetails.classList.add('hidden');
}

// ─── Highlights Parser ──────────────────────────────────────────────────────

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

function renderHighlightsMarkup(text, highlights) {
    // Sort in descending order to avoid index shifts during splice inserts
    const sorted = [...highlights].sort((a, b) => b.start - a.start);
    let result = text;
    
    for (let h of sorted) {
        if (h.start >= 0 && h.end <= result.length) {
            const before = result.substring(0, h.start);
            const word = result.substring(h.start, h.end);
            const after = result.substring(h.end);
            
            result = before + `<span class="highlight highlight-${h.type}" title="${h.type.toUpperCase()}: ${escapeHtml(word)}">${escapeHtml(word)}</span>` + after;
        }
    }
    
    return result.replace(/\n/g, '<br>');
}

// ─── Execute Verification AJAX ──────────────────────────────────────────────

if (btnVerify) {
    btnVerify.addEventListener('click', () => {
        const textVal = articleEditor.value.trim();
        
        if (!textVal || textVal.length < 30) {
            showError('Please paste at least 30 characters for verification analysis.');
            return;
        }
        
        hideError();
        outputPlaceholder.classList.add('hidden');
        resultDetails.classList.add('hidden');
        skeletonLoader.classList.remove('hidden');
        
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: textVal })
        })
        .then(res => {
            if (!res.ok) {
                return res.json().then(data => { throw new Error(data.error || 'Server prediction error') });
            }
            return res.json();
        })
        .then(data => {
            skeletonLoader.classList.add('hidden');
            displayScanResults(data, textVal);
        })
        .catch(err => {
            skeletonLoader.classList.add('hidden');
            outputPlaceholder.classList.remove('hidden');
            showError(err.message || 'Verification pipeline encountered a system error.');
            showToast('Verification failed', 'danger');
        });
    });
}

// ─── Display Scan Results ───────────────────────────────────────────────────

function displayScanResults(res, originalText) {
    // Show details wrapper
    resultDetails.classList.remove('hidden');
    
    // Verdict Badges
    const badge = document.getElementById('verdictBadge');
    badge.textContent = `${res.label} NEWS`;
    badge.className = `verdict-badge ${res.label.toLowerCase()}`;
    
    document.getElementById('aiScore').textContent = `${res.ai_score}/10`;
    document.getElementById('verdictSubtitle').textContent = `Flesch readability: ${res.stats.readability_label}. Sentiment polarity compound index: ${res.stats.sentiment.compound}.`;

    // Metrc squares
    document.getElementById('confidenceVal').textContent = `${res.confidence}%`;
    document.getElementById('riskVal').textContent = res.risk_category;
    document.getElementById('reliabilityVal').textContent = res.reliability;
    document.getElementById('speedVal').textContent = `${res.prediction_time}s`;

    // Explainable AI reasons list
    const xaiReasons = document.getElementById('xaiReasons');
    xaiReasons.innerHTML = res.explanation.split('\n')
        .filter(line => line.strip !== '')
        .map(line => `<p>${escapeHtml(line.replace('•', '').replace('**', '').trim())}</p>`)
        .join('');

    // Tags
    const posList = document.getElementById('posTags');
    const negList = document.getElementById('negTags');
    
    posList.innerHTML = (res.keywords.positive || []).map(w => `<span class="tag positive">${escapeHtml(w)}</span>`).join('');
    negList.innerHTML = (res.keywords.negative || []).concat(res.keywords.suspicious || []).map(w => `<span class="tag negative">${escapeHtml(w)}</span>`).join('');

    if (posList.innerHTML === '') posList.innerHTML = '<span class="text-muted font-sm">None detected</span>';
    if (negList.innerHTML === '') negList.innerHTML = '<span class="text-muted font-sm">None detected</span>';

    // NLP stats
    document.getElementById('statSentences').textContent = res.stats.sentence_count;
    document.getElementById('statReadability').textContent = res.stats.readability_score;
    document.getElementById('statSpam').textContent = res.stats.spam_score;

    // Charts update
    renderProbabilityDoughnut(res.real_prob, res.fake_prob);

    // Download PDF Link
    const pdfBtn = document.getElementById('btnDownloadPdf');
    pdfBtn.href = `/api/report/${res.id}`;

    // Highlight text view injection
    const highlightedHtml = renderHighlightsMarkup(originalText, res.highlights || []);
    articleViewer.innerHTML = highlightedHtml;
    articleEditor.classList.add('hidden');
    articleViewer.classList.remove('hidden');

    // Register toggle edit listener
    const editBtn = document.getElementById('btnEditAgain');
    editBtn.onclick = () => {
        articleViewer.classList.add('hidden');
        articleEditor.classList.remove('hidden');
        articleEditor.focus();
    };

    showToast('Analysis complete!', 'success');
}

// ─── Chart.js Helper ────────────────────────────────────────────────────────

function renderProbabilityDoughnut(realVal, fakeVal) {
    const ctx = document.getElementById('probDoughnutChart');
    if (!ctx) return;

    if (probDoughnutChart) {
        probDoughnutChart.destroy();
    }

    probDoughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Real Probability', 'Fake Probability'],
            datasets: [{
                data: [realVal, fakeVal],
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
