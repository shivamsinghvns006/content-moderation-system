# Automated Content Moderation System

A working prototype of an automated content-moderation platform, built for the
VIT Internship project brief. It analyzes user-submitted **text** and
**images**, automatically approves/flags/rejects them, and gives human
moderators a dashboard to review anything borderline.

---

## 1. Tech Stack (and why)

| Layer            | Technology                | Why |
|------------------|----------------------------|-----|
| Backend / API    | Python + Flask             | Lightweight, easy to read, no cloud account needed to run it |
| Database         | SQLite + SQLAlchemy        | File-based DB, zero setup. Plays the role of Azure Cosmos DB in the original design |
| Text moderation  | `better-profanity` + custom rule-based toxicity/spam scorer | Runs instantly, fully explainable, no API key required |
| Image moderation | `Pillow` (format/size/corruption checks) | Real, working checks without needing a heavy ML model |
| Frontend         | HTML + CSS + vanilla JavaScript | Simple dashboard, no build step required |

> **About Azure:** The original brief recommends Azure AI Vision, Azure AI
> Language, Azure Functions, Cosmos DB, and Azure Monitor. This project keeps
> that architecture in spirit, but swaps in local equivalents so it runs
> immediately with no cloud account. Every file that would normally call
> Azure has a clearly marked stub function (`analyze_with_azure`,
> `analyze_with_azure_vision`) showing exactly how to plug in the real
> service later — see `moderation/text_moderator.py` and
> `moderation/image_moderator.py`.

---

## 2. Project Structure

```
content-moderation-system/
├── app.py                     # Main entry point - run this file
├── config.py                  # All settings/thresholds in one place
├── models.py                  # Database tables (SQLAlchemy)
├── requirements.txt           # Python dependencies
├── .env.example                # Copy to .env to add Azure keys later
├── moderation/
│   ├── text_moderator.py      # Text analysis logic
│   └── image_moderator.py     # Image analysis logic
├── routes/
│   ├── api.py                 # REST API endpoints
│   └── dashboard.py           # Web dashboard routes
├── templates/                 # HTML pages (Jinja2)
├── static/                    # CSS + JS for the dashboard
├── database/                  # moderation.db is created here automatically
├── uploads/                   # uploaded images are stored here automatically
└── tests/
    └── test_moderation.py     # Unit tests for the moderation logic
```

---

## 3. How to Run This in VS Code

### Step 1 — Open the folder
Unzip the project and open the `content-moderation-system` folder in VS Code
(`File > Open Folder...`).

### Step 2 — Create a virtual environment (recommended)
Open a terminal in VS Code (`` Ctrl+` ``) and run:

```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

### Step 5 — Open it in your browser
Go to **http://127.0.0.1:5000**

- `/dashboard` — moderator dashboard (flagged content queue, stats, reports)
- `/try-it` — manually test text/image moderation
- `/audit-log` — full audit trail

The SQLite database (`database/moderation.db`) and any uploaded images are
created automatically the first time you run the app — nothing to configure.

---

## 4. Testing the API Directly

You can also call the API without the browser, e.g. with `curl`:

```bash
curl -X POST http://127.0.0.1:5000/api/moderate/text \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"This is a great community, thanks everyone!\"}"
```

```bash
curl -X POST http://127.0.0.1:5000/api/moderate/image \
  -F "image=@/path/to/some_picture.jpg"
```

### All API Endpoints
| Method | Endpoint                  | Purpose |
|--------|---------------------------|---------|
| POST   | `/api/moderate/text`      | Submit text for real-time moderation |
| POST   | `/api/moderate/image`     | Submit an image for moderation |
| POST   | `/api/report`             | Let a user report inappropriate content |
| GET    | `/api/records`            | List moderation records (filter by `?decision=` `?content_type=`) |
| GET    | `/api/stats`              | Summary counts (used by the dashboard) |

---

## 5. Running the Unit Tests

```bash
python -m unittest discover tests
```

---

## 6. How the Moderation Decision Works

1. **Text** is checked for: profanity, a weighted toxic-keyword score,
   excessive capital letters, and spam patterns (repeated links, repeated
   characters, "buy now" style phrases).
2. **Images** are checked for: valid/allowed format, file corruption,
   suspicious dimensions (e.g. 1×1 tracking pixels), and oversized files.
3. Based on the checks, each item gets one of three decisions:
   - **approved** — published immediately
   - **flagged** — sent to the human moderator dashboard for review
   - **rejected** — blocked automatically
4. Every decision (automated or human) is written to the **audit log** table
   for transparency and compliance, satisfying the brief's requirement to
   "maintain audit logs for transparency and compliance."

---

## 7. Mapping Back to the Original Project Brief

| Brief requirement | Where it's implemented |
|---|---|
| Real-time content analysis and filtering | `moderation/text_moderator.py`, `moderation/image_moderator.py` |
| Dashboard for human moderators | `templates/dashboard.html`, `routes/dashboard.py` |
| High accuracy / minimize false positives | Tunable thresholds in `config.py` |
| User reporting and feedback | `POST /api/report` |
| Integrate with content platforms via APIs | Full REST API in `routes/api.py` |
| Maintain audit logs | `AuditLog` model + `/audit-log` page |

---

## 8. Next Steps (Future Scope)

- Swap the local text/image logic for real **Azure AI Language** and
  **Azure AI Vision** calls (stub functions are already written).
- Move from SQLite to **Azure Cosmos DB** for production-scale storage.
- Deploy the Flask app as an **Azure Function** for serverless scaling.
- Add **Azure Monitor** for performance/accuracy dashboards in production.
