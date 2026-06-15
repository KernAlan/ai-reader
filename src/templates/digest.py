"""Digest-specific HTML templates"""
from datetime import datetime
from typing import Dict, List

PAPER_STYLE = """
.paper {
    background: white;
    margin-bottom: 30px;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
}
.paper:hover {
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border-color: #cbd5e0;
}
.title {
    font-size: 1.3em;
    color: #2b6cb0;
    margin-bottom: 12px;
    font-weight: 600;
    line-height: 1.4;
}
.title a {
    text-decoration: none;
    color: inherit;
}
.title a:hover {
    color: #2c5282;
    text-decoration: underline;
}
.score {
    display: inline-block;
    padding: 4px 12px;
    background: var(--score-color);
    border-radius: 20px;
    font-weight: 500;
    margin: 8px 0;
    font-size: 0.9em;
}
.authors {
    color: #4a5568;
    font-size: 0.95em;
    margin-bottom: 12px;
}
.abstract {
    margin-top: 15px;
    color: #4a5568;
    line-height: 1.7;
    font-size: 0.95em;
}
"""

DIGEST_TEMPLATE = """
<div class="digest">
    <div class="header">
        <h2>AI Reader</h2>
        <p>Found {matching_papers} relevant papers out of {total_papers} new submissions</p>
        <div class="distribution">
            <strong>Score distribution:</strong> {score_distribution}
        </div>
    </div>
    
    <div class="highlights">
        <h3>🔥 Key Highlights</h3>
        {summary}
    </div>
    
    <div class="tier-hot">
        <h3>🔥 Hot (8+) — Worth your time today</h3>
        {hot_papers}
    </div>
    
    <div class="tier-warm">
        <h3>👀 Worth a Look (6-7.9)</h3>
        {warm_papers}
    </div>
    
    <div class="tier-cold">
        <details>
            <summary>📊 Background (<6) — {cold_count} papers with lower scores</summary>
            {cold_papers}
        </details>
    </div>
</div>
"""

PAPER_TEMPLATE = """
<div class="paper" style="opacity: {opacity}">
    <h3>{title}</h3>
    <div class="scores">
        <span class="score relevance">R:{relevance}/10</span>
        <span class="score importance">I:{importance}/10</span>
        <span class="score arbitrage">A:{arbitrage}/10</span>
        <span class="score composite comp-{comp_level}">{composite:.1f}</span>
    </div>
    <div class="abstract">{abstract}</div>
    <div class="meta">
        <a href="{url}" target="_blank">View on arXiv</a>
        {arbitrage_badge}
    </div>
</div>
"""

STYLE = """
.digest {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    margin-bottom: 30px;
}

.distribution {
    font-size: 0.9em;
    color: #4a5568;
    margin-top: 8px;
    padding: 8px 12px;
    background: #f7fafc;
    border-radius: 6px;
    border-left: 3px solid #4299e1;
}

.highlights {
    background: #f7fafc;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 40px;
    border-left: 4px solid #4299e1;
}

.tier-hot {
    margin-bottom: 40px;
}

.tier-hot h3 {
    color: #c53030;
    padding-bottom: 10px;
    border-bottom: 2px solid #fc8181;
}

.tier-warm {
    margin-bottom: 40px;
}

.tier-warm h3 {
    color: #dd6b20;
    padding-bottom: 10px;
    border-bottom: 2px solid #fbd38d;
}

.tier-warm .paper {
    opacity: 0.85;
}

.tier-warm .abstract {
    display: none;
}

.tier-cold {
    margin-bottom: 20px;
}

.tier-cold summary {
    cursor: pointer;
    padding: 10px;
    background: #f7fafc;
    border-radius: 6px;
    font-weight: 600;
    color: #4a5568;
}

.tier-cold .paper {
    opacity: 0.65;
}

.tier-cold .abstract {
    display: none;
}

.paper {
    background: white;
    margin-bottom: 30px;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.scores {
    display: flex;
    gap: 8px;
    margin: 12px 0;
    flex-wrap: wrap;
}

.score {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
}

.score.relevance {
    background: #c6f6d5;
    color: #22543d;
}

.score.importance {
    background: #bee3f8;
    color: #2a4365;
}

.score.arbitrage {
    background: #fefcbf;
    color: #744210;
}

.score.composite {
    background: #e2e8f0;
    color: #4a5568;
}

.score.composite.comp-high {
    background: #c53030;
    color: white;
}

.score.composite.comp-mid {
    background: #dd6b20;
    color: white;
}

.arbitrage-badge {
    display: inline-block;
    background: #ffd700;
    color: #1a202c;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    font-weight: 600;
    margin-left: 10px;
}
"""

def get_score_class(score: float) -> str:
    """Get composite score CSS class"""
    if score >= 8.5:
        return "high"
    elif score >= 6:
        return "mid"
    return "low"


def render_paper(paper: dict) -> str:
    """Render a single paper"""
    relevance = paper.get('relevance', 0)
    importance = paper.get('importance', 0)
    arbitrage = paper.get('arbitrage_score', 0)
    composite = paper.get('composite_score', (relevance + importance) / 2)
    
    # Lower opacity for low-scoring papers, full for high
    if composite >= 8:
        opacity = 1.0
    elif composite >= 6:
        opacity = 0.85
    else:
        opacity = 0.65
    
    # Arbitrage badge for high-arbitrage papers
    if arbitrage >= 8:
        arbitrage_badge = '<span class="arbitrage-badge">🔥 ARBITRAGE</span>'
    else:
        arbitrage_badge = ''
    
    return PAPER_TEMPLATE.format(
        title=paper['title'],
        abstract=paper['abstract'],
        relevance=relevance,
        importance=importance,
        arbitrage=arbitrage,
        composite=composite,
        comp_level=get_score_class(composite),
        opacity=opacity,
        arbitrage_badge=arbitrage_badge,
        url=paper.get('url', f"https://arxiv.org/abs/{paper.get('paper_id', '')}")
    )


def render_digest(papers: List[Dict], summary: str, total_papers: int, threshold: float, had_hallucination: bool) -> str:
    """Render the digest HTML with tiered display"""
    # Build score distribution summary
    dist = {i: 0 for i in range(0, 11)}
    for p in papers:
        cs = round(p.get('composite_score', 0))
        dist[cs] = dist.get(cs, 0) + 1
    
    dist_str = ", ".join(f"{k}: {v}" for k, v in sorted(dist.items()) if v > 0)
    
    # Split into tiers
    hot_papers = [p for p in papers if p.get('composite_score', 0) >= 8]
    warm_papers = [p for p in papers if 6 <= p.get('composite_score', 0) < 8]
    cold_papers = [p for p in papers if p.get('composite_score', 0) < 6]
    
    return DIGEST_TEMPLATE.format(
        matching_papers=len(papers),
        total_papers=total_papers,
        summary=summary,
        score_distribution=dist_str,
        hot_papers="\n".join(render_paper(p) for p in hot_papers) if hot_papers else "<p>No hot papers today.</p>",
        warm_papers="\n".join(render_paper(p) for p in warm_papers) if warm_papers else "<p>No papers in this range.</p>",
        cold_papers="\n".join(render_paper(p) for p in cold_papers) if cold_papers else "<p>No papers in this range.</p>",
        cold_count=len(cold_papers)
    ) 