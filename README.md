# 🔭 GitHub Profile Analyzer

A sleek, dark-themed GitHub profile analyzer built with Python, Streamlit, and Plotly.

## Features

- 📊 **Language breakdown** — pie chart of languages used across all repos
- 🔥 **Commit activity heatmap** — GitHub-style heatmap for last 90 days
- 📈 **Activity by type** — push, PR, issues, forks breakdown
- ⭐ **Top repositories** — ranked by stars with topics, language, and metadata
- 🕒 **Recent activity feed** — live timeline of public events
- 💡 **Dev Persona** — auto-generated description of the developer's profile
- 🏷️ **Topics cloud** — all repo topics aggregated

## Setup

### 1. Clone / download this folder

```bash
cd github-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

### 4. Open in browser

Streamlit will open `http://localhost:8501` automatically.

---

## GitHub Token (Optional but Recommended)

Without a token, the GitHub API allows **60 requests/hour** per IP.  
With a token, it allows **5,000 requests/hour**.

To get a token:
1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Select scope: `public_repo` (read-only is enough)
4. Copy and paste it into the app's token field

---

## Project Structure

```
github-analyzer/
├── app.py           # Main Streamlit UI
├── github_api.py    # GitHub API fetching & data processing
├── requirements.txt
└── README.md
```

## Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Web UI framework |
| Plotly | Interactive charts |
| GitHub REST API v3 | Data source |
| Python 3.9+ | Core language |
