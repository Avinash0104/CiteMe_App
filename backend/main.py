import os
import sys
import asyncio
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import services.Evidence_Retrieval.retrieval as retrieval
import services.Evidence_Retrieval.scoring as scoring
from services.Information_Extraction.api.nlp_api import analyze_sentence, analyze_text

class RetrievalRequest(BaseModel):
    text: str

class ReferenceModel(BaseModel):
    claim: str
    is_claim: bool
    verdict: str
    truth_score: float
    reasoning: str
    references: List[Dict[str, str]]


class RetrievalResponse(BaseModel):
    retrieved_references: List[ReferenceModel]


app = FastAPI(
    title="CiteMe Backend API",
    description="Pipeline",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("System warming up: Loading NLP models into memory...")
    await asyncio.to_thread(analyze_text, "System warmup sequence.")
    print("System ready! Models loaded.")

@app.get("/")
def root():
    return {
        "status": "CiteMe is running!",
        "version": "1.0.0",
    }

@app.post("/retrieve-references", response_model=RetrievalResponse)
async def handle_retrieval(message: RetrievalRequest):
    # 1. Use powerful tools developed by the NLP team for professional sentence segmentation and declaration checks.
    analysis_result = await asyncio.to_thread(analyze_text, message.text)

    if not analysis_result.get("success"):
        return RetrievalResponse(retrieved_references=[])

    claims_to_check = []
    sentences_info = []

    # 2. Iterate through the results after segmenting by subject and distinguish between Claim and non-Claim.
    for sent_data in analysis_result["sentences"]:
        text = sent_data["text"]
        is_claim = sent_data.get("is_claim", False)

        sentences_info.append({"text": text, "is_claim": is_claim})
        if is_claim:
            claims_to_check.append(text)

    # 3. Use travily to retrieval the real claim.
    retrieval_result = {}
    if claims_to_check:
        retrieval_result = await retrieval.retrieve_references(claims_to_check)

    # 4. LLM scores
    final_results = []
    for info in sentences_info:
        if info["is_claim"]:
            claim_text = info["text"]
            # Get the evidence.
            retrieved_refs = retrieval_result.get(claim_text, [])
            # let LLM scores
            score_result = scoring.check_claim(claim_text, retrieved_refs)

            final_results.append(
                ReferenceModel(
                    claim=claim_text,
                    is_claim=True,
                    verdict=score_result["verdict"],
                    truth_score=score_result["truth_score"],
                    reasoning=score_result["reasoning"],
                    references=retrieved_refs,
                )
            )
        else:
            final_results.append(
                ReferenceModel(
                    claim=info["text"],
                    is_claim=False,
                    verdict="Not Applicable",
                    truth_score=0.0,
                    reasoning="Not a factual claim.",
                    references=[],
                )
            )

    return RetrievalResponse(retrieved_references=final_results)

