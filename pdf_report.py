import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import Flowable

W, H = A4

BG       = colors.HexColor("#0d1117")
SURFACE  = colors.HexColor("#161b22")
BORDER   = colors.HexColor("#30363d")
BLUE     = colors.HexColor("#58a6ff")
MUTED    = colors.HexColor("#7d8590")
TEXT     = colors.HexColor("#e6edf3")
TEXT_SEC = colors.HexColor("#cdd9e5")
ACCENT   = colors.HexColor("#1a2332")
BLUE_BDR = colors.HexColor("#388bfd")

LANG_COLORS = ["#58a6ff","#3fb950","#d2a8ff","#ffa657","#ff7b72","#79c0ff","#56d364","#bc8cff"]

def sty(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9, textColor=TEXT, leading=13, spaceAfter=3)
    base.update(kw)
    return ParagraphStyle(name, **base)

S_NAME    = sty("name",    fontName="Helvetica-Bold", fontSize=24, textColor=TEXT,  leading=28, spaceAfter=2)
S_LOGIN   = sty("login",   fontSize=10, textColor=BLUE, spaceAfter=4)
S_BIO     = sty("bio",     fontSize=9,  textColor=MUTED, spaceAfter=4)
S_META    = sty("meta",    fontSize=7.5,textColor=MUTED, spaceAfter=0)
S_SECTION = sty("section", fontName="Helvetica-Bold", fontSize=7.5, textColor=MUTED, leading=10, spaceAfter=6, spaceBefore=14)
S_BODY    = sty("body",    fontSize=8.5,textColor=TEXT_SEC, leading=13)
S_MONO    = sty("mono",    fontSize=7.5,textColor=MUTED, leading=11)
S_BLUE    = sty("blue",    fontSize=8,  textColor=BLUE, fontName="Helvetica-Bold")
S_TOPIC   = sty("topic",   fontSize=8,  textColor=BLUE, leading=14)


class StatCard(Flowable):
    def __init__(self, label, value, w=36*mm, h=22*mm):
        self.label, self.value, self.w, self.h = label, str(value), w, h
    def wrap(self, *args): return self.w, self.h
    def draw(self):
        c = self.canv
        c.setFillColor(SURFACE); c.roundRect(0,0,self.w,self.h,5,fill=1,stroke=0)
        c.setStrokeColor(BORDER); c.setLineWidth(0.5); c.roundRect(0,0,self.w,self.h,5,fill=0,stroke=1)
        c.setFillColor(BLUE); c.setFont("Helvetica-Bold",15)
        c.drawCentredString(self.w/2, self.h-11*mm+1, self.value)
        c.setFillColor(MUTED); c.setFont("Helvetica",6)
        c.drawCentredString(self.w/2, 3.5*mm, self.label.upper())


class LangBar(Flowable):
    def __init__(self, languages, w, h=7*mm):
        self.languages, self.w, self.h = languages, w, h
    def wrap(self, *args): return self.w, self.h + 14
    def draw(self):
        c = self.canv
        items = list(self.languages.items())[:8]
        total = sum(v for _,v in items) or 1
        x = 0
        for i, (lang, count) in enumerate(items):
            sw = self.w * count / total
            col = colors.HexColor(LANG_COLORS[i % len(LANG_COLORS)])
            c.setFillColor(col); c.rect(x, self.h+2, sw, self.h, fill=1, stroke=0)
            x += sw
        x = 0
        for i, (lang, count) in enumerate(items):
            pct = round(count/total*100)
            col = colors.HexColor(LANG_COLORS[i % len(LANG_COLORS)])
            c.setFillColor(col); c.circle(x+3, 3, 2, fill=1, stroke=0)
            c.setFillColor(TEXT_SEC); c.setFont("Helvetica",6)
            label = f"{lang} {pct}%"
            c.drawString(x+7, 1, label)
            x += len(label)*4 + 14
            if x > self.w - 10: break


class RepoCard(Flowable):
    def __init__(self, repo, w=80*mm, h=27*mm):
        self.repo, self.w, self.h = repo, w, h
    def wrap(self, *args): return self.w, self.h
    def draw(self):
        c = self.canv; r = self.repo
        name  = r.get("name","")[:30]
        desc  = (r.get("description") or "No description")[:58]
        lang  = r.get("language") or "—"
        stars = r.get("stargazers_count",0)
        forks = r.get("forks_count",0)
        c.setFillColor(SURFACE); c.roundRect(0,0,self.w,self.h,5,fill=1,stroke=0)
        c.setStrokeColor(BORDER); c.setLineWidth(0.5); c.roundRect(0,0,self.w,self.h,5,fill=0,stroke=1)
        c.setFillColor(BLUE); c.setFont("Helvetica-Bold",8); c.drawString(3.5*mm,self.h-7*mm,name)
        c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(3.5*mm,self.h-12*mm,desc)
        c.setFillColor(TEXT_SEC); c.setFont("Helvetica",6.5); c.drawString(3.5*mm,4*mm,f"* {stars}   f {forks}   {lang}")


def build_pdf(user, repo_data, event_data, persona):
    buf = io.BytesIO()
    login = user.get("login","")
    name  = user.get("name") or login

    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm, topMargin=12*mm, bottomMargin=14*mm)

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BG); canvas.rect(0,0,W,H,fill=1,stroke=0)
        canvas.setFillColor(BLUE); canvas.rect(0, H-2, W, 2, fill=1, stroke=0)
        canvas.setFillColor(MUTED); canvas.setFont("Helvetica",6.5)
        canvas.drawString(18*mm, 8*mm, f"Generated {datetime.utcnow().strftime('%Y-%m-%d')}  ·  GitHub Profile Analyzer")
        canvas.drawRightString(W-18*mm, 8*mm, f"github.com/{login}")
        canvas.restoreState()

    story = []
    bio      = user.get("bio") or ""
    loc      = user.get("location") or ""
    company  = user.get("company") or ""
    followers= user.get("followers",0)
    following= user.get("following",0)

    story.append(Spacer(1,4*mm))
    story.append(Paragraph(name, S_NAME))
    story.append(Paragraph(f"@{login}", S_LOGIN))
    if bio: story.append(Paragraph(bio, S_BIO))
    meta_parts = [p for p in [loc, company, f"{followers} followers · {following} following"] if p]
    if meta_parts: story.append(Paragraph("  ·  ".join(meta_parts), S_META))
    story.append(Spacer(1,5*mm))

    # Stat cards
    story.append(Paragraph("OVERVIEW", S_SECTION))
    stats = [("Repos",user.get("public_repos",0)),("Original",repo_data["original_count"]),
             ("Stars",repo_data["total_stars"]),("Forks",repo_data["total_forks"]),("Followers",followers)]
    cw = (doc.width) / len(stats)
    cards = Table([[StatCard(l,v,w=cw-3*mm) for l,v in stats]], colWidths=[cw]*len(stats), rowHeights=[23*mm])
    cards.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),3*mm)]))
    story.append(cards)
    story.append(Spacer(1,5*mm))

    # Persona
    story.append(Paragraph("DEV PERSONA", S_SECTION))
    pb = Table([[Paragraph(f"💡  {persona}", S_BODY)]], colWidths=[doc.width])
    pb.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),ACCENT),
        ("BOX",(0,0),(-1,-1),0.5,BLUE_BDR),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(pb)
    story.append(Spacer(1,5*mm))

    # Languages
    if repo_data["languages"]:
        story.append(Paragraph("LANGUAGES", S_SECTION))
        story.append(LangBar(repo_data["languages"], w=doc.width))
        story.append(Spacer(1,10*mm))

    # Top repos
    top = repo_data["top_repos"]
    if top:
        story.append(Paragraph("TOP REPOSITORIES", S_SECTION))
        rw = (doc.width - 4*mm) / 2
        for i in range(0, min(len(top),6), 2):
            pair = top[i:i+2]
            items = [RepoCard(r, w=rw) for r in pair]
            while len(items) < 2: items.append(Spacer(rw, 27*mm))
            t = Table([items], colWidths=[rw+4*mm, rw])
            t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
                                   ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),2.5*mm)]))
            story.append(t)
        story.append(Spacer(1,3*mm))

    # Activity
    EVENT_LABELS = {"PushEvent":"Push","PullRequestEvent":"Pull Request","IssuesEvent":"Issues",
                    "ForkEvent":"Fork","WatchEvent":"Star","CreateEvent":"Create",
                    "DeleteEvent":"Delete","IssueCommentEvent":"Comment"}
    if event_data["event_types"]:
        story.append(Paragraph("ACTIVITY (last 90 days)", S_SECTION))
        rows = []
        for etype, count in sorted(event_data["event_types"].items(), key=lambda x: -x[1])[:8]:
            label = EVENT_LABELS.get(etype, etype.replace("Event",""))
            rows.append([Paragraph(label, S_BODY), Paragraph(str(count), S_BLUE)])
        at = Table(rows, colWidths=[doc.width*0.75, doc.width*0.25])
        at.setStyle(TableStyle([
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[SURFACE, colors.HexColor("#1c2128")]),
            ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LINEBELOW",(0,0),(-1,-2),0.3,BORDER),
        ]))
        story.append(at)
        story.append(Spacer(1,4*mm))

    # Topics
    if repo_data["topics"]:
        story.append(Paragraph("TOPICS", S_SECTION))
        story.append(Paragraph("   ·   ".join(repo_data["topics"][:20]), S_TOPIC))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.read()
