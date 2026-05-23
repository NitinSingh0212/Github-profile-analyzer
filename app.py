import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

from github_api import (
    fetch_user, fetch_repos, fetch_events,
    process_repos, process_events,
    get_account_age, generate_persona
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Profile Analyzer",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="stMarkdown"], [class*="stText"] {
    font-family: 'Inter', sans-serif !important;
}

h1, h2, h3 { font-family: 'JetBrains Mono', monospace; }

.hero-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.4rem;
    font-weight: 600;
    color: #e6edf3;
    margin-bottom: 0;
    letter-spacing: -1px;
}

.hero-sub {
    font-family: 'Inter', sans-serif;
    color: #7d8590;
    font-size: 1rem;
    margin-top: 4px;
    font-weight: 300;
}

.stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}

.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #58a6ff;
    display: block;
}

.stat-label {
    font-size: 0.78rem;
    color: #7d8590;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.persona-card {
    background: linear-gradient(135deg, #1a2332 0%, #161b22 100%);
    border: 1px solid #388bfd44;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 16px 0;
    color: #cdd9e5;
    font-size: 0.95rem;
    line-height: 1.7;
}

.repo-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}

.repo-card:hover { border-color: #58a6ff55; }

.repo-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: #58a6ff;
    font-weight: 600;
}

.repo-desc {
    font-size: 0.83rem;
    color: #7d8590;
    margin-top: 4px;
    line-height: 1.5;
}

.tag {
    display: inline-block;
    background: #1f2d3d;
    color: #58a6ff;
    border: 1px solid #388bfd44;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin: 3px 3px 3px 0;
    font-family: 'JetBrains Mono', monospace;
}

.section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #7d8590;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
    margin: 28px 0 16px;
}

.event-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 4px;
    white-space: nowrap;
}

.stTextInput input {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stButton button {
    background: #238636 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.5rem !important;
}

.stButton button:hover {
    background: #2ea043 !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Color map for event types ─────────────────────────────────────────────────
EVENT_COLORS = {
    "PushEvent": "#238636",
    "PullRequestEvent": "#9c6af2",
    "IssuesEvent": "#e3b341",
    "ForkEvent": "#58a6ff",
    "WatchEvent": "#fb8f44",
    "CreateEvent": "#39d353",
    "DeleteEvent": "#f85149",
    "IssueCommentEvent": "#e6745b",
}

EVENT_LABELS = {
    "PushEvent": "Push",
    "PullRequestEvent": "PR",
    "IssuesEvent": "Issue",
    "ForkEvent": "Fork",
    "WatchEvent": "Star",
    "CreateEvent": "Create",
    "DeleteEvent": "Delete",
    "IssueCommentEvent": "Comment",
}

import streamlit.components.v1 as components_hero

# ── Hero Header ───────────────────────────────────────────────────────────────
components_hero.html("""
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<div style="padding: 48px 0 36px 0; text-align: center; background: transparent;">
    <div style="font-size: 13px; font-family: JetBrains Mono, monospace; color: #388bfd; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 16px;">
        ● GITHUB PROFILE ANALYZER
    </div>
    <div style="font-size: 52px; font-weight: 700; font-family: JetBrains Mono, monospace; color: #e6edf3; letter-spacing: -2px; line-height: 1.1; margin-bottom: 16px;">
        Decode any<br><span style="color: #388bfd;">GitHub</span> profile.
    </div>
    <div style="font-size: 16px; font-family: Inter, sans-serif; color: #7d8590; font-weight: 300; max-width: 480px; margin: 0 auto; line-height: 1.6;">
        Languages · repos · activity · commit heatmap · dev persona
    </div>
</div>
""", height=220)

# ── Input ─────────────────────────────────────────────────────────────────────
col_left, col_input, col_btn, col_right = st.columns([1, 4, 1.2, 1])

with col_input:
    username = st.text_input("GitHub Username", placeholder="Enter a GitHub username...", label_visibility="collapsed")

token = None

with col_btn:
    analyze = st.button("Analyze →", use_container_width=True)

if not analyze and not username:
    st.markdown("""
    <div style="text-align:center; padding: 40px 0; color: #7d8590;">
        <p style="font-family: monospace; font-size: 0.85rem; letter-spacing:1px;">↑ &nbsp; type a username above to get started</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Fetch data ────────────────────────────────────────────────────────────────
if analyze and username:
    with st.spinner(f"Fetching data for **{username}**..."):
        user, err = fetch_user(username.strip(), token or None)
        if err:
            st.error(f"❌ {err}")
            st.stop()

        repos = fetch_repos(username.strip(), token or None)
        events = fetch_events(username.strip(), token or None)

    repo_data = process_repos(repos)
    event_data = process_events(events)

    # ── Profile header ────────────────────────────────────────────────────────
    st.markdown("---")
    col_av, col_info = st.columns([1, 4])

    with col_av:
        st.image(user.get("avatar_url", ""), width=120)

    with col_info:
        name = user.get("name") or user.get("login", "")
        login = user.get("login", "")
        bio = user.get("bio", "") or ""
        location = user.get("location", "") or ""
        company = user.get("company", "") or ""
        blog = user.get("blog", "") or ""
        age = get_account_age(user.get("created_at", "2020-01-01T00:00:00Z"))

        st.markdown(f"### {name}")
        st.markdown(f"`@{login}` · {age} on GitHub")
        if bio:
            st.markdown(f"*{bio}*")
        meta_parts = []
        if location: meta_parts.append(f"📍 {location}")
        if company: meta_parts.append(f"🏢 {company}")
        if blog: meta_parts.append(f"🌐 [{blog}]({blog})")
        if meta_parts:
            st.markdown("  ·  ".join(meta_parts))

        st.markdown(
            f'<a href="https://github.com/{login}" target="_blank" style="color:#58a6ff; font-size:0.85rem;">View on GitHub →</a>',
            unsafe_allow_html=True
        )

    # ── Stat cards ────────────────────────────────────────────────────────────
    st.markdown('<p style="font-family:monospace;font-size:0.85rem;color:#7d8590;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid #21262d;padding-bottom:8px;margin:28px 0 16px;">Overview</p>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5, s6 = st.columns(6)

    stats = [
        (s1, user.get("public_repos", 0), "Repos"),
        (s2, repo_data["original_count"], "Original"),
        (s3, repo_data["total_stars"], "Stars"),
        (s4, repo_data["total_forks"], "Forks"),
        (s5, user.get("followers", 0), "Followers"),
        (s6, user.get("following", 0), "Following"),
    ]

    for col, val, label in stats:
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px 24px;text-align:center;">
                <span style="font-family:monospace;font-size:2rem;font-weight:600;color:#58a6ff;display:block;">{val:,}</span>
                <div style="font-size:0.78rem;color:#7d8590;text-transform:uppercase;letter-spacing:1px;margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Persona ───────────────────────────────────────────────────────────────
    persona = generate_persona(user, repo_data, event_data)
    st.markdown(f'<div style="background:#1a2332;border:1px solid #388bfd44;border-radius:12px;padding:20px 24px;margin:16px 0;color:#cdd9e5;font-size:0.95rem;line-height:1.7;">💡 <strong>Dev Persona:</strong> {persona}</div>', unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────────────────────
    st.markdown('<p style="font-family:monospace;font-size:0.85rem;color:#7d8590;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid #21262d;padding-bottom:8px;margin:28px 0 16px;">Language Breakdown</p>', unsafe_allow_html=True)
    col_lang, col_event = st.columns(2)

    with col_lang:
        if repo_data["languages"]:
            langs = repo_data["languages"]
            top_langs = dict(list(langs.items())[:8])

            fig = go.Figure(go.Pie(
                labels=list(top_langs.keys()),
                values=list(top_langs.values()),
                hole=0.55,
                textinfo="label+percent",
                textfont=dict(family="JetBrains Mono", size=12, color="#e6edf3"),
                marker=dict(
                    colors=["#58a6ff", "#3fb950", "#d2a8ff", "#ffa657", "#ff7b72",
                            "#79c0ff", "#56d364", "#bc8cff"],
                    line=dict(color="#0d1117", width=2)
                ),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                annotations=[dict(
                    text=f"{len(langs)}<br>langs",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="#7d8590", family="JetBrains Mono")
                )]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No language data available.")

    with col_event:
        if event_data["event_types"]:
            etype = event_data["event_types"]
            labels = [EVENT_LABELS.get(k, k.replace("Event","")) for k in etype.keys()]
            colors = [EVENT_COLORS.get(k, "#7d8590") for k in etype.keys()]

            fig2 = go.Figure(go.Bar(
                x=labels,
                y=list(etype.values()),
                marker=dict(color=colors, line=dict(width=0)),
                text=list(etype.values()),
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=11, color="#7d8590"),
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(family="JetBrains Mono", size=11, color="#7d8590"), gridcolor="#21262d"),
                yaxis=dict(tickfont=dict(family="JetBrains Mono", size=11, color="#7d8590"), gridcolor="#21262d", showgrid=True),
                margin=dict(t=30, b=10, l=10, r=10),
                height=280,
                title=dict(text="Activity by Type (last 90 days)", font=dict(color="#7d8590", size=12, family="Inter"), x=0),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Commit heatmap ────────────────────────────────────────────────────────
    st.markdown('<p style="font-family:monospace;font-size:0.85rem;color:#7d8590;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid #21262d;padding-bottom:8px;margin:28px 0 16px;">Commit Activity (last 90 days)</p>', unsafe_allow_html=True)

    if event_data["commit_days"]:
        today = datetime.utcnow().date()
        start = today - timedelta(days=89)
        date_range = [start + timedelta(days=i) for i in range(90)]

        commit_map = event_data["commit_days"]
        dates = [str(d) for d in date_range]
        values = [commit_map.get(str(d), 0) for d in date_range]
        weeks = [(d - date_range[0]).days // 7 for d in date_range]
        days_of_week = [d.weekday() for d in date_range]

        fig3 = go.Figure(go.Heatmap(
            x=weeks,
            y=days_of_week,
            z=values,
            text=dates,
            hovertemplate="<b>%{text}</b><br>Commits: %{z}<extra></extra>",
            colorscale=[[0, "#161b22"], [0.01, "#0e4429"], [0.3, "#006d32"], [0.7, "#26a641"], [1, "#39d353"]],
            showscale=False,
            xgap=3,
            ygap=3,
        ))

        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(
                tickvals=list(range(7)),
                ticktext=day_labels,
                tickfont=dict(family="JetBrains Mono", size=10, color="#7d8590"),
                autorange="reversed",
            ),
            xaxis=dict(showticklabels=False),
            margin=dict(t=10, b=10, l=40, r=10),
            height=160,
        )
        st.plotly_chart(fig3, use_container_width=True)

    import streamlit.components.v1 as components

    # ── Top repos ─────────────────────────────────────────────────────────────
    st.markdown("### 📁 Top Repositories")

    cols = st.columns(2)
    for i, repo in enumerate(repo_data["top_repos"]):
        with cols[i % 2]:
            desc = repo.get("description") or "No description"
            lang = repo.get("language") or "—"
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            url = repo.get("html_url", "#")
            updated = repo.get("updated_at", "")[:10]
            topics = repo.get("topics", [])

            html = f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px 18px;margin-bottom:4px;font-family:sans-serif;">
                <div style="font-size:15px;font-weight:600;margin-bottom:6px;">
                    <a href="{url}" target="_blank" style="color:#58a6ff;text-decoration:none;">{repo["name"]}</a>
                </div>
                <div style="font-size:13px;color:#7d8590;margin-bottom:10px;line-height:1.5;">{desc[:120]}{"..." if len(desc)>120 else ""}</div>
                <div style="font-size:12px;color:#7d8590;">⭐ {stars} &nbsp; 🍴 {forks} &nbsp; 🔧 {lang} &nbsp; 📅 {updated}</div>
            </div>"""
            components.html(html, height=130, scrolling=False)

    # ── Recent activity ───────────────────────────────────────────────────────
    st.markdown("### 🕒 Recent Activity")

    act_rows = ""
    for act in event_data["recent_activity"][:8]:
        etype = act["type"]
        label = EVENT_LABELS.get(etype, etype.replace("Event",""))
        color = EVENT_COLORS.get(etype, "#7d8590")
        repo_name = act["repo"]
        date = act["created_at"][:10] if act["created_at"] else ""
        act_rows += f"""
        <div style="padding:8px 4px;border-bottom:1px solid #21262d;font-family:sans-serif;">
            <span style="background:{color}22;color:{color};border:1px solid {color}55;border-radius:4px;padding:2px 8px;font-size:11px;font-family:monospace;margin-right:10px;">{label}</span>
            <span style="color:#cdd9e5;font-size:13px;">{repo_name}</span>
            <span style="color:#7d8590;font-size:12px;margin-left:12px;">{date}</span>
        </div>"""

    components.html(
        f'<div style="background:#0d1117;padding:4px 0;">{act_rows}</div>',
        height=len(event_data["recent_activity"][:8]) * 42 + 16,
        scrolling=False
    )

    # ── Topics ────────────────────────────────────────────────────────────────
    if repo_data["topics"]:
        st.markdown("### 🏷️ Topics")
        topic_spans = " ".join([
            f'<span style="display:inline-block;background:#1f2d3d;color:#58a6ff;border:1px solid #388bfd55;border-radius:20px;padding:3px 12px;font-size:12px;margin:3px;font-family:monospace;">{t}</span>'
            for t in repo_data["topics"][:30]
        ])
        components.html(
            f'<div style="background:#0d1117;padding:8px 0;line-height:2.5;">{topic_spans}</div>',
            height=120,
            scrolling=False
        )

    # ── PDF Download ─────────────────────────────────────────────────────────
    st.markdown("---")
    col_dl1, col_dl2, col_dl3 = st.columns([2, 1.5, 2])
    with col_dl2:
        from pdf_report import build_pdf
        pdf_buf = build_pdf(user, repo_data, event_data, persona)
        st.download_button(
            label="⬇️  Download PDF Report",
            data=pdf_buf,
            file_name=f"{login}_github_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    st.markdown(
        '<p style="text-align:center; color:#7d8590; font-size:0.75rem; font-family:\'JetBrains Mono\',monospace;">Built with GitHub API · Streamlit · Plotly · ReportLab</p>',
        unsafe_allow_html=True
    )
