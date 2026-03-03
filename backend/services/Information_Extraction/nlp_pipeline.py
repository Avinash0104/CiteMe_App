# nlp_pipeline.py
from .claim_detection import ClaimDetector
from .entity_extraction import EntityExtractor
from .keyword_extraction import KeywordExtractor
import spacy

class NLPPipeline:
    def __init__(self):
        print("🚀 Initializing NLP Pipeline...")
        self.claim_detector = ClaimDetector()
        self.entity_extractor = EntityExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.spacy_nlp = spacy.load("en_core_web_trf")
        print("✅ NLP Pipeline Ready!")

    def process_text(self, text: str):
        doc = self.spacy_nlp(text)
        results = []
        for sent in doc.sents:
            s = sent.text.strip()
            is_claim, score = self.claim_detector.is_claim(s)
            entities = self.entity_extractor.extract(s)
            keywords = self.keyword_extractor.extract_keywords(s)
            results.append({
                "sentence": s,
                "is_claim": is_claim,
                "score": score,
                "entities": entities,
                "keywords": keywords
            })
        return {"claims": results}


