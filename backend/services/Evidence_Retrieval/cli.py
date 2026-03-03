import argparse
from typing import List, Dict

import scoring
import retrieval


def run_once(claim: str) -> None:
    results_map = retrieval.retrieve_references_sync([claim])
    refs: List[Dict[str, str]] = results_map.get(claim, [])
    score = scoring.check_claim(claim, refs)

    print("\n=== Claim ===")
    print(claim)
    print("\n=== Verdict ===")
    print(f"Verdict:      {score.get('verdict')}")
    print(f"Truth Score:  {score.get('truth_score')}")
    print(f"(0.0-0.5 = False, 0.5 = Uncertain, 0.5-1.0 = True)")
    
    # Show reasoning if available
    if score.get('reasoning'):
        print(f"\n=== Reasoning ===")
        print(score.get('reasoning'))
    
    # Show references
    if refs:
        print("\n=== Evidence Sources ===")
        for i, r in enumerate(refs, start=1):
            title = r.get("title") or "reference"
            url = r.get("url") or ""
            snippet = r.get("snippet") or ""
            print(f"[{i}] {title}")
            if url and url != "tavily://summary":
                print(f"    URL: {url}")
            print(f"    {snippet[:200]}..." if len(snippet) > 200 else f"    {snippet}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Run evidence retrieval + scoring for a claim")
    parser.add_argument("claim", help="Claim text to evaluate.")
    args = parser.parse_args()

    claim_text = args.claim
    if not claim_text:
        parser.error("Please provide a claim argument")
    run_once(claim_text)


if __name__ == "__main__":
    main()


