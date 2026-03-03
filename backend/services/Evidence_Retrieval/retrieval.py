import asyncio
from typing import List, Dict, TypedDict
from tavily import TavilyClient
from urllib.parse import urlparse
import os
import logging
import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Tavily client with API key from environment
api_key = os.getenv("TAVILY_API_KEY", "")
client = TavilyClient(api_key=api_key)

try:
    semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Semantic similarity model loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load semantic model: {e}")
    semantic_model = None

class Reference(TypedDict):
    title: str
    url: str
    snippet: str
    weight: float  # Quality score 0.0-1.0
    semantic_score: float  # Relevance score 0.0-1.0
    domain_score: float  # Source credibility score 0.0-1.0


def enforce_source_diversity(references: List[Reference], max_per_domain: int = 2) -> List[Reference]:
    """
    Ensure diversity by limiting references per domain.
    
    Strategy:
    - References should already be sorted by weight (best first)
    - Take up to max_per_domain from each unique domain
    - This ensures highest quality sources are kept while enforcing diversity
    """

    domain_counts = {}
    diverse_refs = []

    for ref in references:
        try:
            parsed = urlparse(ref['url'])
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
        except Exception as e:
            logger.warning(f"Failed to parse URL '{ref['url']}': {e}")
            domain = "unknown"
        
        count = domain_counts.get(domain, 0)
        if count < max_per_domain:
            diverse_refs.append(ref)
            domain_counts[domain] = count + 1
        
    return diverse_refs

def calculate_semantic_relevance(claim: str, snippet: str) -> float:
    """
    Calculate how semantically relevant the evidence snippet is to the claim.
    Uses sentence embeddings and cosine similarity.
    Returns a score from 0.0 (not relevant) to 1.0 (highly relevant).
    """

    if semantic_model is None: return 0.75

    try:
        claim_embedding = semantic_model.encode(claim, convert_to_tensor=False)
        snippet_embedding = semantic_model.encode(snippet[:512], convert_to_tensor=False)

        dot_product = np.dot(claim_embedding, snippet_embedding)
        norm_claim = np.linalg.norm(claim_embedding)
        norm_snippet = np.linalg.norm(snippet_embedding)

        if norm_claim == 0 or norm_snippet == 0: return 0.75

        cosine_similarity = dot_product / (norm_claim * norm_snippet) # similarity measure
        normalized_score = max(0.0, min(1.0, cosine_similarity))
        return float(normalized_score)

    except Exception as e:
        logger.warning(f"Failed to calculate semantic relevance: {e}")
        return 0.75



def calculate_evidence_weight(url: str, title: str = "") -> float:
    """
    Calculate quality weight for evidence based on source credibility.
    Returns a score from 0.0 (low quality) to 1.0 (high quality).
    """

    url_lower = url.lower()
    title_lower = title.lower()
    
    # High credibility sources (0.9-1.0)
    high_credibility = [
        '.gov', '.edu',  # Government and educational institutions
        'reuters.com', 'apnews.com', 'ap.org',  # News agencies
        'bbc.com', 'bbc.co.uk',  # BBC
        'nature.com', 'science.org', 'sciencedirect.com',  # Scientific journals
        'nih.gov', 'cdc.gov', 'who.int',  # Health authorities
        'nytimes.com', 'washingtonpost.com', 'wsj.com',  # Major newspapers
        'economist.com', 'ft.com'  # Financial/economic sources
    ]
    
    # Medium credibility sources (0.65-0.80)
    medium_credibility = [
        'wikipedia.org', 'britannica.com',  # Encyclopedias
        '.org',  # Non-profit organizations (general)
        'guardian.com', 'theguardian.com',  # The Guardian
        'cnbc.com', 'bloomberg.com',  # Business news
        'nationalgeographic.com', 'scientificamerican.com'  # Science magazines
    ]
    
    # Low credibility indicators (0.2-0.4)
    low_credibility = [
        'blog', 'forum', 'reddit.com',
        'quora.com', 'answers.com',
        'wordpress.com', 'blogspot.com',
        'medium.com'  # User-generated content
    ]
    
    # Check for high credibility
    for domain in high_credibility:
        if domain in url_lower:
            return 1.0 if domain.startswith('.gov') or domain.startswith('.edu') else 0.95
    
    # Check for medium credibility
    for domain in medium_credibility:
        if domain in url_lower:
            if domain == '.org':
                return 0.80  # Generic .org
            return 0.90
    
    # Check for low credibility
    for indicator in low_credibility:
        if indicator in url_lower or indicator in title_lower:
            return 0.30
    
    # Default: uncertain quality
    return 0.60

# Retrieval Function using Tavily API
async def retrieve_references(claims: List[str]) -> Dict[str, List[Reference]]:
    """
    Retrieve evidence for claims using Tavily Search API.
    Returns a dictionary mapping each claim to a list of reference snippets.
    """
    logger.info(f"Starting evidence retrieval for {len(claims)} claim(s)")
    all_references: Dict[str, List[Reference]] = {}
    max_results = 5
    
    for claim in claims:
        logger.info(f"Retrieving evidence for claim: '{claim[:100]}...'") if len(claim) > 100 else logger.info(f"Retrieving evidence for claim: '{claim}'")
        try:
            # Search for evidence using Tavily with advanced search
            response = client.search(
                query=claim,
                max_results=max_results,
                search_depth="advanced",  # Use advanced search for comprehensive results
                include_raw_content=False # Don't need full HTML
            )
            
            references: List[Reference] = []
            
            for result in response.get("results", []):
                content = result.get("content", "")
                # Take first 600 characters for richer context
                if len(content) > 600:
                    content = content[:600]
                    last_period = content.rfind(".")
                    if last_period > 300:
                        content = content[:last_period + 1]
                
                ref_url = result.get("url", "")
                ref_title = result.get("title", "Source")

                domain_weight = calculate_evidence_weight(ref_url, ref_title)
                relevance_weight = calculate_semantic_relevance(claim, content)
                ref_weight = (domain_weight * 0.6) + (relevance_weight * 0.4)
                if relevance_weight < 0.3: ref_weight *= 0.7
                
                references.append({
                    "title": ref_title,
                    "url": ref_url,
                    "snippet": content,
                    "weight": ref_weight,
                    "semantic_score": relevance_weight,
                    "domain_score": domain_weight
                })
            
            # Sort by weight (highest quality first)
            references.sort(key=lambda x: x['weight'], reverse=True)
            references = enforce_source_diversity(references, max_per_domain=2)
            
            all_references[claim] = references
            avg_weight = sum(r['weight'] for r in references) / len(references) if references else 0
            logger.info(f"Retrieved {len(references)} evidence snippets for claim (avg quality: {avg_weight:.2f})")
            
        except Exception as e:
            # Return error information if search fails
            logger.error(f"Failed to retrieve evidence for claim: {str(e)}")
            all_references[claim] = [
                {
                    "title": "tavily_error",
                    "url": "tavily://error",
                    "snippet": f"Error retrieving evidence: {str(e)}",
                }
            ]
    
    return all_references

# Synchronous helper wrapper for convenience in scripts/tests
def retrieve_references_sync(claims: List[str]) -> Dict[str, List[Reference]]:
    return asyncio.run(retrieve_references(claims))


