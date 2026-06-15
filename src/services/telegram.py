import os
import logging
import httpx
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, config):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or config.telegram.get("bot_token")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID") or config.telegram.get("chat_id")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None

    def send_alert(self, paper: Dict) -> bool:
        """
        Sends a Telegram alert for a high-value 'arbitrage' paper.
        """
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not set. Skipping alert.")
            return False

        try:
            title = paper.get('title', 'Unknown Title')
            url = paper.get('url', 'No URL')
            arbitrage_score = paper.get('arbitrage_score', 0)
            reason = paper.get('arbitrage_reason', 'No reason provided.')

            message = (
                f"🚨 *Arbitrage Discovery Alert* 🚨\n\n"
                f"*Title:* {title}\n"
                f"*Score:* {arbitrage_score}/10\n"
                f"*Why:* {reason}\n\n"
                f"[Read Paper]({url})"
            )

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = httpx.post(self.base_url, json=payload, timeout=10.0)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent for paper: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

    def send_digest_summary(self, top_papers: List[Dict], total_papers: int, github_repos: Optional[List[Dict]] = None) -> bool:
        """
        Sends a daily digest summary with top gems to Telegram.
        """
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not set. Skipping digest.")
            return False

        try:
            lines = ["📬 *Daily AI Gems*", ""]
            
            # Papers section
            if top_papers:
                lines.append(f"*📄 Papers* ({len(top_papers)} hot from {total_papers} submissions)")
                for i, p in enumerate(top_papers[:5], 1):
                    title = p.get('title', 'Unknown')
                    cs = p.get('composite_score', 0)
                    arb = p.get('arbitrage_score', 0)
                    url = p.get('url', '')
                    lines.append(f"{i}. [{title}]({url}) — *{cs:.1f}* (A:{arb})")
                lines.append("")
            
            # GitHub repos section
            if github_repos:
                top_repos = sorted(github_repos, key=lambda r: r.get('composite', 0), reverse=True)[:5]
                lines.append(f"*💻 GitHub Trending* ({len(top_repos)} repos worth a look)")
                for i, r in enumerate(top_repos, 1):
                    name = r.get('name', 'Unknown')
                    cs = r.get('composite', 0)
                    url = r.get('url', f"https://github.com/{name}")
                    lines.append(f"{i}. [{name}]({url}) — *{cs:.1f}*")
                lines.append("")
            
            lines.append("_Full report in digests/_")
            
            message = "\n".join(lines)
            
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }

            response = httpx.post(self.base_url, json=payload, timeout=10.0)
            response.raise_for_status()
            
            logger.info("Daily digest summary sent to Telegram")
            return True

        except Exception as e:
            logger.error(f"Failed to send digest summary: {e}")
            return False
