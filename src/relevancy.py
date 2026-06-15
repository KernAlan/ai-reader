"""Paper relevancy scoring using LLMs"""
from typing import List, Dict, Tuple
import logging
from tqdm import tqdm

from .utils import (
    create_quick_scoring_prompt,
    process_scoring_response,
    openai_completion,
    OpenAIDecodingArguments
)

logger = logging.getLogger(__name__)

def score_papers(
    papers: List[Dict],
    interest: str,
    model_config: Dict,
    threshold: float = 7.5,
    arbitrage_interest: str = "",
    arbitrage_threshold: float = 8.5
) -> Tuple[List[Dict], bool]:
    """Score papers for relevance and importance — returns ALL with scores"""
    logger.info(f"Scoring {len(papers)} papers")
    
    # Split papers into chunks
    chunk_size = model_config.get("papers_per_batch", 8)
    paper_chunks = [papers[i:i+chunk_size] for i in range(0, len(papers), chunk_size)]
    
    # Score papers in chunks
    all_scored_papers = []
    had_hallucination = False
    
    for chunk in tqdm(paper_chunks, desc="Scoring papers"):
        prompt = create_quick_scoring_prompt(interest, chunk, arbitrage_interest=arbitrage_interest)
        response = openai_completion(
            prompt,
            OpenAIDecodingArguments(),
            model_name=model_config.get("name", "gpt-4"),
            provider=model_config.get("provider", "openai")
        )
        
        chunk_scored, chunk_hallu = process_scoring_response(
            chunk, 
            response, 
            threshold, 
            arbitrage_threshold=arbitrage_threshold
        )
        all_scored_papers.extend(chunk_scored)
        had_hallucination = had_hallucination or chunk_hallu
    
    # Log results
    logger.info(f"Papers processed: {len(all_scored_papers)}")
    
    # Log full score distribution
    relevance_dist = {i: 0 for i in range(1, 11)}
    importance_dist = {i: 0 for i in range(1, 11)}
    arbitrage_dist = {i: 0 for i in range(1, 11)}
    
    for p in all_scored_papers:
        rel_score = round(p["relevance"])
        imp_score = round(p["importance"])
        arb_score = round(p["arbitrage_score"])
        if 1 <= rel_score <= 10:
            relevance_dist[rel_score] += 1
        if 1 <= imp_score <= 10:
            importance_dist[imp_score] += 1
        if 1 <= arb_score <= 10:
            arbitrage_dist[arb_score] += 1
            
    logger.info(f"Relevance distribution: " + ", ".join(f"{k}:{v}" for k, v in relevance_dist.items() if v > 0))
    logger.info(f"Importance distribution: " + ", ".join(f"{k}:{v}" for k, v in importance_dist.items() if v > 0))
    logger.info(f"Arbitrage distribution:  " + ", ".join(f"{k}:{v}" for k, v in arbitrage_dist.items() if v > 0))
    
    # Sort by composite score descending
    all_scored_papers.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
    
    logger.info(f"Final: {len(all_scored_papers)} scored papers (all shown in digest)")
    return all_scored_papers, had_hallucination
