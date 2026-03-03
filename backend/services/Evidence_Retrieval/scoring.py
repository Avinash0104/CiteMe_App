from typing import Dict, List
import os
import requests
from groq import Groq
import logging
from urllib.parse import urlparse

#from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

"""
Hybrid scoring: LLM provides verdict, score and reasoning, system calculates truth score.
Evidence from Tavily acts as proof supporting/contradicting the claim.
Uses local Ollama or Groq for LLM inference.
"""

# Initialize Groq client (optional - for team testing)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

def analyze_evidence_reliability(references: List[Dict], claim: str) -> Dict:
    """
    Analyze evidence for contradictions and consensus
    Consensus Scoring - How many independent high-quality sources agree?
    Returns reliability analysis with penalty multiplier.
    """

    if not references or len(references) < 1:
        return {
            'consensus_level': 'insufficient',
            'unique_quality_sources': 0,
            'multiplier': 0.7,  # Penalty for no evidence
            'warning': 'Insufficient evidence for verification'
        }

    unique_domains = set()
    high_quality_sources = []

    for ref in references:
        try:
            domain = urlparse(ref.get('url', '')).netloc.lower()
            domain = domain.replace('www.', '')
        except:
            domain = 'unknown'

        domain_weight = ref.get('domain_score', 0.5)
        if domain_weight >= 0.85:
            if domain not in unique_domains:
                unique_domains.add(domain)
                high_quality_sources.append({
                    'domain': domain,
                    'title': ref.get('title', ''),
                    'weight': domain_weight
                })

    num_quality_sources = len(high_quality_sources)

    if num_quality_sources >= 4:
        multiplier = 1.0
    elif num_quality_sources == 3:
        multiplier = 0.97
    elif num_quality_sources == 2:
        multiplier = 0.95
    elif num_quality_sources == 1:
        multiplier = 0.90
    else:
        multiplier = 0.85
    
    result = {
        'unique_quality_sources': num_quality_sources,
        'quality_source_list': [s['domain'] for s in high_quality_sources],
        'multiplier': multiplier
    }

    return result

def groq_analyze(prompt: str, system_message: str) -> str:
    """Call Groq API for LLM analysis (for team testing)"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set. Get a free key at: https://console.groq.com/keys")
    
    logger.debug("Using Groq API for LLM analysis")
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=300
    )
    
    return response.choices[0].message.content


def local_analyze(prompt: str, system_message: str) -> str:
    """Call local Ollama for LLM analysis"""
    logger.debug("Using local Ollama for LLM analysis")
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.1:8b",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}. Make sure Ollama is running with 'ollama serve' and llama3.1:8b model is available.")


# LLM determines verdict and reasoning, system calculates confidence score.
def check_claim(claim: str, references: List[Dict[str, str]]) -> Dict[str, any]:
    logger.info(f"Analyzing claim: '{claim[:100]}...'") if len(claim) > 100 else logger.info(f"Analyzing claim: '{claim}'")
    logger.info(f"Number of evidence snippets: {len(references)}")
    
    if not references:
        logger.warning("No evidence provided for fact-checking")
        return {
            "truth_score": 0.00,
            "verdict": "No Evidence",
            "reasoning": "No evidence was provided for fact-checking."
        }

    reliability = analyze_evidence_reliability(references, claim)
    
    # Calculate average evidence quality
    weights = [ref.get('weight', 0.5) for ref in references]
    avg_weight = sum(weights) / len(weights)
    
    logger.info(f"Average evidence quality: {avg_weight:.2f}")
    
    # Build evidence context from Tavily results with quality indicators (Option D)
    evidence_items = []
    for i, ref in enumerate(references[:5]):  # Max 5 pieces of evidence
        weight = ref.get('weight', 0.5)
        quality_label = "High" if weight >= 0.85 else "Medium" if weight >= 0.65 else "Low"
        evidence_items.append(
            f"Evidence {i+1} [{quality_label} Quality: {weight:.1f}/1.0] ({ref.get('title', 'Source')}): {ref['snippet'][:400]}"
        )
    
    evidence_text = "\n\n".join(evidence_items)
    
    # Enhanced prompt - ask LLM to provide truth score that measures claim truthfulness
    prompt = f"""Analyze this statement and rate HOW TRUE the statement itself is based on the evidence.

                STATEMENT: {claim}

                SOURCES:
                {evidence_text}

                Your job: Rate how TRUE or FALSE the statement is on a scale from 0.00 to 1.00.

                TRUTH_SCORE scale:
                - 0.90-1.00 = Statement is definitely TRUE (strong evidence supports it)
                - 0.70-0.89 = Statement is mostly TRUE (good evidence supports it)
                - 0.51-0.69 = Statement is somewhat TRUE (weak/mixed evidence leans toward true)
                - 0.50 = Uncertain (evidence is balanced or insufficient)
                - 0.31-0.49 = Statement is somewhat FALSE (weak/mixed evidence leans toward false)
                - 0.10-0.30 = Statement is mostly FALSE (good evidence contradicts it)
                - 0.00-0.09 = Statement is definitely FALSE (strong evidence contradicts it)

                Respond ONLY in this format:
                VERDICT: [True/False/Uncertain]
                TRUTH_SCORE: [0.00 to 1.00 - rate how true the STATEMENT is]
                REASONING: [Brief explanation of why the claim is true/false/uncertain based on reasoning. Consider the quality of sources when making your assessment.]
                """
    
    try:
        # Use local LLM by default, Groq available for team testing
        result_text = groq_analyze(prompt, "You are a fact-checking assistant. Analyze evidence objectively and provide clear verdicts.")
        
        # Parse the LLM response
        verdict = "Uncertain"
        truth_score = 0.50
        reasoning = ""
        
        for line in result_text.split('\n'):
            line = line.strip()
            if line.startswith("VERDICT:"):
                verdict = line.split(":", 1)[1].strip()
            elif line.startswith("TRUTH_SCORE:"):
                # Extract truth score from LLM response
                score_text = line.split(":", 1)[1].strip()
                truth_score = float(score_text)
                truth_score = max(0.0, min(1.0, truth_score))
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
        
        # Store original LLM score for logging
        llm_score = truth_score
        
        # post-processing adjustment based on evidence quality
        quality_factor = 0.7 + (0.3 * avg_weight)
        # If very few sources, be more conservative
        if len(references) < 3:
            quality_factor = max(quality_factor, 0.85)  # Less aggressive penalty
        
        # Apply quality adjustment & reliability multiplier
        truth_score = llm_score * quality_factor * reliability['multiplier']
        truth_score = max(0.0, min(1.0, truth_score))  # Clamp to [0, 1]
        
        logger.info(f"LLM Score: {llm_score:.2f} | Quality Factor: {quality_factor:.2f} | Final Score: {truth_score:.2f}")
        logger.info(f"Verdict: {verdict}")
        logger.info(f"Reasoning: {reasoning}")
        
        result = {
            "truth_score": round(truth_score, 3),
            "llm_score": round(llm_score, 3),  # Include original score for transparency
            "quality_factor": round(quality_factor, 3),
            "verdict": verdict,
            "reasoning": reasoning
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error during claim analysis: {str(e)}")
        return {
            "truth_score": 0.00,
            "verdict": "Error",
            "reasoning": f"An error occurred: {str(e)}"
        }