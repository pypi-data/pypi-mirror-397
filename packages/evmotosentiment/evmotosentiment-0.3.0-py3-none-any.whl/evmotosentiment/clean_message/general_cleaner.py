import nltk
import re

try:
    from nltk.corpus import stopwords
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")
    from nltk.corpus import stopwords

# Step 1: Define stopwords
stop_words = set(word.lower() for word in stopwords.words('english'))

do_not_discard = [
    'off','not','out','stucked','stuck','coming','light','lights',
    'on','turn','bike','turning','shut','shutting','down','breaker',
    'talking','responding','asleep','charging','add','going','drain',
    'drained','waiting','wait','no','damage','damaged','connector'
    ]
for word in do_not_discard:
    stop_words.discard(word)

# Step 2: Function to clean text
def preprocess_text(text):
    """

    Parameters
    ----------
    text : str
        the text to be processed
        
    Returns
    -------
    words : str
        the text that has been processed
        
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Remove numbers
    text = re.sub(r'\b\d+\b', '', text)
    # Tokenize (split into words)
    words = text.split()
    # Remove stopwords
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)