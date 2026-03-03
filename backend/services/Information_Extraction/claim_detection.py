# claim_detection.py
from transformers import pipeline

OPINION_CUES = [
    "i think", "i believe", "in my opinion", "i feel",
    "seems", "probably", "maybe", "should", "beautiful",
    "awesome", "amazing", "love", "hate", "wonderful"
]

class ClaimDetector:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.labels = ["factual claim", "opinion/comment"]

    def is_claim(self, sentence: str):
        res = self.classifier(sentence, candidate_labels=self.labels)
        score = dict(zip(res["labels"], res["scores"]))["factual claim"]
        score = self._penalize_opinion(sentence.lower(), score)
        return score >= 0.6, round(score, 3)

    def _penalize_opinion(self, s: str, score: float) -> float:
        if any(cue in s for cue in OPINION_CUES):
            score *= 0.4
        if "?" in s:
            score *= 0.6
        return score