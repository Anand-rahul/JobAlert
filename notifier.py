import time
import requests
from config import DISCORD_WEBHOOK_URL

def send_discord_notification(job: dict):
    if not DISCORD_WEBHOOK_URL:
        return

    score = job.get("match_score", 0)
    reasoning = job.get("ai_reasoning", "")
    
    description_body = f"**🔥 AI Match Score: {score}%**\n*{reasoning}*\n\n{job.get('snippet', '')}\n\n**[Apply Here ➔]({job.get('url', '#')})**"

    embed = {
        "title": f"🚀 {job.get('title', 'Job Alert')}",
        "url": job.get("url", "#"),
        "color": 3447003 if score < 80 else 3066993, # Green if highly matched, blue if standard
        "description": description_body,
        "fields": [
            {"name": "🏢 Company", "value": job.get("company_name", "Unknown"), "inline": True},
            {"name": "📍 Location", "value": job.get("location", "Unknown"), "inline": True},
            {"name": "🕒 Type", "value": job.get("job_type", "N/A"), "inline": True},
            {"name": "🔗 Source", "value": job.get("via", "Unknown"), "inline": True}
        ],
        "footer": {"text": "Hybrid Semantic Webhook Pipeline"},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
    except:
        pass
