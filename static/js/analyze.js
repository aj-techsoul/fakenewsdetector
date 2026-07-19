/**
 * analyze.js — Analyze Page Logic
 * =================================
 * Handles text editor counters, sample loading, clipboard paste,
 * validation, AJAX prediction submission, and loading animation.
 */

// ─── DOM Elements ───────────────────────────────────────────────────────────

const newsInput = document.getElementById('newsInput');
const charCount = document.getElementById('charCount');
const wordCount = document.getElementById('wordCount');
const btnClear = document.getElementById('btnClear');
const btnPaste = document.getElementById('btnPaste');
const btnSampleReal = document.getElementById('btnSampleReal');
const btnSampleFake = document.getElementById('btnSampleFake');
const btnAnalyze = document.getElementById('btnAnalyze');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const loadingOverlay = document.getElementById('loadingOverlay');

// ─── Text Counters ──────────────────────────────────────────────────────────

function updateCounters() {
    const text = newsInput.value;
    charCount.textContent = text.length.toLocaleString();

    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    wordCount.textContent = words.length.toLocaleString();
}

newsInput.addEventListener('input', updateCounters);

// ─── Button Handlers ────────────────────────────────────────────────────────

// Clear button
btnClear.addEventListener('click', () => {
    newsInput.value = '';
    updateCounters();
    hideError();
    newsInput.focus();
});

// Paste button
btnPaste.addEventListener('click', async () => {
    try {
        const text = await navigator.clipboard.readText();
        newsInput.value = text;
        updateCounters();
        hideError();
        showToast('Text pasted from clipboard', 'success');
    } catch (err) {
        showToast('Unable to access clipboard. Please paste manually.', 'error');
    }
});

// Sample Real News
btnSampleReal.addEventListener('click', () => {
    newsInput.value = SAMPLE_REAL;
    updateCounters();
    hideError();
    showToast('Sample real news article loaded', 'success');
});

// Sample Fake News
btnSampleFake.addEventListener('click', () => {
    newsInput.value = SAMPLE_FAKE;
    updateCounters();
    hideError();
    showToast('Sample fake news article loaded', 'info');
});

// ─── Error Handling ─────────────────────────────────────────────────────────

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.add('visible');
}

function hideError() {
    errorMessage.classList.remove('visible');
}

// ─── Loading Animation ─────────────────────────────────────────────────────

function showLoading() {
    loadingOverlay.classList.add('active');

    const steps = ['step1', 'step2', 'step3', 'step4'];
    let currentStep = 0;

    // Reset all steps
    steps.forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('active', 'done');
    });

    // Animate steps sequentially
    function activateNext() {
        if (currentStep > 0) {
            const prev = document.getElementById(steps[currentStep - 1]);
            prev.classList.remove('active');
            prev.classList.add('done');
            prev.querySelector('i').className = 'fas fa-check-circle';
        }

        if (currentStep < steps.length) {
            const current = document.getElementById(steps[currentStep]);
            current.classList.add('active');
            currentStep++;
            setTimeout(activateNext, 600);
        }
    }

    activateNext();
}

function hideLoading() {
    loadingOverlay.classList.remove('active');
}

// ─── Analyze Submit ─────────────────────────────────────────────────────────

btnAnalyze.addEventListener('click', async () => {
    const text = newsInput.value.trim();

    // Validation
    if (!text) {
        showError('Please enter a news article to analyze.');
        newsInput.focus();
        return;
    }

    if (text.length < 20) {
        showError('The text is too short. Please provide at least 20 characters for accurate analysis.');
        newsInput.focus();
        return;
    }

    const words = text.split(/\s+/).filter(w => w.length > 0);
    if (words.length < 5) {
        showError('Please provide at least 5 words for meaningful analysis.');
        newsInput.focus();
        return;
    }

    // Hide any previous errors
    hideError();

    // Show loading animation
    showLoading();

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Prediction failed');
        }

        // Redirect to result page
        hideLoading();
        window.location.href = `/result/${data.id}`;

    } catch (err) {
        hideLoading();
        showError(err.message || 'An error occurred. Please try again.');
        showToast('Analysis failed: ' + (err.message || 'Unknown error'), 'error');
    }
});

// Allow Ctrl+Enter to submit
newsInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        btnAnalyze.click();
    }
});

// ─── Initialize ─────────────────────────────────────────────────────────────

updateCounters();
