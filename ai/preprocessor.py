import re
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Auto download required NLTK datasets
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except Exception as e:
    print(f"NLTK download warning: {e}")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text_nlp(text):
    """
    Advanced text cleaning and lemmatization pipeline:
    1. Unicode normalization (NFC)
    2. Lowercase
    3. Remove URLs
    4. Remove HTML tags
    5. Remove emojis & special symbols
    6. Remove numbers and punctuation
    7. Remove stopwords
    8. WordNet Lemmatization
    """
    if not isinstance(text, str):
        return ''

    # Unicode normalization
    text = unicodedata.normalize('NFC', text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove Reuters tag (common in ISOT real news) to prevent leakage
    text = re.sub(r'\(reuters\)\s*-?\s*', '', text)

    # Remove emojis and non-ASCII icons
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Remove numbers, punctuation and special chars
    text = re.sub(r'[^a-z\s]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize, remove stopwords, and lemmatize with caching
    words = text.split()
    cleaned_words = []
    
    # Local cache reference for faster access
    global_cache = _get_lemmatize_cache()
    
    for w in words:
        if w not in stop_words and len(w) > 2:
            if w in global_cache:
                lemma = global_cache[w]
            else:
                # Lemmatize nouns, verbs, and adjectives
                lemma = lemmatizer.lemmatize(w, pos='v')
                lemma = lemmatizer.lemmatize(lemma, pos='n')
                lemma = lemmatizer.lemmatize(lemma, pos='a')
                global_cache[w] = lemma
            cleaned_words.append(lemma)

    return ' '.join(cleaned_words)

# Module-level private cache to persist across calls
_LEMMATIZE_CACHE = {}
def _get_lemmatize_cache():
    return _LEMMATIZE_CACHE
