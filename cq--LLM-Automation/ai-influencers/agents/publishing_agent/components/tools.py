import os
import json
import re
import textwrap
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pytz


# optional API libs (installed via requirements)
try:
    import tweepy
except Exception:
    tweepy = None

try:
    import praw
except Exception:
    praw = None

try:
    import requests
except Exception:
    requests = None

load_dotenv()

# env
TIMEZONE = os.getenv("TIMEZONE", "Africa/Casablanca")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() in ("1", "true", "yes")
# API tokens (left blank for manager)
API_KEY = os.getenv("API_KEY", "")
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")
MEDIUM_USER_ID = os.getenv("MEDIUM_USER_ID", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "CapQuantBot/0.1")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID", "")

# timezone helper
def get_tz():
    try:
        return pytz.timezone(TIMEZONE)
    except Exception:
        return pytz.timezone("Africa/Casablanca")

def ensure_json(path: Path):
    if not path.exists():
        path.write_text(json.dumps({"Schedule": []}, ensure_ascii=False, indent=4), encoding="utf-8")

# load/save schedule
def load_schedule(path: Path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "Schedule" in data:
        return data["Schedule"]
    if isinstance(data, list):
        return data
    return []

def save_schedule(path: Path, schedule_list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"Schedule": schedule_list}, f, ensure_ascii=False, indent=4)

# basic cleaners
def clean_text(text: str):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def enforce_limit(text: str, limit: int):
    if len(text) <= limit:
        return text
    return textwrap.shorten(text, width=limit, placeholder="...")

# -------------------------
# Simple content generators
# (convert X short posts into platform-specific forms)
# -------------------------
def generate_linkedin_from_x(entry):
    # produce a longer post: expand content with a professional intro and CTA
    base = clean_text(entry.get("Content", ""))
    hashtags = entry.get("Hashtags", "")
    # add short expansion sentences (deterministic)
    expansion = " This post explores why this topic matters to professionals and how teams can act on it."
    c = f"{base}{expansion}\n\n{hashtags}"
    return enforce_limit(c, 1200)

def generate_instagram_from_x(entry):
    base = clean_text(entry.get("Content", ""))
    tags = entry.get("Hashtags", "")
    # add emojis and line breaks
    caption = f"{base}\n\n✨ What do you think? \n\n{tags} \n\n📸 #CapQuant"
    return enforce_limit(caption, 2200)

def generate_medium_from_x(entry):
    # create a simple HTML article skeleton using the short content as an intro
    title = clean_text(entry.get("Content", "")[:80])
    intro = clean_text(entry.get("Content", ""))
    body = f"<h1>{title}</h1>\n<p>{intro}</p>\n<p>In this article we discuss practical steps and real-world examples — build, measure, iterate.</p>"
    # tags
    tags = [t.strip("# ") for t in (entry.get("Hashtags") or "").split() if t.startswith("#")]
    return {"title": title or "CapQuant Insight", "content": body, "tags": tags[:5]}

def generate_reddit_from_x(entry):
    # create a title and a body (reddit often expects title + body)
    title = clean_text(entry.get("Content", "")[:120])
    body = f"{clean_text(entry.get('Content',''))}\n\n{entry.get('Hashtags','')}\n\nWhat do you think?"
    return {"title": enforce_limit(title, 300), "body": body}

# -------------------------
# Post wrappers (respect DRY_RUN)
# They return a dict or simulated result.
# -------------------------
def post_to_twitter_sim(content):
    if DRY_RUN or tweepy is None:
        print(f"[DRY-RUN] Twitter -> {content}")
        return {"status": "simulated", "platform_id": None}
    # live path (requires proper keys)
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET,
        bearer_token=BEARER_TOKEN
    )
    resp = client.create_tweet(text=content)
    return {"status": "ok", "platform_id": getattr(resp, "data", {}).get("id")}

def post_to_medium_sim(title, content_html, tags):
    if DRY_RUN or requests is None or not MEDIUM_TOKEN or not MEDIUM_USER_ID:
        print(f"[DRY-RUN] Medium -> {title}\n{content_html[:200]}")
        return {"status": "simulated", "platform_id": None}
    headers = {"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"}
    payload = {"title": title, "contentFormat": "html", "content": content_html, "tags": tags, "publishStatus":"public"}
    r = requests.post(f"https://api.medium.com/v1/users/{MEDIUM_USER_ID}/posts", headers=headers, json=payload)
    return {"status": r.status_code, "platform_id": r.json()}

def post_to_reddit_sim(subreddit, title, body):
    if DRY_RUN or praw is None or not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET):
        print(f"[DRY-RUN] Reddit -> r/{subreddit} :: {title}\n{body[:200]}")
        return {"status": "simulated", "platform_id": None}
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET,
                         username=REDDIT_USERNAME, password=REDDIT_PASSWORD, user_agent=REDDIT_USER_AGENT)
    submission = reddit.subreddit(subreddit).submit(title=title, selftext=body)
    return {"status": "ok", "platform_id": submission.id}

def post_to_instagram_sim(image_url, caption):
    if DRY_RUN or requests is None or not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_PAGE_ID:
        print(f"[DRY-RUN] Instagram -> caption: {caption[:200]}")
        return {"status": "simulated", "platform_id": None}
    # simplified flow (create media + publish)
    r1 = requests.post(f"https://graph.facebook.com/v15.0/{INSTAGRAM_PAGE_ID}/media",
                       data={"image_url": image_url, "caption": caption, "access_token": INSTAGRAM_ACCESS_TOKEN})
    creation_id = r1.json().get("id")
    r2 = requests.post(f"https://graph.facebook.com/v15.0/{INSTAGRAM_PAGE_ID}/media_publish",
                       data={"creation_id": creation_id, "access_token": INSTAGRAM_ACCESS_TOKEN})
    return {"status": r2.status_code, "platform_id": r2.json()}

def post_to_linkedin_sim(content):
    if DRY_RUN or requests is None or not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_USER_ID:
        print(f"[DRY-RUN] LinkedIn -> {content[:300]}")
        return {"status": "simulated", "platform_id": None}
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}", "X-Restli-Protocol-Version":"2.0.0", "Content-Type":"application/json"}
    payload = {"author": LINKEDIN_USER_ID, "lifecycleState":"PUBLISHED",
               "specificContent":{"com.linkedin.ugc.ShareContent":{"shareCommentary":{"text":content},"shareMediaCategory":"NONE"}},
               "visibility":{"com.linkedin.ugc.MemberNetworkVisibility":"PUBLIC"}}
    r = requests.post(url, headers=headers, json=payload)
    return {"status": r.status_code, "platform_id": r.json()}

# -------------------------
# Helper to map run_dt
# -------------------------
def parse_run_dt(entry):
    date = entry.get("Date")
    time_str = entry.get("Time")
    if not date or not time_str:
        return None
    tz = get_tz()
    try:
        dt = datetime.fromisoformat(f"{date}T{time_str}")
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        return dt
    except Exception:
        try:
            dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            return tz.localize(dt)
        except Exception:
            return None
