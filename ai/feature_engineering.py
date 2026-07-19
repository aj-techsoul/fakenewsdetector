import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon
try:
    nltk.download('vader_lexicon', quiet=True)
except Exception as e:
    print(f"VADER download warning: {e}")

# Initialize Sentiment Analyzer
try:
    sia = SentimentIntensityAnalyzer()
except Exception:
    sia = None


def count_syllables(word):
    """Approximate syllable count in a word using vowel groups heuristic."""
    word = word.lower().strip()
    if not word:
        return 0
    
    # Remove silent e at the end (simplistic approach)
    if word.endswith('e'):
        word = word[:-1]
        
    vowels = "aeiouy"
    count = 0
    prev_char_is_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_is_vowel:
            count += 1
        prev_char_is_vowel = is_vowel
        
    if count == 0:
        count = 1
    return count


def calculate_flesch_reading_ease(words, sentence_count):
    """
    Calculate Flesch Reading Ease score:
    Score formula: 206.835 - 1.015 * (ASL) - 84.6 * (ASW)
    where:
    ASL = Average Sentence Length (words / sentences)
    ASW = Average Syllables per Word (syllables / words)
    """
    word_count = len(words)
    if word_count == 0 or sentence_count == 0:
        return 0.0

    total_syllables = sum(count_syllables(w) for w in words)
    
    asl = word_count / sentence_count
    asw = total_syllables / word_count
    
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(max(0.0, min(100.0, score)), 2)


def get_readability_label(score):
    """Return descriptive reading ease levels."""
    if score >= 90:
        return "Very Easy (5th Grade)"
    elif score >= 80:
        return "Easy (6th Grade)"
    elif score >= 70:
        return "Fairly Easy (7th Grade)"
    elif score >= 60:
        return "Standard (8th-9th Grade)"
    elif score >= 50:
        return "Fairly Difficult (High School)"
    elif score >= 30:
        return "Difficult (College)"
    else:
        return "Very Confusing (Graduate)"


def analyze_features(text):
    """
    Perform comprehensive feature analysis on text:
    1. Sentence / Word counts
    2. Sentiment score (positive, negative, compound)
    3. Readability grade and statistics
    4. Heuristic spam score
    """
    if not text or not text.strip():
        return {
            'word_count': 0,
            'char_count': 0,
            'sentence_count': 0,
            'reading_time': '0 sec',
            'avg_word_length': 0.0,
            'vocab_richness': 0.0,
            'readability_score': 0.0,
            'readability_label': 'N/A',
            'sentiment': {'pos': 0.0, 'neg': 0.0, 'neu': 0.0, 'compound': 0.0},
            'spam_score': 0
        }

    # Sentence count
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)

    # Word counts
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    char_count = len(text)

    # Reading time (avg 200 WPM)
    read_mins = word_count / 200
    if read_mins < 1:
        reading_time = f"{max(1, int(read_mins * 60))} sec"
    else:
        reading_time = f"{read_mins:.1f} min"

    # Lexical features
    avg_word_length = round(sum(len(w) for w in words) / max(word_count, 1), 1)
    unique_words = set(w.lower() for w in words)
    vocab_richness = round(len(unique_words) / max(word_count, 1) * 100, 1)

    # Readability Ease
    readability_score = calculate_flesch_reading_ease(words, sentence_count)
    readability_label = get_readability_label(readability_score)

    # Sentiment analysis (VADER)
    sentiment_data = {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}
    if sia and text.strip():
        try:
            sentiment_data = sia.polarity_scores(text)
        except Exception:
            pass

    # Spam heuristic score
    spam_score = 0
    upper_ratio = sum(1 for c in text if c.isupper()) / max(char_count, 1)
    if upper_ratio > 0.4:
        spam_score += 25
    
    excl_count = text.count('!')
    if excl_count > 4:
        spam_score += 15
    
    # Emotional and sensational trigger word frequencies
    triggers = ['breaking', 'shocking', 'secret', 'banned', 'conspiracy', 'wake up', 'expose']
    for t in triggers:
        if t in text.lower():
            spam_score += 10
            
    spam_score = min(100, spam_score)

    return {
        'word_count': word_count,
        'char_count': char_count,
        'sentence_count': sentence_count,
        'reading_time': reading_time,
        'avg_word_length': avg_word_length,
        'vocab_richness': vocab_richness,
        'readability_score': readability_score,
        'readability_label': readability_label,
        'sentiment': sentiment_data,
        'spam_score': spam_score
    }
