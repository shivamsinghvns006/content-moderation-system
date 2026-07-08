"""
text_moderator.py
------------------
This module analyzes TEXT content (comments, posts, messages) and decides:
  - approved  -> content is fine, publish it immediately
  - flagged   -> content is borderline, send to a human moderator
  - rejected  -> content clearly breaks the rules, block it automatically

HOW IT WORKS (step by step):
1. Profanity check       -> uses a word-list library to catch bad words
2. Toxicity scoring      -> a simple weighted-keyword model that scores how
                             hostile/abusive the text sounds (0.0 to 1.0)
3. Spam / spammy pattern -> checks for excessive caps, links, repeated chars
4. Combine everything into one final decision + confidence score

NOTE ON "REAL AI":
In production, step 2 would normally call a proper NLP model (or Azure AI
Language's "Text Analytics for Health / Content Safety" API) which uses a
trained neural network to understand context, sarcasm, etc. Here we use a
transparent, rule-based scorer instead, so that:
  - the project runs instantly with no GPU/internet/API key required
  - you can literally read every rule and explain it in your presentation
  - swapping in Azure AI Language later is a 10-line change (see the
    `analyze_with_azure` stub at the bottom of this file).
"""

import re
from better_profanity import profanity

profanity.load_censor_words()

# Weighted keywords used for the toxicity heuristic.
# Higher weight = stronger signal of hostile/abusive intent.
# (This list is intentionally small and illustrative for a student project;
# in a real system this would be a trained ML classifier.)
TOXIC_KEYWORDS = {
    "hate": 0.6,
    "kill": 0.7,
    "stupid": 0.3,
    "idiot": 0.35,
    "dumb": 0.25,
    "shut up": 0.3,
    "loser": 0.3,
    "worthless": 0.4,
    "die": 0.5,
    "attack": 0.3,
}

SPAM_PATTERNS = [
    r"(.)\1{5,}",                 # same character repeated 6+ times, e.g. "aaaaaa"
    r"\b(buy now|click here|free money|earn \$\$\$)\b",
]

LINK_PATTERN = r"https?://\S+"
MAX_LINKS_ALLOWED = 1  # 2 or more links in one message is treated as spammy


def _caps_ratio(text: str) -> float:
    """Returns the fraction of alphabetic characters that are uppercase."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    caps = [c for c in letters if c.isupper()]
    return len(caps) / len(letters)


def _toxicity_score(text: str) -> float:
    """A simple weighted-keyword toxicity scorer. Returns 0.0 - 1.0."""
    lowered = text.lower()
    score = 0.0
    for keyword, weight in TOXIC_KEYWORDS.items():
        if keyword in lowered:
            score += weight
    return min(score, 1.0)


def _is_spam(text: str) -> bool:
    # Count how many links appear anywhere in the message
    links_found = re.findall(LINK_PATTERN, text, re.IGNORECASE)
    if len(links_found) > MAX_LINKS_ALLOWED:
        return True

    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def analyze_text(text: str, toxicity_threshold: float = 0.5) -> dict:
    """
    Main entry point. Analyzes a piece of text and returns a result dict:

    {
        "decision": "approved" | "flagged" | "rejected",
        "confidence_score": float,
        "categories": [list of reasons],
    }
    """
    categories = []

    has_profanity = profanity.contains_profanity(text)
    if has_profanity:
        categories.append("profanity")

    toxicity = _toxicity_score(text)
    if toxicity >= toxicity_threshold:
        categories.append("toxicity")

    caps_ratio = _caps_ratio(text)
    if caps_ratio > 0.7 and len(text) > 10:
        categories.append("excessive_caps")

    is_spam = _is_spam(text)
    if is_spam:
        categories.append("spam")

    # ---- Decision logic ----
    # Rejected: severe profanity + high toxicity together, or blatant spam
    if (has_profanity and toxicity >= toxicity_threshold) or is_spam:
        decision = "rejected"
        confidence = max(toxicity, 0.85 if is_spam else 0.7)
    # Flagged: any single red flag on its own -> needs a human to look at it
    elif categories:
        decision = "flagged"
        confidence = max(toxicity, 0.5)
    # Approved: nothing suspicious found
    else:
        decision = "approved"
        confidence = 1.0 - toxicity

    return {
        "decision": decision,
        "confidence_score": round(confidence, 2),
        "categories": categories,
    }


def analyze_with_azure(text: str) -> dict:
    """
    STUB / PLACEHOLDER for real Azure AI Language integration.

    To use this for real:
    1. pip install azure-ai-textanalytics
    2. Fill in AZURE_LANGUAGE_KEY / AZURE_LANGUAGE_ENDPOINT in config.py
    3. Uncomment and complete the code below.

    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential

    client = TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_LANGUAGE_KEY),
    )
    response = client.analyze_sentiment([text])[0]
    # map response.sentiment / confidence_scores to a decision, same shape
    # as analyze_text() above, then return it.
    """
    raise NotImplementedError(
        "Azure integration not configured. Using analyze_text() instead."
    )
