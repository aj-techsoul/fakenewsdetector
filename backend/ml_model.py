"""
backend/ml_model.py — ML Model Loader, Predictor & Explainer
=============================================================
Handles loading the trained model, making predictions on user input,
generating human-readable explanations, and extracting keyword analysis.
"""

import os
import re
import time
import json
import joblib
import numpy as np

import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'model.pkl')
VECTORIZER_PATH = os.path.join(MODELS_DIR, 'vectorizer.pkl')
METRICS_PATH = os.path.join(MODELS_DIR, 'metrics.json')

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

# ─── Keyword Lists ───────────────────────────────────────────────────────────

SENSATIONAL_WORDS = {
    'shocking', 'breaking', 'urgent', 'exposed', 'bombshell', 'explosive',
    'unbelievable', 'incredible', 'outrageous', 'horrifying', 'devastating',
    'terrifying', 'alarming', 'stunning', 'jaw-dropping', 'mind-blowing',
    'scandalous', 'controversial', 'viral', 'leaked', 'secret', 'revealed',
    'conspiracy', 'cover-up', 'hoax', 'scam', 'fraud'
}

EMOTIONAL_WORDS = {
    'hate', 'love', 'fear', 'anger', 'rage', 'fury', 'terror', 'panic',
    'despair', 'grief', 'shame', 'guilt', 'disgust', 'horrified', 'furious',
    'enraged', 'heartbroken', 'devastated', 'betrayed', 'victimized',
    'outraged', 'infuriated', 'appalled', 'disgusted', 'terrified'
}

CREDIBILITY_WORDS = {
    'according', 'research', 'study', 'report', 'official', 'confirmed',
    'evidence', 'data', 'statistics', 'analysis', 'investigation', 'source',
    'published', 'journal', 'university', 'government', 'authority',
    'expert', 'scientist', 'professor', 'peer-reviewed', 'documented'
}

MANIPULATIVE_WORDS = {
    'wake up', 'they don\'t want you to know', 'mainstream media',
    'the truth', 'big pharma', 'deep state', 'new world order',
    'sheeple', 'puppet', 'brainwashed', 'propaganda', 'censored',
    'silenced', 'banned', 'suppressed', 'hidden agenda'
}

# ─── Model Management ────────────────────────────────────────────────────────

_model = None
_vectorizer = None
_metrics = None


def load_model():
    """Load the trained model and vectorizer from disk."""
    global _model, _vectorizer, _metrics

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model not found. Please run 'python train_model.py' first."
        )

    _model = joblib.load(MODEL_PATH)
    _vectorizer = joblib.load(VECTORIZER_PATH)

    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            _metrics = json.load(f)

    return True


def get_model():
    """Get the loaded model, loading it if necessary."""
    global _model
    if _model is None:
        load_model()
    return _model


def get_vectorizer():
    """Get the loaded vectorizer, loading it if necessary."""
    global _vectorizer
    if _vectorizer is None:
        load_model()
    return _vectorizer


def get_metrics():
    """Get the saved training metrics."""
    global _metrics
    if _metrics is None:
        load_model()
    return _metrics


def is_model_loaded():
    """Check if model is loaded and ready."""
    return _model is not None and _vectorizer is not None


# ─── Text Preprocessing ─────────────────────────────────────────────────────

def clean_text(text):
    """Clean and preprocess text for prediction (same pipeline as training)."""
    if not isinstance(text, str):
        return ''

    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\(reuters\)\s*-?\s*', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words and len(w) > 2]

    return ' '.join(words)


# ─── Prediction ──────────────────────────────────────────────────────────────

def predict(text):
    """
    Predict whether the given text is Fake or Real news.

    Returns:
        dict with keys: prediction, label, confidence, fake_prob, real_prob,
                        prediction_time, cleaned_text
    """
    model = get_model()
    vectorizer = get_vectorizer()

    start_time = time.time()

    # Clean text
    cleaned = clean_text(text)

    # Vectorize
    text_vector = vectorizer.transform([cleaned])

    # Predict
    prediction = model.predict(text_vector)[0]

    # Get decision function score for confidence
    try:
        decision_score = model.decision_function(text_vector)[0]
        # Convert decision score to a probability-like confidence using sigmoid
        confidence = 1 / (1 + np.exp(-abs(decision_score)))
        confidence = max(0.51, min(0.99, confidence))  # Clamp between 51-99%
    except Exception:
        confidence = 0.85  # Fallback

    prediction_time = time.time() - start_time

    # Label
    label = 'REAL' if prediction == 1 else 'FAKE'

    # Probabilities
    if label == 'REAL':
        real_prob = round(confidence * 100, 2)
        fake_prob = round((1 - confidence) * 100, 2)
    else:
        fake_prob = round(confidence * 100, 2)
        real_prob = round((1 - confidence) * 100, 2)

    return {
        'prediction': int(prediction),
        'label': label,
        'confidence': round(confidence * 100, 2),
        'fake_prob': fake_prob,
        'real_prob': real_prob,
        'prediction_time': round(prediction_time, 4),
        'cleaned_text': cleaned
    }


# ─── Explanation Generator ───────────────────────────────────────────────────

def generate_explanation(text, prediction_result):
    """
    Generate a human-readable AI explanation for the prediction.

    Analyzes the text for linguistic patterns and constructs an
    explanation paragraph.
    """
    label = prediction_result['label']
    confidence = prediction_result['confidence']
    text_lower = text.lower()

    # Count pattern occurrences
    sensational_found = [w for w in SENSATIONAL_WORDS if w in text_lower]
    emotional_found = [w for w in EMOTIONAL_WORDS if w in text_lower]
    credibility_found = [w for w in CREDIBILITY_WORDS if w in text_lower]

    # Build explanation components
    observations = []

    if label == 'FAKE':
        if sensational_found:
            observations.append(
                f"contains sensational language ({', '.join(sensational_found[:3])})"
            )
        if emotional_found:
            observations.append(
                f"uses emotionally manipulative words ({', '.join(emotional_found[:3])})"
            )
        if len(credibility_found) < 2:
            observations.append(
                "lacks credible source references and factual citations"
            )
        if '!' in text:
            exclamation_count = text.count('!')
            if exclamation_count > 2:
                observations.append(
                    f"uses excessive exclamation marks ({exclamation_count} found)"
                )
        if text.upper() == text and len(text) > 50:
            observations.append("uses ALL CAPS formatting typical of clickbait")

        if not observations:
            observations.append(
                "exhibits linguistic patterns commonly found in misinformation"
            )

        explanation = (
            f"This article {', '.join(observations)}. "
            f"Based on the trained machine learning model's analysis of "
            f"TF-IDF features and linguistic patterns, the article is "
            f"predicted to be **Fake News** with {confidence:.1f}% confidence. "
            f"The model detected patterns that are statistically associated "
            f"with unreliable news sources in the training dataset."
        )
    else:
        if credibility_found:
            observations.append(
                f"references credible indicators ({', '.join(credibility_found[:3])})"
            )
        if not sensational_found:
            observations.append("maintains a neutral and factual tone")
        if not emotional_found:
            observations.append("avoids emotionally manipulative language")

        if not observations:
            observations.append(
                "follows patterns consistent with legitimate journalism"
            )

        explanation = (
            f"This article {', '.join(observations)}. "
            f"Based on the trained machine learning model's analysis of "
            f"TF-IDF features and linguistic patterns, the article is "
            f"predicted to be **Real News** with {confidence:.1f}% confidence. "
            f"The text structure and vocabulary align with reliable news "
            f"sources found in the training dataset."
        )

    return explanation


# ─── Keyword Extraction ─────────────────────────────────────────────────────

def extract_keywords(text):
    """
    Extract and categorize keywords from the text.

    Returns dict with lists: positive, negative, suspicious, emotional, repeated
    """
    text_lower = text.lower()
    words = re.findall(r'\b[a-z]+\b', text_lower)

    # Find word frequencies
    word_freq = {}
    for w in words:
        if w not in stop_words and len(w) > 2:
            word_freq[w] = word_freq.get(w, 0) + 1

    # Categorize
    positive = [w for w in CREDIBILITY_WORDS if w in text_lower][:8]
    negative = [w for w in SENSATIONAL_WORDS if w in text_lower][:8]
    suspicious = [w for w in MANIPULATIVE_WORDS if w in text_lower][:8]
    emotional = [w for w in EMOTIONAL_WORDS if w in text_lower][:8]
    repeated = [w for w, c in sorted(word_freq.items(), key=lambda x: -x[1])
                if c >= 3][:8]

    return {
        'positive': positive,
        'negative': negative,
        'suspicious': suspicious,
        'emotional': emotional,
        'repeated': repeated
    }
