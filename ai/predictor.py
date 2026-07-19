import os
import re
import time
import joblib
import numpy as np

from ai.preprocessor import clean_text_nlp
from ai.feature_engineering import analyze_features

# ─── Config paths ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'model.pkl')
VECTORIZER_PATH = os.path.join(MODELS_DIR, 'vectorizer.pkl')

_model = None
_vectorizer = None


def load_predictor():
    """Load trained model and vectorizer."""
    global _model, _vectorizer
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        return False
    
    _model = joblib.load(MODEL_PATH)
    _vectorizer = joblib.load(VECTORIZER_PATH)
    return True


def get_model():
    global _model
    if _model is None:
        load_predictor()
    return _model


def get_vectorizer():
    global _vectorizer
    if _vectorizer is None:
        load_predictor()
    return _vectorizer


# ─── Suspicious / Clickbait triggers ──────────────────────────────────────────

CLICKBAIT_PHRASES = [
    r"you won\'t believe", r"shocking secret", r"leaked report", r"wake up people",
    r"what they don\'t want", r"big pharma", r"deep state", r"hidden agenda",
    r"mainstream media", r"censored truth", r"miracle cure", r"proven truth",
    r"share this widely", r"must read", r"official cover-up", r"mind-blowing"
]

SENSATIONAL_WORDS = {
    'shocking', 'breaking', 'urgent', 'exposed', 'bombshell', 'explosive',
    'unbelievable', 'incredible', 'outrageous', 'horrifying', 'devastating',
    'terrifying', 'alarming', 'stunning', 'jaw-dropping', 'mind-blowing',
    'scandalous', 'controversial', 'conspiracy', 'hoax', 'scam', 'fraud'
}

EMOTIONAL_WORDS = {
    'hate', 'love', 'fear', 'anger', 'rage', 'fury', 'terror', 'panic',
    'despair', 'grief', 'shame', 'guilt', 'disgust', 'horrified', 'furious',
    'enraged', 'heartbroken', 'devastated', 'betrayed', 'outraged',
    'infuriated', 'appalled', 'disgusted', 'terrified', 'sheeple', 'puppet'
}

CREDIBILITY_WORDS = {
    'according', 'research', 'study', 'report', 'official', 'confirmed',
    'evidence', 'data', 'statistics', 'analysis', 'investigation', 'source',
    'published', 'journal', 'university', 'government', 'authority',
    'expert', 'scientist', 'professor', 'peer-reviewed', 'documented'
}


def find_suspicious_highlights(text):
    """
    Search original text and return absolute character index offsets for highlights:
    - Clickbait phrases
    - CAPS words
    - Sensational words
    - Emotional words
    - Excess punctuation (multiple ! or ?)
    """
    highlights = []
    text_lower = text.lower()

    # 1. Clickbait Phrases
    for phrase in CLICKBAIT_PHRASES:
        for match in re.finditer(phrase, text_lower):
            highlights.append({
                'start': match.start(),
                'end': match.end(),
                'word': text[match.start():match.end()],
                'type': 'clickbait'
            })

    # 2. EXCESS CAPS words (4+ chars, excluding standard abbreviations)
    for match in re.finditer(r'\b[A-Z]{4,}\b', text):
        word = match.group()
        # Avoid marking common neutral ones like USPS, NATO, CNN, HTML
        if word not in {'NATO', 'USPS', 'OPEC', 'UNICEF', 'NASA', 'HTML', 'HTTP', 'JSON', 'WIFI'}:
            highlights.append({
                'start': match.start(),
                'end': match.end(),
                'word': word,
                'type': 'caps'
            })

    # 3. Double/Multiple Punctuation
    for match in re.finditer(r'[!?]{2,}', text):
        highlights.append({
            'start': match.start(),
            'end': match.end(),
            'word': match.group(),
            'type': 'punctuation'
        })

    # Tokenizer for word level matches
    for match in re.finditer(r'\b[a-zA-Z]+\b', text):
        word = match.group()
        word_l = word.lower()

        if word_l in SENSATIONAL_WORDS:
            # Avoid duplicating overlaps
            if not any(h['start'] <= match.start() < h['end'] for h in highlights):
                highlights.append({
                    'start': match.start(),
                    'end': match.end(),
                    'word': word,
                    'type': 'sensational'
                })
        elif word_l in EMOTIONAL_WORDS:
            if not any(h['start'] <= match.start() < h['end'] for h in highlights):
                highlights.append({
                    'start': match.start(),
                    'end': match.end(),
                    'word': word,
                    'type': 'emotional'
                })

    # Sort highlights by start position
    highlights = sorted(highlights, key=lambda x: x['start'])
    return highlights


def predict_news_article(text):
    """
    Run the ML prediction pipeline and return enterprise analysis:
    - Prediction label
    - Confidence score
    - Probability details
    - Reliability status
    - Risk category
    - AI Score
    - Explainable AI text
    - Clickbait/Highlight offsets
    """
    start_time = time.time()

    model = get_model()
    vectorizer = get_vectorizer()

    if model is None or vectorizer is None:
        raise FileNotFoundError("AI models are not trained or loaded. Run model trainer first.")

    # NLP preprocessing
    cleaned = clean_text_nlp(text)
    vector = vectorizer.transform([cleaned])

    # Classifier prediction
    prediction = int(model.predict(vector)[0])
    label = 'REAL' if prediction == 1 else 'FAKE'

    # Retrieve confidence via Decision Function or Probabilities
    try:
        score = model.decision_function(vector)[0]
        confidence = 1 / (1 + np.exp(-abs(score)))
        confidence = max(0.55, min(0.999, confidence))
    except Exception:
        # fallback
        confidence = 0.85

    prediction_time = time.time() - start_time

    # Probability details
    real_prob = round(confidence * 100, 2) if label == 'REAL' else round((1 - confidence) * 100, 2)
    fake_prob = round(confidence * 100, 2) if label == 'FAKE' else round((1 - confidence) * 100, 2)
    confidence_pct = round(confidence * 100, 2)

    # Reliability and Risk definitions
    if label == 'REAL':
        if confidence_pct >= 90:
            reliability = 'Very High'
            risk_category = 'Very Low'
            ai_score = round(9.0 + (confidence_pct - 90) / 10, 1)
        elif confidence_pct >= 75:
            reliability = 'High'
            risk_category = 'Low'
            ai_score = round(7.5 + (confidence_pct - 75) * 0.1, 1)
        else:
            reliability = 'Moderate'
            risk_category = 'Medium'
            ai_score = round(5.5 + (confidence_pct - 50) * 0.08, 1)
    else:
        if confidence_pct >= 90:
            reliability = 'Very Low'
            risk_category = 'Very High'
            ai_score = round(1.0 - (confidence_pct - 90) * 0.1, 1)
            ai_score = max(0.1, ai_score)
        elif confidence_pct >= 75:
            reliability = 'Low'
            risk_category = 'High'
            ai_score = round(2.5 - (confidence_pct - 75) * 0.1, 1)
        else:
            reliability = 'Moderate'
            risk_category = 'Medium'
            ai_score = round(4.5 - (confidence_pct - 50) * 0.08, 1)

    # Get text analysis statistics
    stats = analyze_features(text)

    # Compile dynamic Explainable AI (XAI) reasons
    highlights = find_suspicious_highlights(text)
    clickbait_count = sum(1 for h in highlights if h['type'] == 'clickbait')
    caps_count = sum(1 for h in highlights if h['type'] == 'caps')
    punctuation_count = sum(1 for h in highlights if h['type'] == 'punctuation')

    reasons = []
    if label == 'FAKE':
        if clickbait_count > 0:
            reasons.append("• Suspicious clickbait phrasing detected in the headline or body.")
        if caps_count > 1:
            reasons.append("• Excessive uppercase styling matches deceptive patterns.")
        if punctuation_count > 0:
            reasons.append("• Exaggerated double punctuation indicators detected.")
        if stats['sentiment']['compound'] > 0.6 or stats['sentiment']['compound'] < -0.6:
            reasons.append("• Text uses highly polar sentiment (emotionally charged language).")
        if stats['spam_score'] > 30:
            reasons.append(f"• High content-spam probability index calculated ({stats['spam_score']}/100).")
        if not reasons:
            reasons.append("• Sentence structure features match historically deceptive publications.")
            
        explanation = (
            f"The article is predicted to be **Fake News** with {confidence_pct}% confidence. "
            f"Key factors supporting this classification:\n\n" + "\n".join(reasons)
        )
    else:
        if stats['readability_score'] >= 50:
            reasons.append("• Structured vocabulary aligns with standard news journalism formats.")
        if abs(stats['sentiment']['compound']) < 0.3:
            reasons.append("• Text shows objective sentiment (uses a balanced, neutral tone).")
        if stats['spam_score'] < 15:
            reasons.append("• Very low indicators of clickbait or spam structures.")
        # check credibility keywords
        cred_found = [w for w in CREDIBILITY_WORDS if w in text.lower()]
        if len(cred_found) >= 2:
            reasons.append(f"• Includes critical references and authority indicators ({', '.join(cred_found[:2])}).")
        if not reasons:
            reasons.append("• Objective sentence patterns consistent with reliable news sources.")
            
        explanation = (
            f"The article is predicted to be **Real News** with {confidence_pct}% confidence. "
            f"Key factors supporting this classification:\n\n" + "\n".join(reasons)
        )

    # Keywords summary
    text_lower = text.lower()
    keywords = {
        'positive': [w for w in CREDIBILITY_WORDS if w in text_lower][:6],
        'negative': [w for w in SENSATIONAL_WORDS if w in text_lower][:6],
        'suspicious': [w for w in EMOTIONAL_WORDS if w in text_lower][:6],
        'repeated': [match['word'] for match in highlights if match['type'] == 'clickbait'][:6]
    }

    return {
        'prediction': prediction,
        'label': label,
        'confidence': confidence_pct,
        'fake_prob': fake_prob,
        'real_prob': real_prob,
        'reliability': reliability,
        'risk_category': risk_category,
        'ai_score': ai_score,
        'explanation': explanation,
        'keywords': keywords,
        'stats': stats,
        'highlights': highlights,
        'prediction_time': round(prediction_time, 4)
    }
