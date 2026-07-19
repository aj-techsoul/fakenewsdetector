"""
backend/text_analysis.py — Text Statistics & Analysis
======================================================
Provides text statistics like word count, sentence count, reading time,
vocabulary richness, complexity score, and spam score.
"""

import re
import math


def analyze_text(text):
    """
    Compute comprehensive text statistics.

    Returns:
        dict with: word_count, char_count, sentence_count, reading_time,
                   avg_word_length, vocabulary_richness, complexity_score,
                   spam_score
    """
    if not text or not text.strip():
        return {
            'word_count': 0,
            'char_count': 0,
            'sentence_count': 0,
            'reading_time': '0 sec',
            'avg_word_length': 0,
            'vocabulary_richness': 0,
            'complexity_score': 0,
            'spam_score': 0
        }

    # Basic counts
    char_count = len(text)
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)

    # Sentence count (split on . ! ?)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)

    # Reading time (average 200 WPM)
    reading_minutes = word_count / 200
    if reading_minutes < 1:
        reading_time = f"{max(1, int(reading_minutes * 60))} sec"
    else:
        reading_time = f"{reading_minutes:.1f} min"

    # Average word length
    avg_word_length = round(
        sum(len(w) for w in words) / max(word_count, 1), 1
    )

    # Vocabulary richness (unique words / total words)
    unique_words = set(w.lower() for w in words)
    vocabulary_richness = round(
        len(unique_words) / max(word_count, 1) * 100, 1
    )

    # Complexity score (0-100)
    # Based on avg word length, sentence length, and vocabulary richness
    avg_sentence_length = word_count / max(sentence_count, 1)
    complexity = min(100, round(
        (avg_word_length * 8) +
        (min(avg_sentence_length, 30) * 1.5) +
        (vocabulary_richness * 0.3)
    ))

    # Spam score (0-100) - heuristic based on suspicious patterns
    spam_score = _calculate_spam_score(text, words, word_count)

    return {
        'word_count': word_count,
        'char_count': char_count,
        'sentence_count': sentence_count,
        'reading_time': reading_time,
        'avg_word_length': avg_word_length,
        'vocabulary_richness': vocabulary_richness,
        'complexity_score': complexity,
        'spam_score': spam_score
    }


def _calculate_spam_score(text, words, word_count):
    """
    Calculate a heuristic spam score (0-100).
    Higher score = more likely to be spammy/fake.
    """
    score = 0

    # Excessive capitalization
    upper_chars = sum(1 for c in text if c.isupper())
    upper_ratio = upper_chars / max(len(text), 1)
    if upper_ratio > 0.5:
        score += 20
    elif upper_ratio > 0.3:
        score += 10

    # Excessive exclamation marks
    excl_count = text.count('!')
    if excl_count > 5:
        score += 15
    elif excl_count > 2:
        score += 8

    # Excessive question marks
    quest_count = text.count('?')
    if quest_count > 5:
        score += 10

    # URL density
    url_count = len(re.findall(r'https?://\S+', text))
    if url_count > 3:
        score += 10

    # Very short text (could be clickbait)
    if word_count < 50:
        score += 15
    elif word_count < 100:
        score += 8

    # Repetitive words
    if word_count > 0:
        word_freq = {}
        for w in words:
            wl = w.lower()
            word_freq[wl] = word_freq.get(wl, 0) + 1
        max_freq = max(word_freq.values()) if word_freq else 0
        if max_freq > word_count * 0.1:
            score += 10

    # Sensational patterns
    sensational_patterns = [
        r'you won\'t believe',
        r'shocking',
        r'breaking',
        r'this is huge',
        r'exposed',
        r'wake up',
        r'share before',
        r'must read',
        r'what they don\'t',
    ]
    for pattern in sensational_patterns:
        if re.search(pattern, text.lower()):
            score += 5

    return min(100, score)
