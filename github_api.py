import requests
from datetime import datetime, timedelta
from collections import defaultdict

BASE_URL = "https://api.github.com"

def get_headers(token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def fetch_user(username, token=None):
    r = requests.get(f"{BASE_URL}/users/{username}", headers=get_headers(token))
    if r.status_code == 404:
        return None, "User not found."
    if r.status_code == 403:
        return None, "Rate limit exceeded. Add a GitHub token to continue."
    if r.status_code != 200:
        return None, f"GitHub API error: {r.status_code}"
    return r.json(), None

def fetch_repos(username, token=None):
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"{BASE_URL}/users/{username}/repos",
            headers=get_headers(token),
            params={"per_page": 100, "page": page, "sort": "updated"}
        )
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        if len(data) < 100:
            break
    return repos

def fetch_events(username, token=None):
    events = []
    for page in range(1, 4):  # GitHub limits to 90 days / 300 events
        r = requests.get(
            f"{BASE_URL}/users/{username}/events/public",
            headers=get_headers(token),
            params={"per_page": 100, "page": page}
        )
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        events.extend(data)
    return events

def process_repos(repos):
    languages = defaultdict(int)
    topics_all = []
    total_stars = 0
    total_forks = 0
    original_repos = []
    forked_repos = []

    for repo in repos:
        if repo.get("fork"):
            forked_repos.append(repo)
        else:
            original_repos.append(repo)

        if repo.get("language"):
            languages[repo["language"]] += 1

        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        topics_all.extend(repo.get("topics", []))

    top_repos = sorted(original_repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:6]

    return {
        "languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "original_count": len(original_repos),
        "forked_count": len(forked_repos),
        "top_repos": top_repos,
        "topics": list(set(topics_all)),
    }

def process_events(events):
    commit_days = defaultdict(int)
    event_types = defaultdict(int)
    recent_activity = []

    for event in events:
        created_at = event.get("created_at", "")
        if created_at:
            day = created_at[:10]
            event_type = event.get("type", "")
            event_types[event_type] += 1

            if event_type == "PushEvent":
                commits = event.get("payload", {}).get("commits", [])
                commit_days[day] += len(commits)
            else:
                commit_days[day] += 0  # ensure day is recorded

        if len(recent_activity) < 10:
            recent_activity.append({
                "type": event.get("type", ""),
                "repo": event.get("repo", {}).get("name", ""),
                "created_at": created_at,
            })

    return {
        "commit_days": dict(commit_days),
        "event_types": dict(event_types),
        "recent_activity": recent_activity,
    }

def get_account_age(created_at):
    created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    delta = datetime.utcnow() - created
    years = delta.days // 365
    months = (delta.days % 365) // 30
    if years > 0:
        return f"{years}y {months}m"
    return f"{months} months"

def generate_persona(user, repo_data, event_data):
    languages = list(repo_data["languages"].keys())
    stars = repo_data["total_stars"]
    original = repo_data["original_count"]
    commits = sum(event_data["commit_days"].values())

    lang_str = ", ".join(languages[:3]) if languages else "various languages"

    if stars > 100:
        star_label = "🌟 Open-source contributor with significant community impact"
    elif stars > 20:
        star_label = "⭐ Growing open-source presence"
    else:
        star_label = "🔧 Focused builder (more about code than clout)"

    if commits > 50:
        activity = "highly active coder"
    elif commits > 10:
        activity = "consistent contributor"
    else:
        activity = "selective but thoughtful coder"

    return f"{star_label} — a {activity} primarily working in {lang_str} with {original} original projects."
