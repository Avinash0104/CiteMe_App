# entity_extraction.py
import spacy

class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_trf")

    def extract(self, sentence: str):
        doc = self.nlp(sentence)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities