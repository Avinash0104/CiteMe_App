#!/usr/bin/env python3
# nlp_api.py - NLP Pipeline Unified Interface
"""
Simple and easy-to-use NLP analysis interface
Provided for other teams to call directly

Usage:
    from nlp_api import analyze_text
    
    result = analyze_text("Your text here")
    print(result)
"""

from typing import Dict, List, Any, Tuple
import re
import logging
import sys
from pathlib import Path

# Add parent directory to Python path to import core modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store initialized models (Singleton pattern to avoid repeated loading)
_nlp_pipeline = None
_pipeline_initialized = False



def split_into_clauses(text: str) -> List[str]:
    """
    升级版启发式子句分割器：保留连接词，并智能合并短主语/短词组。
    """
    # Use parentheses (and|but) to capture conjunctions; this way, the conjunctions will also be retained in the list after splitting.
    raw_chunks = re.split(r'(?i)(?:,\s*)?\b(and|but)\b\s+', text)

    # If there is no "and" or "but", return directly to the original sentence.
    if len(raw_chunks) == 1:
        return [text]

    clauses = []
    current_clause = raw_chunks[0].strip()

    # The step size is 2 for each iteration (skipping conjunctions and directly taking the next clause segment).
    for i in range(1, len(raw_chunks), 2):
        conjunction = raw_chunks[i].strip()
        next_chunk = raw_chunks[i+1].strip()

        if len(current_clause.split()) < 5 or len(next_chunk.split()) < 5:
            current_clause = f"{current_clause} {conjunction} {next_chunk}"
        else:
            clauses.append(current_clause)
            current_clause = next_chunk

    clauses.append(current_clause)
    return clauses


def _initialize_pipeline():
    """
    Internal function: Initialize NLP Pipeline
    Uses singleton pattern to ensure models are loaded only once
    """
    global _nlp_pipeline, _pipeline_initialized

    if _pipeline_initialized:
        return _nlp_pipeline

    try:
        logger.info("Initializing NLP Pipeline...")

        from claim_detection import ClaimDetector
        from entity_extraction import EntityExtractor
        from keyword_extraction import KeywordExtractor
        import spacy

        # Create pipeline object
        class NLPPipeline:
            def __init__(self):
                self.claim_detector = ClaimDetector()
                self.entity_extractor = EntityExtractor()
                self.keyword_extractor = KeywordExtractor()
                self.spacy_nlp = spacy.load("en_core_web_trf")

        _nlp_pipeline = NLPPipeline()
        _pipeline_initialized = True

        logger.info("✅ NLP Pipeline initialized successfully!")
        return _nlp_pipeline

    except Exception as e:
        logger.error(f"❌ NLP Pipeline initialization failed: {e}")
        raise


def analyze_text(
    text: str,
    include_claims: bool = True,
    include_entities: bool = True,
    include_keywords: bool = True,
    max_keywords: int = 10
) -> Dict[str, Any]:
    """
    Analyze text, extract claims, entities, and keywords

    Args:
        text (str): Text to analyze
        include_claims (bool): Whether to perform claim detection, default True
        include_entities (bool): Whether to extract entities, default True
        include_keywords (bool): Whether to extract keywords, default True
        max_keywords (int): Maximum keywords to extract per sentence, default 5

    Returns:
        Dict: Dictionary containing analysis results
        {
            "success": bool,           # Whether successful
            "total_sentences": int,    # Total number of sentences
            "sentences": [             # Analysis results for each sentence
                {
                    "text": str,           # Sentence text
                    "is_claim": bool,      # Is it a claim (if include_claims=True)
                    "claim_score": float,  # Claim confidence (if include_claims=True)
                    "entities": [...],     # List of entities (if include_entities=True)
                    "keywords": [...]      # List of keywords (if include_keywords=True)
                }
            ],
            "statistics": {            # Statistics
                "claim_count": int,
                "entity_count": int,
                "keyword_count": int
            }
        }

    Example:
        >>> result = analyze_text("Apple Inc. was founded by Steve Jobs in 1976.")
        >>> print(result["sentences"][0]["entities"])
        [["Apple Inc.", "ORG"], ["Steve Jobs", "PERSON"], ["1976", "DATE"]]
    """

    # Input validation
    if not text or not isinstance(text, str):
        return {
            "success": False,
            "error": "Input text must be a non-empty string",
            "total_sentences": 0,
            "sentences": []
        }

    if not text.strip():
        return {
            "success": False,
            "error": "Input text cannot contain only whitespace characters",
            "total_sentences": 0,
            "sentences": []
        }

    try:
        # Initialize pipeline
        pipeline = _initialize_pipeline()

        # Use spaCy for sentence segmentation
        doc = pipeline.spacy_nlp(text)
        sentences_data = []

        claim_count = 0
        entity_count = 0
        keyword_count = 0

        # Process each sentence
        for sent in doc.sents:
            base_sentence_text = sent.text.strip()

            # Skip empty sentences
            if not base_sentence_text:
                continue

            # 使用我们新写的分割器，把大句子切成小块
            clauses = split_into_clauses(base_sentence_text)

            # 对切出来的每一个小块进行独立分析
            for clause_text in clauses:
                sentence_result = {
                    "text": clause_text  # 现在 text 变成了切分后的小句
                }

                # Claim detection
                if include_claims:
                    is_claim, score = pipeline.claim_detector.is_claim(clause_text)
                    sentence_result["is_claim"] = is_claim
                    sentence_result["claim_score"] = score
                    if is_claim:
                        claim_count += 1

                # Entity extraction
                if include_entities:
                    entities = pipeline.entity_extractor.extract(clause_text)
                    sentence_result["entities"] = entities
                    entity_count += len(entities)

                # Keyword extraction
                if include_keywords:
                    keywords = pipeline.keyword_extractor.extract_keywords(
                        clause_text,
                        top_n=max_keywords
                    )
                    sentence_result["keywords"] = keywords
                    keyword_count += len(keywords)

                sentences_data.append(sentence_result)

        # Construct return result
        result = {
            "success": True,
            "total_sentences": len(sentences_data),
            "sentences": sentences_data,
            "statistics": {
                "claim_count": claim_count if include_claims else None,
                "entity_count": entity_count if include_entities else None,
                "keyword_count": keyword_count if include_keywords else None
            }
        }

        return result

    except Exception as e:
        logger.error(f"❌ Error occurred while analyzing text: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_sentences": 0,
            "sentences": []
        }


def analyze_sentence(
    sentence: str,
    include_claims: bool = True,
    include_entities: bool = True,
    include_keywords: bool = True,
    max_keywords: int = 5
) -> Dict[str, Any]:
    """
    Analyze a single sentence (simplified interface)

    Args:
        sentence (str): Sentence to analyze
        include_claims (bool): Whether to perform claim detection
        include_entities (bool): Whether to extract entities
        include_keywords (bool): Whether to extract keywords
        max_keywords (int): Maximum keywords to extract

    Returns:
        Dict: Analysis result for a single sentence

    Example:
        >>> result = analyze_sentence("Python is a programming language.")
        >>> print(result["is_claim"])
        False
    """

    if not sentence or not isinstance(sentence, str):
        return {
            "success": False,
            "error": "Input sentence must be a non-empty string"
        }

    try:
        pipeline = _initialize_pipeline()

        sentence = sentence.strip()
        result = {"success": True, "text": sentence}

        # Claim detection
        if include_claims:
            is_claim, score = pipeline.claim_detector.is_claim(sentence)
            result["is_claim"] = is_claim
            result["claim_score"] = score

        # Entity extraction
        if include_entities:
            entities = pipeline.entity_extractor.extract(sentence)
            result["entities"] = entities

        # Keyword extraction
        if include_keywords:
            keywords = pipeline.keyword_extractor.extract_keywords(
                sentence,
                top_n=max_keywords
            )
            result["keywords"] = keywords

        return result

    except Exception as e:
        logger.error(f"❌ Error occurred while analyzing sentence: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_keywords_only(text: str, top_n: int = 10) -> List[str]:
    """
    Extract only keywords from text

    Args:
        text (str): Text to analyze
        top_n (int): Number of keywords to extract

    Returns:
        List[str]: List of keywords

    Example:
        >>> keywords = get_keywords_only("Python is a programming language.", top_n=3)
        >>> print(keywords)
        ["python", "programming", "language"]
    """

    result = analyze_text(
        text,
        include_claims=False,
        include_entities=False,
        include_keywords=True,
        max_keywords=top_n
    )

    if not result["success"]:
        return []

    # Merge keywords from all sentences
    all_keywords = []
    for sent in result["sentences"]:
        all_keywords.extend(sent.get("keywords", []))

    # Deduplicate (preserve order)
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return unique_keywords[:top_n]


def get_claims_only(text: str) -> List[Dict[str, Any]]:
    """
    Extract only claims from text

    Args:
        text (str): Text to analyze

    Returns:
        List[Dict]: List of claims with scores
    """
    result = analyze_text(
        text,
        include_claims=True,
        include_entities=False,
        include_keywords=False
    )

    claims = []
    if result["success"]:
        for sent in result["sentences"]:
            if sent.get("is_claim"):
                claims.append({
                    "text": sent["text"],
                    "score": sent["claim_score"]
                })
    return claims


def get_entities_only(text: str) -> List[List[str]]:
    """
    Extract only entities from text

    Args:
        text (str): Text to analyze

    Returns:
        List[List[str]]: List of entities [text, label]
    """
    result = analyze_text(
        text,
        include_claims=False,
        include_entities=True,
        include_keywords=False
    )

    all_entities = []
    if result["success"]:
        for sent in result["sentences"]:
            all_entities.extend(sent.get("entities", []))
    return all_entities


# Convenient module-level exports
__all__ = [
    'analyze_text',          # Main function: complete analysis
    'analyze_sentence',      # Analyze single sentence
    'get_claims_only',       # Get claims only
    'get_entities_only',     # Get entities only
    'get_keywords_only'      # Get keywords only
]


if __name__ == "__main__":
    """
    Test code example
    """
    print("=" * 80)
    print("NLP API Test".center(80))
    print("=" * 80)

    # Test text
    test_text = """
    Apple Inc. was founded by Steve Jobs in 1976. 
    I think the company makes great products. 
    The iPhone revolutionized the smartphone industry in 2007.
    """

    print("\n📝 Test Text:")
    print(test_text)

    print("\n" + "=" * 80)
    print("1️⃣  Complete Analysis (analyze_text)".center(80))
    print("=" * 80)
    result = analyze_text(test_text)
    print(f"Success: {result['success']}")
    print(f"Sentence Count: {result['total_sentences']}")
    print(f"Claim Count: {result['statistics']['claim_count']}")
    print(f"Entity Count: {result['statistics']['entity_count']}")

    print("\n" + "=" * 80)
    print("2️⃣  Get Claims Only (get_claims_only)".center(80))
    print("=" * 80)
    claims = get_claims_only(test_text)
    for i, claim in enumerate(claims, 1):
        print(f"{i}. {claim['text']} (Confidence: {claim['score']})")

    print("\n" + "=" * 80)
    print("3️⃣  Get Entities Only (get_entities_only)".center(80))
    print("=" * 80)
    entities = get_entities_only(test_text)
    for entity, entity_type in entities:
        print(f"• {entity} ({entity_type})")

    print("\n" + "=" * 80)
    print("4️⃣  Get Keywords Only (get_keywords_only)".center(80))
    print("=" * 80)
    keywords = get_keywords_only(test_text, top_n=8)
    print(f"Keywords: {', '.join(keywords)}")

    print("\n" + "=" * 80)
    print("5️⃣  Analyze Single Sentence (analyze_sentence)".center(80))
    print("=" * 80)
    sentence_result = analyze_sentence("Climate change is a serious threat.")
    print(f"Sentence: {sentence_result['text']}")
    print(f"Is Claim: {sentence_result['is_claim']}")
    print(f"Keywords: {sentence_result['keywords']}")

    print("\n✅ Test Completed!")
