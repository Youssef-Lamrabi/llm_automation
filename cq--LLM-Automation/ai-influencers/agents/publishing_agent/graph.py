import traceback
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from components.config import (
    SCHEDULE_X, SCHEDULE_LINKEDIN, SCHEDULE_INSTAGRAM,
    SCHEDULE_MEDIUM, SCHEDULE_REDDIT, LOG_CSV
)
from components.tools import (
    load_schedule, save_schedule, parse_run_dt, DRY_RUN,
    generate_linkedin_from_x, generate_instagram_from_x,
    generate_medium_from_x, generate_reddit_from_x,
    post_to_twitter_sim, post_to_medium_sim, post_to_reddit_sim,
    post_to_instagram_sim, post_to_linkedin_sim
)

# helper logging
def append_log(row, path=LOG_CSV):
    import csv
    file_exists = Path(path).exists()
    header = ["scheduled_time", "run_time", "status", "message", "content_preview"]
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# -------------------------
# Utility: if platform schedule missing, auto-generate from X
# -------------------------
def ensure_platform_schedule_from_x(x_path: Path, platform_path: Path, transform_fn):
    x_list = load_schedule(x_path)
    if not x_list:
        return
    # if platform schedule exists and non-empty, do nothing
    existing = load_schedule(platform_path)
    if existing:
        return
    out = []
    for e in x_list:
        # build platform entry
        entry = {
            "Date": e.get("Date"),
            "Time": e.get("Time"),
            "Content": transform_fn(e) if isinstance(transform_fn(e), str) else transform_fn(e),
            "posted": False
        }
        out.append(entry)
    save_schedule(platform_path, out)
    print(f"[auto-gen] Created {platform_path} from X schedule ({len(out)} entries)")

# -------------------------
# Generic scheduler runner (similar to your earlier graph)
# -------------------------
def schedule_jobs_for_path(path: Path, publish_callable, preview_field="Content", once=True, post_past=False):
    schedule_list = load_schedule(path)
    if not schedule_list:
        print(f"[skip] No schedule at {path}")
        return
    now = datetime.now()
    past = []
    future = []
    for idx, entry in enumerate(schedule_list):
        if entry.get("posted"):
            continue
        dt = parse_run_dt(entry)
        if not dt:
            continue
        if dt <= now:
            past.append((idx, entry, dt))
        else:
            future.append((idx, entry, dt))
    print(f"[info] {path.name}: total={len(schedule_list)}, past={len(past)}, future={len(future)}")
    # post past immediately if requested and not dry
    if post_past and past and not DRY_RUN:
        for idx, entry, dt in past:
            try:
                content = entry.get(preview_field)
                resp = publish_callable(entry)
                entry["posted"] = True
                entry["posted_at"] = datetime.now().isoformat()
                save_schedule(path, schedule_list)
                append_log({"scheduled_time": dt.isoformat(), "run_time": datetime.now().isoformat(),
                            "status": "success", "message": str(resp)[:200], "content_preview": str(content)[:140]})
            except Exception as ex:
                append_log({"scheduled_time": dt.isoformat(), "run_time": datetime.now().isoformat(),
                            "status": "failed", "message": str(ex)[:200], "content_preview": str(entry.get(preview_field))[:140]})
    # schedule future jobs using a quick run (we use BlockingScheduler only if not dry and future exists)
    if DRY_RUN:
        for idx, entry, dt in future:
            print(f"[dry] would schedule at {dt.isoformat()} -> {entry.get(preview_field)[:120]}")
        return
    if not future:
        return
    executors = {"default": ThreadPoolExecutor(4)}
    scheduler = BlockingScheduler(executors=executors)
    for idx, entry, dt in future:
        def job_closure(e=entry, scheduled_time=dt, idx=idx):
            try:
                resp = publish_callable(e)
                e["posted"] = True
                e["posted_at"] = datetime.now().isoformat()
                save_schedule(path, load_schedule(path))  # reload & save
                append_log({"scheduled_time": scheduled_time.isoformat(), "run_time": datetime.now().isoformat(),
                            "status": "success", "message": str(resp)[:200], "content_preview": str(e.get(preview_field))[:140]})
                print(f"[job] posted idx {idx}")
            except Exception as ex:
                append_log({"scheduled_time": scheduled_time.isoformat(), "run_time": datetime.now().isoformat(),
                            "status": "failed", "message": str(ex)[:200], "content_preview": str(e.get(preview_field))[:140]})
                print(f"[job] failed idx {idx}: {ex}")
        scheduler.add_job(job_closure, "date", run_date=dt)
    print("[start] Starting scheduler (blocking) — will run future jobs")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[stop] Scheduler stopped")

# -------------------------
# publish wrappers used by schedule_jobs_for_path
# -------------------------
def publish_twitter_entry(entry):
    text = entry.get("Content")
    return post_to_twitter_sim(text)

def publish_linkedin_entry(entry):
    # transform if Content is a structure
    content = entry.get("Content") or ""
    # if Content is not long enough, keep it; else use as is
    return post_to_linkedin_sim(content)

def publish_instagram_entry(entry):
    # This system assumes an image_url field may exist; if not, we'll simulate a caption-only post
    caption = entry.get("Content")
    image_url = entry.get("ImageUrl", "")
    return post_to_instagram_sim(image_url, caption)

def publish_medium_entry(entry):
    data = entry.get("Content")
    if isinstance(data, dict):
        title = data.get("title")
        content_html = data.get("content")
        tags = data.get("tags", [])
    else:
        # fallback: create article skeleton
        title = "CapQuant Post"
        content_html = f"<p>{entry.get('Content','')}</p>"
        tags = []
    return post_to_medium_sim(title, content_html, tags)

def publish_reddit_entry(entry):
    subreddit = entry.get("Subreddit", "test")
    r = generate_reddit_from_x(entry) if not entry.get("title") else {"title": entry.get("title"), "body": entry.get("Content")}
    return post_to_reddit_sim(subreddit, r["title"], r["body"])

# -------------------------
# Per-platform run functions
# -------------------------
def run_twitter(dry_run=False):
    schedule_jobs_for_path(Path(SCHEDULE_X), publish_twitter_entry, preview_field="Content")

def run_linkedin(dry_run=False):
    # auto-generate LinkedIn schedule from X if missing
    ensure_platform_schedule_from_x(Path(SCHEDULE_X), Path(SCHEDULE_LINKEDIN), generate_linkedin_from_x)
    schedule_jobs_for_path(Path(SCHEDULE_LINKEDIN), publish_linkedin_entry, preview_field="Content")

def run_instagram(dry_run=False):
    ensure_platform_schedule_from_x(Path(SCHEDULE_X), Path(SCHEDULE_INSTAGRAM), generate_instagram_from_x)
    schedule_jobs_for_path(Path(SCHEDULE_INSTAGRAM), publish_instagram_entry, preview_field="Content")

def run_medium(dry_run=False):
    # produce dict content for Medium entries
    # auto-generate if not exists
    x_list = load_schedule(Path(SCHEDULE_X))
    existing = load_schedule(Path(SCHEDULE_MEDIUM))
    if not existing and x_list:
        out = []
        for e in x_list:
            d = generate_medium_from_x(e)
            out.append({"Date": e.get("Date"), "Time": e.get("Time"), "Content": d, "posted": False})
        save_schedule(Path(SCHEDULE_MEDIUM), out)
        print(f"[auto-gen] Medium schedule created ({len(out)})")
    schedule_jobs_for_path(Path(SCHEDULE_MEDIUM), publish_medium_entry, preview_field="Content")

def run_reddit(dry_run=False):
    ensure_platform_schedule_from_x(Path(SCHEDULE_X), Path(SCHEDULE_REDDIT), generate_reddit_from_x)
    schedule_jobs_for_path(Path(SCHEDULE_REDDIT), publish_reddit_entry, preview_field="Content")
