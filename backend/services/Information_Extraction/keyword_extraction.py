# keyword_extraction.py
from keybert import KeyBERT

class KeywordExtractor:
    def __init__(self):
        self.model = KeyBERT()

    def extract_keywords(self, sentence: str, top_n=5):
        keywords = self.model.extract_keywords(sentence, top_n=top_n)
        return [k[0] for k in keywords]