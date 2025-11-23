**Unified Documentation for the Multi-Platform Publishing Automation System**


# **1. Overview**

The Publishing Agent is a unified system that automatically **reads content schedules**, **generates posts**, and **publishes them** across multiple platforms:

* **X (Twitter)**
* **LinkedIn**
* **Instagram**
* **Medium**
* **Reddit**

The system uses **internal scheduling**, meaning posts are triggered at the exact date/time specified in each platform’s schedule JSON file.

This documentation covers:

* Folder structure
* How the system works
* How to run it locally
* How scheduling operates
* How to retrieve API keys 
* Required .env configuration
* Platform limitations
* Deployment notes

Everything is ready and production-ready except API keys, which must be supplied by account owner
As they get updated each time and verification is needed so as you own the account it would be working fine.

---

# **2. Project Structure**

```
publishing-agent/
│
├─ components/
│   ├─ nodes.py               # prepare_post(), publish_post() logic
│   ├─ config.py              # SCHEDULE_PATH + routing
│   ├─ tools.py               # helpers, formatters, generators
│   ├─ state.py               # unified PublishState()
│
├─ schedules/
│   ├─ Content_Schedule_X.json
│   ├─ Content_Schedule_LinkedIn.json
│   ├─ Content_Schedule_Instagram.json
│   ├─ Content_Schedule_Medium.json
│   └─ Content_Schedule_Reddit.json
│
├─ prompts/
│   ├─ publish_twitter_prompt.txt
│   ├─ publish_instagram_prompt.txt
│   └─ schedule_prompt.txt
│
├─ graph.py                   # master scheduler
├─ main.py                    # platform selector + routing
├─ .env                       # API keys (remaining to be filled)
├─ requirements.txt
└─ README.md (this file)
```


# **3. How the System Works**

### ✔ 1. Loads the selected platform

X, LinkedIn, Instagram, Medium, Reddit
→ chosen through `main.py`.

### ✔ 2. Reads its schedule JSON file

Example:

Content_Schedule_X.json

Each item has:

Date, Time, Content, Hashtags, posted flag

### ✔ 3. Generates/Formats content

Based on prompts and persona.

### ✔ 4. Posts automatically at the correct time

Uses **APScheduler**.s

### ✔ 5. Marks posts as “posted”

Avoids duplicates:

```
"posted": true
"posted_at": "2025-01-01T10:00:00"
```

### ✔ 6. Logs everything

Saved into:

```
publish_api_logs.csv
```

---

# **4. Running the System (LOCAL)**

## **A. Activate virtual environment**

```
./venv/Scripts/activate
```

## **B. DRY RUN (testing, no posting)**

```
$env:DRY_RUN="True"; python graph.py --dry-run
```

## **C. LIVE MODE (auto-posting)**

```
$env:DRY_RUN="False"; python graph.py
```

## **D. Post overdue posts immediately**

```
python graph.py --post-past
```

## **E. Test single-run mode**

```
python graph.py --once
```

---

# **5. Using main.py (Choose Platform)**

Run automation for one platform only:

```
python main.py --platform x
python main.py --platform linkedin
python main.py --platform instagram
python main.py --platform reddit
python main.py --platform medium
```

main.py automatically:

* Loads correct schedule
* Passes it into graph.py
* Runs scheduler

---


### How it works:

1. graph.py reads your schedule file
2. Compares each entry to current time
3. If overdue → optionally publish immediately (`--post-past`)
4. If upcoming → schedule APScheduler jobs
5. Scheduler runs in background and triggers publish_post() automatically

### Can all platforms run at the same time?

Yes.

Just run main.py multiple times in separate processes, or use a cloud service that runs multiple workers.

---

# **6. API Keys (Manager Must Provide)**

Because this involves **business accounts**, account owner can retrieve the tokens.

---

# **6.1 X (Twitter) API — FREE**

### Steps:

1. Visit [https://developer.twitter.com](https://developer.twitter.com)
2. Create App
3. Generate:

   * API_KEY
   * API_SECRET
   * ACCESS_TOKEN
   * ACCESS_TOKEN_SECRET
   * BEARER_TOKEN

Add to `.env`:

```
X_API_KEY=
X_API_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
X_BEARER_TOKEN=
```

Fully automatable.

---

# **6.2 Reddit API — FREE**

### Steps:

1. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **Create App → Script**
3. Add:

```
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=
```

Fully automatic posting (subreddit restrictions apply).

---

# **6.3 Medium API — FREE & Simple**

### Steps:

1. Go to [https://medium.com/me/settings](https://medium.com/me/settings)
2. Scroll to **Integration Tokens**
3. Create token
4. Also find your USER ID

Add to `.env`:

```
MEDIUM_TOKEN=
MEDIUM_USER_ID=
```

Fully automated.

---

# **6.4 LinkedIn API — RESTRICTED (Manager MUST approve)**

LinkedIn **does not allow public posting APIs** unless:

* Manager creates a LinkedIn App
* Manager associates the company page
* Manager grants `w_organization_social` permissions
* Manager generates OAuth access token manually

### Steps (Manager Only)

1. [https://www.linkedin.com/developers/apps](https://www.linkedin.com/developers/apps)
2. Create App
3. Add business page under **Associated Organizations**
4. Request these permissions:

```
r_organization_social
w_organization_social
```

5. Manager logs in → Generates **OAuth Access Token**

Add to `.env`:

```
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORG_ID=
```

⚠ Tokens expire — manager must refresh every 30–60 days.

---

# **6.5 Instagram API (Meta) — RESTRICTED**

Requires:

* Business Instagram account
* Connected Facebook Page
* Meta Developer App
* Manager approves permissions

### Steps:

1. [https://developers.facebook.com](https://developers.facebook.com)
2. Create App
3. Add:

   * Instagram Content Publishing
   * Instagram Basic Display
4. Manager logs in → Approves app
5. Get:

```
IG_APP_ID=
IG_APP_SECRET=
IG_ACCESS_TOKEN=
IG_BUSINESS_ACCOUNT_ID=
```

⚠ Tokens must be refreshed by manager.

---

# **7. .env Configuration**

Place in `/publishing-agent/.env`

```
# --- X ---
X_API_KEY=
X_API_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
X_BEARER_TOKEN=

# --- LinkedIn ---
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORG_ID=

# --- Instagram ---
IG_APP_ID=
IG_APP_SECRET=
IG_ACCESS_TOKEN=
IG_BUSINESS_ACCOUNT_ID=

# --- Medium ---
MEDIUM_TOKEN=
MEDIUM_USER_ID=

# --- Reddit ---
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=

# --- System ---
TIMEZONE=Africa/Casablanca
DRY_RUN=False
```

---

# **8. Platform Limitations (Important For Management)**

| Platform      | Free Posting        | Scheduling Allowed       | Notes                              |
| ------------- | ------------------- | ------------------------ | ---------------------------------- |
| **X**         | Yes                 | Yes (internal scheduler) | Full automation                    |
| **Reddit**    | Yes                 | Internal only            | Must respect subreddit rules       |
| **Medium**    | Yes                 | Internal only            | No time-based features on Medium   |
| **Instagram** | Yes (Business only) | Internal only            | Manager approval required          |
| **LinkedIn**  | Yes (restricted)    | Internal only            | Must use manager’s personal access |

**LinkedIn & Instagram require manager intervention** because they block developer access without explicit business admin approval.

---

# **9. Deployment (Cloud)**


Options:

* AWS EC2
* Azure App Service
* DigitalOcean Droplet
* Render
* Railway
* Docker container

Run the scheduler as a **background service** using:

```
pm2
supervisor
systemd
docker restart-policy
```
