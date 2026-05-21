import urllib.request
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_DIR = Path("/tmp/fonts")
FONT_DIR.mkdir(exist_ok=True)

fonts = {
    "DMSans":       "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf",
    "DMSans-Bold":  "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf",
}

BODY   = "Helvetica"
BOLD   = "Helvetica-Bold"
MONO   = "Courier"

try:
    path = FONT_DIR / "DMSans.ttf"
    if not path.exists():
        urllib.request.urlretrieve(fonts["DMSans"], path)
    pdfmetrics.registerFont(TTFont("DMSans", str(path)))
    pdfmetrics.registerFont(TTFont("DMSans-Bold", str(path)))
    BODY = "DMSans"
    BOLD = "DMSans-Bold"
    print("DM Sans loaded")
except Exception as e:
    print(f"Font download failed, using Helvetica: {e}")

# ── Colors ───────────────────────────────────────────────────────────────────
TEAL        = HexColor("#01696F")
TEAL_DARK   = HexColor("#0C4E54")
TEAL_LIGHT  = HexColor("#E8F4F5")
TEAL_MID    = HexColor("#B8DEE0")
GRAY_BG     = HexColor("#F7F6F2")
GRAY_BORDER = HexColor("#D4D1CA")
GRAY_TEXT   = HexColor("#28251D")
GRAY_MUTED  = HexColor("#7A7974")
WARN_BG     = HexColor("#FFF8F0")
WARN_BORDER = HexColor("#BB653B")
WARN_TEXT   = HexColor("#964219")
CODE_BG     = HexColor("#F0F0EE")
WHITE       = white

W, H = letter
MARGIN = 0.85 * inch

# ── Styles ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, parent="Normal", font=None, color=None, **kw):
    fn = font or BODY
    tc = color or GRAY_TEXT
    return ParagraphStyle(name, parent=styles[parent], fontName=fn, textColor=tc, **kw)

sNormal     = S("sNormal",       fontSize=9.5,  leading=14,  spaceAfter=6)
sSmall      = S("sSmall",        fontSize=8.5,  leading=12,  spaceAfter=4, color=GRAY_MUTED)
sH1         = S("sH1",           fontSize=22,   leading=26,  spaceAfter=4,  font=BOLD, color=WHITE)
sH2         = S("sH2",           fontSize=13,   leading=17,  spaceBefore=14, spaceAfter=5, font=BOLD, color=TEAL_DARK)
sH3         = S("sH3",           fontSize=10.5, leading=14,  spaceBefore=8,  spaceAfter=3, font=BOLD)
sBullet     = S("sBullet",       fontSize=9.5,  leading=14,  spaceAfter=3,  leftIndent=14, firstLineIndent=-10)
sCode       = S("sCode",         fontSize=8.5,  leading=13,  spaceAfter=2,  font=MONO,
                backColor=CODE_BG, leftIndent=8, rightIndent=8, borderPadding=4)
sCaption    = S("sCaption",      fontSize=8,    leading=11,  spaceAfter=4,  color=GRAY_MUTED, alignment=1)
sCallout    = S("sCallout",      fontSize=9,    leading=13,  spaceAfter=2,  leftIndent=10)
sTH         = S("sTH",           fontSize=9,    leading=12,  font=BOLD, color=WHITE)
sTD         = S("sTD",           fontSize=9,    leading=13)
sTDm        = S("sTDm",          fontSize=8.5,  leading=12,  color=GRAY_MUTED)
sRef        = S("sRef",          fontSize=8.5,  leading=13,  spaceAfter=3,  color=GRAY_TEXT)

def bullet(text):
    return Paragraph(f"• &nbsp; {text}", sBullet)

def h2(text):
    return Paragraph(text, sH2)

def h3(text):
    return Paragraph(text, sH3)

def p(text):
    return Paragraph(text, sNormal)

def sp(n=6):
    return Spacer(1, n)

def rule():
    return HRFlowable(width="100%", thickness=0.5, color=GRAY_BORDER, spaceAfter=6, spaceBefore=2)

def callout(text, color=TEAL_LIGHT, border=TEAL_MID):
    style = ParagraphStyle("co", parent=sCallout, backColor=color,
                           borderColor=border, borderWidth=1, borderPadding=6,
                           borderRadius=3, spaceAfter=8)
    return Paragraph(text, style)

def warn(text):
    return callout(text, color=WARN_BG, border=WARN_BORDER)

def tbl(data, col_widths, header_rows=1):
    t = Table(data, colWidths=col_widths)
    ts = [
        ("BACKGROUND",  (0,0), (-1, header_rows-1), TEAL),
        ("TEXTCOLOR",   (0,0), (-1, header_rows-1), WHITE),
        ("FONTNAME",    (0,0), (-1, header_rows-1), BOLD),
        ("FONTSIZE",    (0,0), (-1,-1),              8.5),
        ("LEADING",     (0,0), (-1,-1),              12),
        ("ALIGN",       (0,0), (-1,-1),              "LEFT"),
        ("VALIGN",      (0,0), (-1,-1),              "TOP"),
        ("TOPPADDING",  (0,0), (-1,-1),              5),
        ("BOTTOMPADDING",(0,0),(-1,-1),              5),
        ("LEFTPADDING", (0,0), (-1,-1),              7),
        ("RIGHTPADDING",(0,0), (-1,-1),              7),
        ("GRID",        (0,0), (-1,-1),              0.4, GRAY_BORDER),
        ("ROWBACKGROUNDS",(0,header_rows),(-1,-1),   [WHITE, GRAY_BG]),
    ]
    t.setStyle(TableStyle(ts))
    return t

# ── Header / Footer ──────────────────────────────────────────────────────────
def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, H - 30, W, 30, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont(BOLD, 8)
    canvas.drawString(MARGIN, H - 19, "ECE Sizing Calculator — User Guide")
    canvas.setFont(BODY, 8)
    canvas.drawRightString(W - MARGIN, H - 19, "Expedient | Confidential")
    canvas.setFillColor(GRAY_MUTED)
    canvas.setFont(BODY, 7.5)
    canvas.drawString(MARGIN, 24, "ece-sizer.pplx.app")
    canvas.drawRightString(W - MARGIN, 24, f"Page {doc.page}")
    canvas.setStrokeColor(GRAY_BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, 34, W - MARGIN, 34)
    canvas.restoreState()

def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, H - 220, W, 220, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont(BOLD, 28)
    canvas.drawString(MARGIN, H - 90, "ECE Sizing Calculator")
    canvas.setFont(BODY, 14)
    canvas.drawString(MARGIN, H - 118, "Elastic Cloud Enterprise Deployment Planner")
    canvas.setFont(BODY, 10)
    canvas.setFillColor(HexColor("#B8DEE0"))
    canvas.drawString(MARGIN, H - 142, "User Guide & Calculation Reference")
    canvas.drawString(MARGIN, H - 160, "v1.0.11  ·  Expedient Technology Solutions")
    canvas.setFillColor(GRAY_MUTED)
    canvas.setFont(BODY, 7.5)
    canvas.drawString(MARGIN, 24, "ece-sizer.pplx.app")
    canvas.drawRightString(W - MARGIN, 24, f"Page {doc.page}")
    canvas.setStrokeColor(GRAY_BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, 34, W - MARGIN, 34)
    canvas.restoreState()

# ── Document ─────────────────────────────────────────────────────────────────
OUT = "/home/user/workspace/ECE_Sizing_Calculator_User_Guide.pdf"
doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    title="ECE Sizing Calculator — User Guide",
    author="Perplexity Computer",
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=0.65*inch, bottomMargin=0.65*inch,
)

story = []

# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 3.2*inch))
story.append(Paragraph(
    "This guide explains how to use the ECE Sizing Calculator to plan Elastic Cloud Enterprise "
    "deployments, interpret results, and understand the formulas behind every number.",
    ParagraphStyle("coverdesc", parent=sNormal, fontSize=11, leading=16,
                   textColor=GRAY_MUTED, alignment=1)
))
story.append(Spacer(1, 0.3*inch))

toc_data = [
    [Paragraph("Section", sTH), Paragraph("Topic", sTH)],
    [Paragraph("1", sTD), Paragraph("Overview & Quick Start", sTD)],
    [Paragraph("2", sTD), Paragraph("Input Fields Reference", sTD)],
    [Paragraph("3", sTD), Paragraph("Advanced Ratios & Tuning", sTD)],
    [Paragraph("4", sTD), Paragraph("Results & KPIs", sTD)],
    [Paragraph("5", sTD), Paragraph("Shard Model", sTD)],
    [Paragraph("6", sTD), Paragraph("How the Calculations Work", sTD)],
    [Paragraph("7", sTD), Paragraph("Compare Deployment", sTD)],
    [Paragraph("8", sTD), Paragraph("Saving, Exporting & Printing", sTD)],
    [Paragraph("9", sTD), Paragraph("Tips & Common Mistakes", sTD)],
    [Paragraph("10", sTD), Paragraph("References & Further Reading", sTD)],
]
story.append(tbl(toc_data, [0.5*inch, 5.3*inch]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("1. Overview & Quick Start"),
    rule(),
    p("The ECE Sizing Calculator helps you plan the right hardware and Elasticsearch cluster "
      "configuration for an Elastic Cloud Enterprise deployment. It takes your data "
      "characteristics as inputs — ingest rate, retention, use case — and outputs RAM, storage, "
      "node counts, and shard health guidance sized to Elastic's published best practices."),
    sp(6),
    callout("Live URL: <a href='https://ece-sizer.pplx.app' color='#01696F'>ece-sizer.pplx.app</a> &nbsp;·&nbsp; "
            "No login required &nbsp;·&nbsp; Works in any modern browser"),
    sp(4),
    h3("Quick Start (5 steps)"),
    bullet("Select a <b>Use Case Preset</b> (SIEM, APM, Security Analytics, Enterprise Search, or Custom)."),
    bullet("Choose an <b>Architecture Preset</b> (Elastic Standard 3-tier, Expedient Optimized, or Minimal)."),
    bullet("Enter your <b>Daily Ingest (GB/day)</b> and <b>Availability Zones</b>."),
    bullet("Set <b>retention days</b> for each active tier (Hot / Warm / Cold / Frozen)."),
    bullet("Review the <b>Results</b> section — RAM, Storage, Object Store, and Shard Health."),
    sp(6),
    callout("<b>Tip:</b> Start with a preset and adjust only what you know. The defaults are based on "
            "Elastic's official sizing guidelines and are safe starting points."),
    sp(8),
    h3("Use Case Presets"),
]

preset_data = [
    [Paragraph("Preset", sTH), Paragraph("Best For", sTH), Paragraph("Key Defaults Set", sTH)],
    [Paragraph("SIEM", sTD),
     Paragraph("Security information & event management, log ingestion", sTD),
     Paragraph("Hot 7d, Warm 23d, Cold 60d; Hot ratio 1:30", sTD)],
    [Paragraph("APM", sTD),
     Paragraph("Application performance monitoring, traces, metrics", sTD),
     Paragraph("Hot 3d, Warm 14d; higher replica count", sTD)],
    [Paragraph("Security Analytics", sTD),
     Paragraph("Threat hunting, detection engineering, Elastic Security", sTD),
     Paragraph("Hot 14d, Warm 30d, Frozen 365d; frozen tier enabled", sTD)],
    [Paragraph("Enterprise Search", sTD),
     Paragraph("App search, website search, document retrieval", sTD),
     Paragraph("Non-rolling index type; cold/frozen disabled", sTD)],
    [Paragraph("Custom", sTD),
     Paragraph("Any workload not covered above", sTD),
     Paragraph("All fields left at last-used values for manual tuning", sTD)],
]
story.append(tbl(preset_data, [1.1*inch, 2.1*inch, 2.65*inch]))
story.append(sp(8))

story += [
    h3("Architecture Presets"),
]
arch_data = [
    [Paragraph("Preset", sTH), Paragraph("Description", sTH), Paragraph("When to Use", sTH)],
    [Paragraph("Elastic Standard", sTD),
     Paragraph("3 AZs, 1 replica, dedicated masters enabled", sTD),
     Paragraph("Production — full HA, Elastic recommended baseline", sTD)],
    [Paragraph("Expedient Optimized", sTD),
     Paragraph("3 AZs, 1 replica, cold ratio 1:200, masters auto-scaled", sTD),
     Paragraph("Expedient-hosted ECE — tuned for the Expedient allocator environment", sTD)],
    [Paragraph("Minimal", sTD),
     Paragraph("1 AZ, 0 replicas, no dedicated masters", sTD),
     Paragraph("Dev/test only — no fault tolerance", sTD)],
]
story.append(tbl(arch_data, [1.3*inch, 2.1*inch, 2.45*inch]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INPUT FIELDS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("2. Input Fields Reference"),
    rule(),
    p("All primary inputs are in the top card. Fields update results in real time as you type."),
    sp(6),
]

input_data = [
    [Paragraph("Field", sTH), Paragraph("What to Enter", sTH), Paragraph("Notes", sTH)],
    [Paragraph("Client / Project Name", sTD),
     Paragraph("Free text label", sTD),
     Paragraph("Included in Export JSON filename", sTD)],
    [Paragraph("Daily Ingest (GB/day)", sTD),
     Paragraph("Uncompressed source data volume per day", sTD),
     Paragraph("Enter raw pre-compression size. The Compression Ratio field (Advanced) converts this to on-disk GB before storage calculations.", sTD)],
    [Paragraph("Availability Zones", sTD),
     Paragraph("1, 2, or 3", sTD),
     Paragraph("3 AZs required for production HA. Replicas are distributed across zones.", sTD)],
    [Paragraph("Hot Retention (days)", sTD),
     Paragraph("Days data stays on hot (SSD) nodes", sTD),
     Paragraph("Typical: 3–14 days for logs; 30+ days for search data.", sTD)],
    [Paragraph("Hot Replicas", sTD),
     Paragraph("Number of replica shards per primary", sTD),
     Paragraph("1 replica = full copy of data (doubles storage). Minimum 1 for HA.", sTD)],
    [Paragraph("Warm Retention (days)", sTD),
     Paragraph("Additional days on warm (HDD) tier after hot", sTD),
     Paragraph("Enable warm toggle first. 0 = warm tier not used.", sTD)],
    [Paragraph("Cold / Frozen Retention", sTD),
     Paragraph("Days in cold (searchable snapshot) or frozen (partial mount) tiers", sTD),
     Paragraph("Frozen tier uses object storage — very low cost per GB.", sTD)],
    [Paragraph("Dedicated Masters", sTD),
     Paragraph("Auto (recommended) or manual count + RAM", sTD),
     Paragraph("Auto picks 4/8/16 GB based on node count and shard count.", sTD)],
    [Paragraph("Coordinator Nodes", sTD),
     Paragraph("Optional — count and RAM", sTD),
     Paragraph("Recommended for deployments with >10 hot nodes or heavy Kibana usage.", sTD)],
]
story.append(tbl(input_data, [1.5*inch, 1.9*inch, 2.45*inch]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — ADVANCED
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("3. Advanced Ratios & Tuning"),
    rule(),
    p("The Advanced section is organized into five groups. Most users can leave these at "
      "defaults — they represent Elastic's published planning guidelines. Adjust only when "
      "you have specific hardware specs or measured workload data."),
    sp(4),
    callout("<b>Note on heuristics:</b> Overhead multipliers and the CPU ingest rule are planning "
            "heuristics used in Elastic sizing workshops — not officially published constants. "
            "Actual values vary by workload. Treat them as conservative starting points."),
    sp(6),
]

adv_data = [
    [Paragraph("Group / Field", sTH), Paragraph("Default", sTH), Paragraph("What It Controls", sTH)],
    # RAM:Storage
    [Paragraph("RAM : Storage Ratios", ParagraphStyle("grp",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Hot (1:X)", sTD), Paragraph("1:30", sTD),
     Paragraph("GB of RAM per GB of indexed data on hot nodes. Higher = more storage-dense but slower.", sTD)],
    [Paragraph("  Warm (1:X)", sTD), Paragraph("1:160", sTD),
     Paragraph("Warm nodes are force-merged and read-only — much higher ratio is safe.", sTD)],
    [Paragraph("  Cold (1:X)", sTD), Paragraph("1:160 (1:200 Expedient)", sTD),
     Paragraph("Cold uses the same hardware profile as warm. Storage savings come from searchable snapshots eliminating replica copies — not from a lower RAM ratio. The Expedient Optimized preset uses 1:200 to reflect the specific storage-to-RAM characteristics of the Expedient ECE environment.", sTD)],
    [Paragraph("  Frozen (1:X)", sTD), Paragraph("1:1500", sTD),
     Paragraph("Frozen nodes hold only metadata and a small local cache. Dataset lives in object store. Elastic published ratio: 1:1500.", sTD)],
    # Overhead
    [Paragraph("Overhead & Watermark", ParagraphStyle("grp2",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Hot Overhead Multiplier", sTD), Paragraph("1.5×", sTD),
     Paragraph("Lucene segment overhead heuristic for hot tier. Conservative planning default. Actual overhead varies with field mappings and merge state (typically 1.4–1.7×).", sTD)],
    [Paragraph("  Warm Overhead Multiplier", sTD), Paragraph("1.25×", sTD),
     Paragraph("Lower than hot because warm data is force-merged (fewer segments). Typical range: 1.15–1.30×.", sTD)],
    [Paragraph("  Cold/Frozen Overhead", sTD), Paragraph("1.1×", sTD),
     Paragraph("Snapshot data is fully merged — minimal overhead.", sTD)],
    [Paragraph("  Disk Watermark Headroom", sTD), Paragraph("15%", sTD),
     Paragraph("Elasticsearch blocks writes at 85% disk usage by default. This buffer ensures you never hit it.", sTD)],
    # Shard
    [Paragraph("Shard & Index Sizing", ParagraphStyle("grp3",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Target Shard Size (GB)", sTD), Paragraph("30 GB", sTD),
     Paragraph("Elastic recommends 10–50 GB. Used to compute primary shard count.", sTD)],
    [Paragraph("  System Indices Shards", sTD), Paragraph("250", sTD),
     Paragraph("Baseline for .kibana, .security, and other built-in indices.", sTD)],
    [Paragraph("  Indices/Day", sTD), Paragraph("1", sTD),
     Paragraph("Distinct data streams writing per day. Increase for multi-source deployments.", sTD)],
    # ILM
    [Paragraph("ILM Rollover", ParagraphStyle("grp4",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Rollover Condition", sTD), Paragraph("Age-based", sTD),
     Paragraph("Age-based: one index per day. Size-based: ILM rolls when index hits max size.", sTD)],
    [Paragraph("  Max Index Size (GB)", sTD), Paragraph("50 GB", sTD),
     Paragraph("(Size-based only) Elastic ILM max_primary_shard_size threshold.", sTD)],
    # Snapshots
    [Paragraph("Snapshots", ParagraphStyle("grp5",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Snapshot Retention (days)", sTD), Paragraph("7", sTD),
     Paragraph("Days of nightly snapshot backups kept in object store. Calculator shows conservative upper bound — actual storage is typically 30–60% lower due to incremental deduplication.", sTD)],
    [Paragraph("  Index Type", sTD), Paragraph("Rolling", sTD),
     Paragraph("Rolling (logs/metrics): daily delta only. Non-rolling (search): adds full initial snapshot.", sTD)],
    # Compression
    [Paragraph("Compression", ParagraphStyle("grpC",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Compression Ratio", sTD), Paragraph("2.0×", sTD),
     Paragraph("How much Elasticsearch compresses your data on disk. Elastic typically achieves 2–4× for log/event data. "
               "All storage and shard size calculations use ingest ÷ compression ratio as the effective on-disk daily volume. "
               "Set to 1.0× to treat ingest as already-compressed or to plan conservatively.", sTD)],
    # Infrastructure
    [Paragraph("Infrastructure", ParagraphStyle("grp6",parent=sNormal,fontName=BOLD,fontSize=8.5,textColor=TEAL_DARK)), Paragraph("", sTD), Paragraph("", sTD)],
    [Paragraph("  Hot vCPU / Node", sTD), Paragraph("8", sTD),
     Paragraph("vCPUs assigned to each hot node. Used for CPU ingest capacity check (planning heuristic).", sTD)],
    [Paragraph("  ECE Allocator Count", sTD), Paragraph("14", sTD),
     Paragraph("Number of allocator hosts. Each uses 12 GB for ECE control plane (per Elastic documentation).", sTD)],
    [Paragraph("  Allocator RAM / Host (GB)", sTD), Paragraph("1412", sTD),
     Paragraph("Physical RAM per allocator. ECE control plane overhead (12 GB) is subtracted from usable tenant RAM.", sTD)],
    [Paragraph("  Nodes/Zone (per tier)", sTD), Paragraph("1", sTD),
     Paragraph("Nodes per AZ for hot/warm/cold/frozen. Affects total shard capacity ceiling.", sTD)],
    [Paragraph("  Frozen Cache/Node (GB)", sTD), Paragraph("1000 GB", sTD),
     Paragraph("Local SSD cache for frozen tier. Elastic guidance: 1–10% of remote dataset; 5% is the recommended starting point.", sTD)],
]

adv_tbl = Table(adv_data, colWidths=[1.65*inch, 0.75*inch, 3.45*inch])
grp_rows = [1, 6, 11, 15, 18, 21, 23]  # 0-indexed rows that are group headers
adv_ts = [
    ("BACKGROUND",  (0,0), (-1, 0), TEAL),
    ("TEXTCOLOR",   (0,0), (-1, 0), WHITE),
    ("FONTNAME",    (0,0), (-1, 0), BOLD),
    ("FONTSIZE",    (0,0), (-1,-1), 8.5),
    ("LEADING",     (0,0), (-1,-1), 12),
    ("ALIGN",       (0,0), (-1,-1), "LEFT"),
    ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ("TOPPADDING",  (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 7),
    ("RIGHTPADDING",(0,0), (-1,-1), 7),
    ("GRID",        (0,0), (-1,-1), 0.4, GRAY_BORDER),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, GRAY_BG]),
]
for r in grp_rows:
    adv_ts.append(("BACKGROUND", (0,r), (-1,r), TEAL_LIGHT))
    adv_ts.append(("SPAN",       (0,r), (-1,r)))
adv_tbl.setStyle(TableStyle(adv_ts))
story.append(adv_tbl)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — RESULTS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("4. Results & KPIs"),
    rule(),
    p("The Results section updates instantly as you change inputs. It shows five key output areas:"),
    sp(4),
]

kpi_data = [
    [Paragraph("KPI", sTH), Paragraph("What It Shows", sTH), Paragraph("How to Interpret", sTH)],
    [Paragraph("Total RAM", sTD),
     Paragraph("Sum of all Elasticsearch node RAM across all tiers + masters + coordinators", sTD),
     Paragraph("Sub-line shows tenant RAM utilization % of total allocator capacity (12 GB ECE overhead per allocator deducted).", sTD)],
    [Paragraph("Total Storage", sTD),
     Paragraph("Hot + Warm + Cold on-node storage including replicas, overhead, and watermark buffer", sTD),
     Paragraph("This is the raw disk capacity needed on allocator hosts — not object store.", sTD)],
    [Paragraph("Object Store", sTD),
     Paragraph("Frozen tier data + snapshot retention in S3/Blob/GCS", sTD),
     Paragraph("Low-cost storage tier. Frozen data is fetched on demand — not stored locally. Snapshot estimate is a conservative upper bound.", sTD)],
    [Paragraph("Frozen Cache Health", sTD),
     Paragraph("Cache % of frozen data — ok (≥10%), warn (5–10%), bad (<5%)", sTD),
     Paragraph("Below 5% risks cache thrashing. Elastic guidance: 5% minimum starting point. Increase toward 10% for high cache-hit workloads.", sTD)],
    [Paragraph("CPU Hint", sTD),
     Paragraph("Ingest GB/hr vs. vCPU capacity check using 4 vCPU/GB-hr planning heuristic", sTD),
     Paragraph("Yellow/red means hot nodes may be CPU-bound at peak ingest. Not official Elastic guidance — actual CPU needs vary by workload complexity.", sTD)],
]
story.append(tbl(kpi_data, [1.2*inch, 2.1*inch, 2.55*inch]))
story.append(sp(8))

storage_bkd_data = [
    [Paragraph("Column", sTH), Paragraph("What It Shows", sTH)],
    [Paragraph("Tier", sTD), Paragraph("Hot, Warm, Cold, Frozen, or Total (on-node)", sTD)],
    [Paragraph("Primary Data", sTD),
     Paragraph("Primary-only on-disk volume: ingestOnDisk × overhead multiplier × retention days. "
               "Does not include replicas.", sTD)],
    [Paragraph("Replica Overhead", sTD),
     Paragraph("Storage added by replica copies: primary data × replica count. "
               "Cold and frozen tiers show 'Snapshots — no local replicas' because they use searchable snapshots.", sTD)],
    [Paragraph("Total On-Node", sTD),
     Paragraph("(Primary + replicas) × watermark multiplier — the actual disk capacity required on allocator hosts.", sTD)],
    [Paragraph("Replicas", sTD),
     Paragraph("Replica count for the tier (1× = one full copy, 0 = no redundancy).", sTD)],
    [Paragraph("Compression", sTD),
     Paragraph("The effective compression ratio applied to this tier. Matches the Advanced → Compression Ratio input.", sTD)],
]

story += [
    h3("Node Breakdown Table"),
    p("Below the KPIs, a table shows each component — Hot, Warm, Cold, Frozen, Master, Coordinator — "
      "with its RAM per node, node count (per zone × AZs), total RAM, and storage contribution."),
    sp(4),
    callout("<b>ECE Instance Size Snapping:</b> The calculator automatically snaps each node's RAM "
            "to the nearest valid ECE instance size (data.default profile): 1, 2, 4, 8, 16, 32, or 64 GB. "
            "This ensures the output reflects what ECE can actually allocate."),
    sp(8),
    h3("Storage Breakdown Table"),
    p("Below the node breakdown, the Storage Breakdown table gives a replica-aware, per-tier view of "
      "how on-disk storage is distributed. It separates primary data from replica overhead so you can "
      "see exactly what each tier's replica configuration costs in storage."),
    sp(4),
]
story.append(tbl(storage_bkd_data, [1.2*inch, 4.65*inch]))
story.append(sp(4))
story.append(callout(
    "<b>Reading the totals row:</b> The Total (on-node) row sums only local-disk tiers (Hot + Warm + Cold). "
    "Frozen data lives in object store — it appears in the Object Store KPI, not here. "
    "The note below the table shows raw ingest vs. compressed volume at your chosen ratio."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SHARD MODEL
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("5. Shard Model"),
    rule(),
    p("The Shard Model section provides a health check on your shard configuration against "
      "Elastic's best practices. It is the most actionable section for detecting "
      "under- or over-sharded deployments before they cause problems in production."),
    sp(4),
    h3("Shard Health Banner"),
    p("A color-coded banner summarizes overall shard health:"),
    bullet("<b>Green (OK):</b> All shard density and count checks pass."),
    bullet("<b>Yellow (Warning):</b> One or more thresholds approaching limit — review recommendations."),
    bullet("<b>Red (Critical):</b> Cluster shard limit or density ceiling exceeded — action required."),
    sp(6),
    h3("Shard Table"),
    p("The table shows per-tier shard counts broken down into:"),
]

shard_data = [
    [Paragraph("Column", sTH), Paragraph("Meaning", sTH)],
    [Paragraph("Primary Shards", sTD), Paragraph("Derived from: ceil(daily ingest on-disk ÷ target shard size) × indices/day × retention days", sTD)],
    [Paragraph("Replica Shards", sTD), Paragraph("Primary shards × replica count", sTD)],
    [Paragraph("Total Shards", sTD), Paragraph("Primary + replica", sTD)],
    [Paragraph("Shards/Node", sTD), Paragraph("Total shards ÷ nodes in tier. Hard limit: 1,000/node (Elastic 8.3+ cluster.max_shards_per_node default).", sTD)],
    [Paragraph("Ceiling", sTD), Paragraph("Max shards the tier can host: hot/warm = 1,000/node; cold = 1,000/node; frozen = 3,000/node.", sTD)],
    [Paragraph("Heap/Node", sTD), Paragraph("Node RAM ÷ 2, capped at 31 GB (JVM limit)", sTD)],
    [Paragraph("Utilization Bar", sTD), Paragraph("Shards/node as % of the per-node ceiling. Red >100%, yellow >75%.", sTD)],
]
story.append(tbl(shard_data, [1.4*inch, 4.45*inch]))

story += [
    sp(6),
    h3("Cluster-Wide Checks"),
    bullet("<b>Total cluster shards vs. dynamic limit:</b> Elastic 8.3+ guideline is 1,000 shards "
           "per non-frozen data node. The calculator computes this limit dynamically — e.g., "
           "a cluster with 12 non-frozen nodes has a limit of 12,000 shards. This replaced the "
           "older fixed 50,000 soft limit in Elasticsearch 8.3."),
    bullet("<b>Hot+Warm shard density:</b> Cluster-wide shards across hot and warm tiers combined "
           "divided by total hot+warm JVM heap. Should stay below 20 shards/GB of heap."),
    sp(6),
    h3("Recommendations Panel"),
    p("When issues are detected, the Recommendations panel shows actionable guidance. Possible recommendations include:"),
    bullet("Increase target shard size (shards too small / too many)"),
    bullet("Reduce indices/day or use data streams (too many index groups)"),
    bullet("Add hot/warm nodes per zone (density too high)"),
    bullet("Reduce retention (too many shards accumulating)"),
    bullet("Increase replica count (under-replicated for HA)"),
    bullet("Frozen cache too small (less than 5% of frozen data)"),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — FORMULAS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("6. How the Calculations Work"),
    rule(),
    p("This section documents every formula the calculator uses. All variables correspond directly "
      "to input field IDs in the calculator."),
    sp(4),
    h3("6.1  ECE Instance Size Snapping"),
    p("Before computing heap or shard ceilings, node RAM is snapped to the nearest valid ECE instance size "
      "(data.default instance configuration):"),
    Paragraph("Valid sizes (GB): 1, 2, 4, 8, 16, 32, 64", sCode),
    p("The calculator picks the smallest valid size >= the computed node RAM. For nodes requiring "
      "more than 64 GB, it rounds up to the next multiple of 64 GB. This ensures all outputs "
      "are achievable on a real ECE deployment."),
    sp(6),

    h3("6.2  Compression & On-Disk Ingest"),
    p("Before any storage or shard formula runs, the raw ingest is converted to an on-disk daily volume "
      "using the Compression Ratio input (Advanced → Compression group):"),
    Paragraph("ingest_on_disk = ingest / compression_ratio   [default: ingest / 2.0]", sCode),
    sp(4),
    callout("<b>Why this matters:</b> All downstream storage and shard size calculations use "
            "ingest_on_disk, not the raw ingest. Entering a higher compression ratio (e.g. 3× for "
            "highly structured log data) reduces computed storage requirements proportionally. "
            "Set compression_ratio = 1.0 to treat ingest as already-compressed, or to plan conservatively."),
    sp(6),

    h3("6.3  Storage per Tier (Age-Based ILM)"),
    Paragraph("# Step 1: convert raw ingest to on-disk daily volume", sCode),
    Paragraph("ingest_on_disk = ingest / compression_ratio", sCode),
    Paragraph("", sCode),
    Paragraph("# Step 2: per-tier storage (uses ingest_on_disk throughout)", sCode),
    Paragraph("hot_data  = ingest_on_disk × hot_days  × (1 + hot_replicas)  × hot_overhead", sCode),
    Paragraph("warm_data = ingest_on_disk × warm_days × (1 + warm_replicas) × warm_overhead", sCode),
    Paragraph("cold_data = ingest_on_disk × cold_days × (1 + cold_replicas) × cold_overhead", sCode),
    Paragraph("", sCode),
    Paragraph("hot_storage  = hot_data  × watermark_multiplier", sCode),
    Paragraph("warm_storage = warm_data × watermark_multiplier", sCode),
    Paragraph("watermark_multiplier = 1 / (1 - watermark_pct/100)   [default: 1/0.85 ≈ 1.176]", sCode),
    sp(4),
    callout("<b>Overhead multipliers</b> are planning heuristics: hot 1.5×, warm 1.25×, cold/frozen 1.1×. "
            "Warm is lower because ILM force-merges indices before transitioning them. "
            "Actual overhead depends on field mappings, document size, and merge policy."),
    sp(6),

    h3("6.4  Storage per Tier (Size-Based ILM Rollover)"),
    p("When Size-based rollover is selected, the hot tier calculation changes:"),
    Paragraph("daily_on_disk     = ingest_on_disk × hot_overhead", sCode),
    Paragraph("active_per_stream = ceil(daily_on_disk / max_index_size_gb)", sCode),
    Paragraph("hot_active_indices = active_per_stream × indices_per_day", sCode),
    Paragraph("hot_data = hot_active_indices × max_index_size_gb × (1 + hot_replicas) × hot_overhead", sCode),
    sp(4),
    p("This models the fact that with size-based rollover, multiple partially-filled indices may "
      "exist simultaneously on hot nodes rather than a single daily index."),
    sp(6),

    h3("6.5  Object Store (Snapshots + Frozen)"),
    Paragraph("snapshot_daily    = ingest_on_disk × hot_overhead   [rolling index type]", sCode),
    Paragraph("snapshot_storage  = snapshot_daily × snapshot_retention_days", sCode),
    Paragraph("", sCode),
    Paragraph("# Non-rolling index type adds initial full snapshot:", sCode),
    Paragraph("initial_snapshot  = (hot_data + warm_data)          [non-rolling only]", sCode),
    Paragraph("", sCode),
    Paragraph("frozen_storage    = ingest_on_disk × frozen_days × (1 + frozen_replicas) × cold_overhead", sCode),
    Paragraph("object_store_total = snapshot_storage + initial_snapshot + frozen_storage", sCode),
    sp(4),
    callout("<b>Snapshot storage note:</b> The formula computes a conservative upper bound. "
            "Elasticsearch snapshots are incremental and deduplicate unchanged Lucene segments. "
            "Actual object storage is typically 30–60% lower than this estimate."),
    sp(6),

    h3("6.6  RAM per Tier"),
    Paragraph("hot_ram    = hot_data    / hot_ratio                                         ", sCode),
    Paragraph("warm_ram   = warm_data   / warm_ratio                                        ", sCode),
    Paragraph("cold_ram   = cold_data   / cold_ratio    [cold_ratio default: 160]           ", sCode),
    Paragraph("frozen_ram = frozen_obj  / frozen_ratio  [frozen_ratio default: 1500]        ", sCode),
    Paragraph("", sCode),
    Paragraph("node_ram = tier_ram / az_count / nodes_per_zone", sCode),
    Paragraph("snapped_node_ram = snapToECE(node_ram)   [snap to valid ECE instance size]  ", sCode),
    Paragraph("heap_per_node    = min(snapped_node_ram / 2, 31)   [JVM 31 GB heap cap]     ", sCode),
    sp(4),
    callout("<b>Cold tier RAM note:</b> Cold uses the same hardware profile as warm (1:160 default). "
            "The apparent cost savings of cold vs. warm come from eliminating replica copies via "
            "searchable snapshots — not from a lower RAM ratio."),
    sp(6),

    h3("6.7  Dedicated Master RAM (Auto)"),
    Paragraph("if   total_data_nodes > 30  OR  total_shards > 20,000:  master_ram = 16 GB", sCode),
    Paragraph("elif total_data_nodes > 10  OR  total_shards >  5,000:  master_ram =  8 GB", sCode),
    Paragraph("else:                                                    master_ram =  4 GB", sCode),
    sp(6),

    h3("6.8  Shard Count"),
    Paragraph("# Age-based:", sCode),
    Paragraph("pri_shards = ceil(ingest_on_disk × hot_overhead / target_shard_size) × indices_per_day", sCode),
    Paragraph("", sCode),
    Paragraph("# Size-based:", sCode),
    Paragraph("pri_shards = ceil(max_index_size / target_shard_size) × hot_active_indices", sCode),
    Paragraph("", sCode),
    Paragraph("hot_shards  = pri_shards × hot_days  × (1 + hot_replicas)  + system_shards", sCode),
    Paragraph("warm_shards = pri_shards × warm_days × (1 + warm_replicas)", sCode),
    Paragraph("cluster_shards = hot_shards + warm_shards + cold_shards + frozen_shards", sCode),
    sp(6),

    h3("6.9  Shard Density Check (per node)"),
    p("Elasticsearch 8.3+ enforces a hard per-node shard limit via cluster.max_shards_per_node. "
      "The calculator uses this as the ceiling for all tiers:"),
    Paragraph("hot_ceiling    = 1,000 shards/node   [cluster.max_shards_per_node default]", sCode),
    Paragraph("warm_ceiling   = 1,000 shards/node", sCode),
    Paragraph("cold_ceiling   = 1,000 shards/node   [searchable snapshots, no indexing]", sCode),
    Paragraph("frozen_ceiling = 3,000 shards/node   [metadata + cache only]", sCode),
    Paragraph("", sCode),
    Paragraph("shards_per_node = tier_total_shards / tier_total_nodes", sCode),
    Paragraph("density_pct     = shards_per_node / tier_ceiling × 100", sCode),
    sp(4),
    callout("<b>Note:</b> The older rule of '20 shards per GB of JVM heap' was deprecated in "
            "Elasticsearch 8.3 in favor of the flat 1,000/node limit. The calculator still "
            "shows heap-based density as a secondary metric for hot+warm tiers combined."),
    sp(6),

    h3("6.10  Cluster Shard Limit"),
    Paragraph("non_frozen_nodes  = hot_nodes + warm_nodes + cold_nodes", sCode),
    Paragraph("cluster_shard_limit = non_frozen_nodes × 1,000", sCode),
    Paragraph("warn_threshold      = cluster_shard_limit × 0.80", sCode),
    sp(4),
    p("The limit scales with cluster size: a 12-node non-frozen cluster has a 12,000 shard limit. "
      "This replaced the older fixed 50,000 soft limit in Elasticsearch 8.3."),
    sp(6),

    h3("6.11  ECE Allocator Overhead"),
    Paragraph("ECE_CTRL_PLANE_GB     = 12   [per allocator host — Elastic documentation]", sCode),
    Paragraph("allocator_overhead_gb = allocator_count × 12", sCode),
    Paragraph("allocator_total_gb    = allocator_count × allocator_ram_per_host", sCode),
    Paragraph("allocator_tenant_gb   = allocator_total_gb - allocator_overhead_gb", sCode),
    Paragraph("tenant_utilization_pct = total_ram / allocator_tenant_gb × 100", sCode),
    sp(4),
    callout("<b>What this means:</b> The sub-line under Total RAM shows how much of your allocator "
            "fleet's usable tenant RAM this deployment consumes. Above 80% is a planning warning — "
            "leave headroom for cluster resizing and other tenants."),
    sp(6),

    h3("6.12  CPU Ingest Check (Planning Heuristic)"),
    Paragraph("ingest_gb_hr       = ingest / 24", sCode),
    Paragraph("vcpus_needed       = ingest_gb_hr × 4   [heuristic: ~4 vCPU per GB/hr]", sCode),
    Paragraph("vcpus_available    = hot_vcpu_per_node × hot_total_nodes", sCode),
    Paragraph("cpu_ratio          = vcpus_needed / vcpus_available", sCode),
    p("Green: ratio < 1.0 &nbsp;·&nbsp; Yellow: 0.5–1.0 (approaching) &nbsp;·&nbsp; Red: >1.0 (CPU-bound risk)"),
    sp(4),
    warn("<b>Heuristic caveat:</b> The 4 vCPU/GB-hr rule is a workload-specific planning heuristic, "
         "not an officially published Elastic constant. CPU needs vary significantly based on "
         "indexing pipeline complexity, field mapping count, and ingest processor usage. "
         "Use this as an early warning indicator only."),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SAVING / SHARING
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("7. Compare Deployment"),
    rule(),
    p("The Compare Deployment feature lets you enter the settings of an existing live deployment "
      "and compare them side-by-side against the calculator\u2019s recommendations. It is particularly "
      "useful when evaluating whether a current cluster is right-sized, under-provisioned, or over-provisioned."),
    sp(4),
    h3("Opening the Panel"),
    p("In the Results Summary section, click the <b>Compare Deployment</b> button (next to Export JSON "
      "and Import JSON). The button turns teal when the panel is open. Click it again to collapse."),
    sp(4),
    h3("Entering Actual Values"),
    p("The panel contains input fields organized into the same tier groups as the calculator:"),
    bullet("<b>Hot / Warm / Cold / Frozen</b> \u2014 Node RAM (GB), Nodes/Zone, Availability Zones, "
           "and Storage per Node (GB). For frozen, enter Cache per Node (GB) instead of storage."),
    bullet("<b>Kibana &amp; Infrastructure</b> \u2014 Kibana RAM per instance and instance count; "
           "Master node RAM and count; Coordinator node RAM and count."),
    sp(4),
    callout("<b>Tip:</b> You do not need to fill in every field. The diff table renders automatically "
            "as soon as you enter any value \u2014 no submit button required. "
            "Leave fields blank for tiers or components not present in your deployment."),
    sp(6),
    h3("Reading the Diff Table"),
    p("The diff table renders immediately as you type and shows one row per metric per tier:"),
]

diff_data = [
    [Paragraph("Column", sTH), Paragraph("What It Shows", sTH)],
    [Paragraph("Component", sTD), Paragraph("Tier or role (Hot, Warm, Cold, Frozen, Kibana, Masters, Coordinators, Cluster)", sTD)],
    [Paragraph("Metric", sTD), Paragraph("The specific measurement being compared (e.g., Node RAM, Total Storage, Nodes/Zone)", sTD)],
    [Paragraph("Recommended", sTD), Paragraph("The value the calculator derives from your inputs and Elastic best practices", sTD)],
    [Paragraph("Actual", sTD), Paragraph("The value you entered for the live deployment", sTD)],
    [Paragraph("Delta", sTD), Paragraph("Absolute difference and % vs. the recommendation (e.g., +128 GB over, or 256 GB under)", sTD)],
    [Paragraph("Status pill", sTD),
     Paragraph("OK (green) = actual meets or exceeds recommendation.  "
               "Near (yellow) = within 20% below.  "
               "Under (red) = more than 20% below recommendation.  "
               "N/A = no recommended value available.", sTD)],
]
story.append(tbl(diff_data, [1.3*inch, 4.55*inch]))

story += [
    sp(6),
    callout("<b>Tier visibility:</b> Warm, Cold, and Frozen tier rows only appear in the diff table "
            "if that tier is enabled in the calculator, or if you have entered actual values for it."),
    sp(6),
    h3("Export Comparison JSON"),
    p("The <b>Export Comparison JSON</b> button downloads a structured JSON file containing both "
      "the recommended and actual values for all entered fields. "
      "The file is named with the client name and timestamp "
      "(e.g., ECE-Comparison-ClientName-2026-05-20.json)."),
    sp(4),
    bullet("<b>export_type: \u2018comparison\u2019</b> \u2014 distinguishes it from a standard sizing export"),
    bullet("<b>recommended</b> block \u2014 total RAM, storage, and per-tier values from the calculator"),
    bullet("<b>actual</b> block \u2014 all entered values per tier plus computed totals"),
    sp(4),
    h3("Clearing the Comparison"),
    p("The <b>Clear</b> button resets all comparison inputs and hides the diff table. "
      "The calculator\u2019s main sizing inputs and results are not affected."),
    sp(8),
    h2("8. Saving, Exporting & Printing"),
    rule(),
    sp(4),
    h3("Export JSON"),
    p("The Export JSON button downloads a complete snapshot of all input field values, including "
      "the new Compression Ratio field. The file is named with the client name and timestamp. "
      "This is the primary way to save a sizing calculation for later or to hand off to a colleague."),
    sp(4),
    h3("Import JSON"),
    p("The Import JSON button (blue, next to Export) loads a previously exported file back into "
      "the calculator. All fields — including Compression Ratio — are restored exactly as they "
      "were when the file was exported. The results section scrolls into view automatically after import."),
    sp(4),
    callout("<b>Version compatibility:</b> The importer supports both the current nested format and "
            "older flat export formats from previous versions. Legacy exports will import correctly. "
            "Exports that predate v1.0.11 will default compression_ratio to 2.0× on import."),
    sp(6),
    h3("Print / PDF Export"),
    p("The Print button in the top toolbar (or Ctrl/Cmd + P) triggers the browser's print dialog. "
      "The calculator automatically applies a print stylesheet that:"),
    bullet("Hides all input forms, navigation, and buttons — only results are printed."),
    bullet("Renders a styled header with the title and client name, and a footer with the calculator URL."),
    bullet("Formats the Node Breakdown and Storage Breakdown tables with teal column headers and alternating row shading."),
    bullet("Preserves all KPI cards (Total RAM, Total Storage, Object Store) in a 3-column layout."),
    sp(4),
    callout("<b>Saving as PDF:</b> In the browser print dialog, choose <b>Save as PDF</b> (or "
            "\u2018Microsoft Print to PDF\u2019 on Windows) as the destination to generate a PDF file "
            "suitable for proposals and client handoffs."),
    sp(6),
    h3("Reset Defaults"),
    p("The Reset button restores all fields to calculator defaults (including Compression Ratio → 2.0×). "
      "This does not affect any previously exported JSON files."),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — TIPS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("9. Tips & Common Mistakes"),
    rule(),
    sp(4),
    h3("Getting Accurate Ingest Numbers"),
    bullet("Use <b>pre-compression</b> source data size, not what you see on disk in Elasticsearch. "
           "Enter this as Daily Ingest (GB/day), then set the Compression Ratio in Advanced to match "
           "your environment (2× is a safe default; 3–4× for highly structured log data)."),
    bullet("If you only have disk usage from Kibana Stack Monitoring, multiply it by your compression ratio "
           "to back-calculate source ingest volume."),
    bullet("For SIEM deployments, EPS (events per second) × average event size (bytes) × 86,400 = GB/day."),
    bullet("<b>Compression Ratio tip:</b> Setting a higher ratio (e.g. 3×) reduces all storage and "
           "shard size estimates proportionally. If actual disk usage in Kibana is significantly lower "
           "than the calculator predicts, try increasing the compression ratio to match reality."),
    sp(6),
    h3("Choosing Retention Correctly"),
    bullet("Hot retention should reflect how long data needs fast (sub-second) query response — "
           "usually 3–14 days for logs."),
    bullet("Warm retention covers data that is queried occasionally and can tolerate slightly slower "
           "response (seconds). Force-merged and read-only."),
    bullet("Cold and frozen tiers are for compliance/archival — query performance is not guaranteed."),
    sp(6),
    h3("Shard Sizing"),
    bullet("The 10–50 GB target shard size is an Elastic best practice. Shards below 10 GB "
           "create unnecessary overhead. Shards above 50 GB slow recovery times."),
    bullet("The shard ceiling is 1,000 shards per node (Elasticsearch 8.3+ default). "
           "If the shard model shows red, the most common fix is to <b>increase target shard size</b> "
           "(reduce shard count) or <b>add nodes per zone</b> (distribute shards across more nodes)."),
    bullet("System indices shards (default 250) account for .kibana, .security, .fleet, etc. "
           "In large Elastic Security deployments this may need to be higher (400–600)."),
    sp(6),
    h3("Frozen Tier"),
    bullet("Frozen is economical but not free — ensure your object store (S3/Azure Blob/GCS) is "
           "provisioned with sufficient capacity."),
    bullet("Elastic guidance: target 5–10% of frozen data volume as local cache. "
           "Below 5% causes excessive object store fetches and slow query times. "
           "5% is the recommended starting point for new deployments."),
    sp(6),
    h3("Cold vs. Frozen: Which to Use"),
    bullet("<b>Cold:</b> Searchable snapshots with full index mounted locally. "
           "Lower latency, higher RAM. Good for data queried a few times per week."),
    bullet("<b>Frozen:</b> Partially-mounted snapshots — most data stays in object store. "
           "Very low RAM, higher query latency. Best for compliance archival rarely queried."),
    sp(6),
    h3("Common Mistakes"),
    bullet("<b>Setting retention too high on hot tier:</b> Hot nodes use expensive NVMe SSD — "
           "move data to warm after 7–14 days to reduce cost."),
    bullet("<b>Ignoring the watermark buffer:</b> Without 15% headroom, Elasticsearch will stop "
           "indexing when disks fill up. Never plan to use 100% of disk capacity."),
    bullet("<b>Zero replicas:</b> A 0-replica cluster has no data redundancy — a single node failure "
           "causes data loss and index red state."),
    bullet("<b>Using Minimal preset for production:</b> The Minimal preset (1 AZ, 0 replicas) is for "
           "dev/test only. Always use at least 2 AZs with 1 replica in production."),
    bullet("<b>Underestimating cold RAM:</b> Cold uses the same 1:160 hardware ratio as warm. "
           "The storage savings come from searchable snapshots eliminating replicas — plan cold RAM accordingly."),
    sp(8),
    rule(),
    p("For questions about this calculator or Expedient's Elastic Cloud Enterprise offerings, "
      "contact your Expedient Technical Resolution Manager."),
    sp(4),
    Paragraph(
        'Calculator: <a href="https://ece-sizer.pplx.app" color="#01696F">ece-sizer.pplx.app</a>',
        ParagraphStyle("link", parent=sNormal, alignment=1)
    ),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h2("10. References & Further Reading"),
    rule(),
    p("The formulas and thresholds in this calculator are derived from the following Elastic "
      "official documentation and published guidance. These sources are the authoritative "
      "reference for any value used in the calculator."),
    sp(8),
]

ref_sections = [
    ("Sizing & Hardware Guidance", [
        ("Elastic hardware recommendations",
         "Elastic's official hardware sizing reference for hot, warm, cold, and frozen tiers. "
         "Source for RAM:storage ratios (hot 1:30, warm 1:160, frozen 1:1500) and tier hardware profiles.",
         "https://www.elastic.co/guide/en/cloud/current/ec-hardware.html"),
        ("Size your deployment",
         "Elastic Cloud sizing guide covering RAM:storage ratios, node sizing, and tier recommendations.",
         "https://www.elastic.co/guide/en/cloud/current/ec-customize-deployment.html"),
        ("ECE allocator planning",
         "ECE documentation specifying 12 GB of ECE control plane overhead per allocator host.",
         "https://www.elastic.co/guide/en/cloud-enterprise/current/ece-allocators.html"),
        ("ECE instance configurations",
         "Reference for official ECE data.default instance sizes: 1, 2, 4, 8, 16, 32, 64 GB.",
         "https://www.elastic.co/guide/en/cloud-enterprise/current/ece-instance-configurations.html"),
    ]),
    ("Shard Management", [
        ("Size your shards",
         "Elastic's primary reference for shard sizing guidance: 10–50 GB target shard size, "
         "ILM rollover best practices, and the 1,000 shards/node cluster limit.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html"),
        ("cluster.max_shards_per_node setting",
         "Elasticsearch 8.3+ setting that enforces 1,000 shards per node as the default hard limit. "
         "Replaces the older 50,000 cluster-wide soft limit.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/misc-cluster-settings.html#cluster-max-shards-per-node"),
        ("ILM: Manage the index lifecycle",
         "Index Lifecycle Management documentation covering rollover conditions, "
         "max_primary_shard_size, and tier transition policies.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html"),
    ]),
    ("Disk & Memory", [
        ("Disk-based shard allocation",
         "Documents Elasticsearch's disk watermark defaults: low 85%, high 90%, flood 95%. "
         "Source for the 15% watermark headroom buffer used in storage calculations.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/disk-usage-watermark.html"),
        ("Heap sizing and JVM",
         "Elastic recommendation to cap JVM heap at 31 GB to stay below the compressed ordinary "
         "object pointer (compressed-oops) threshold used in shard ceiling calculations.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/advanced-configuration.html#set-jvm-heap-size"),
        ("Dedicated master nodes",
         "Elastic guidance on when to use dedicated master nodes and how to size them (4/8/16 GB). "
         "Source for the auto-master RAM scaling thresholds.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/master-election.html"),
    ]),
    ("Searchable Snapshots & Frozen Tier", [
        ("Searchable snapshots overview",
         "Explains cold and frozen tier architecture — how fully-mounted vs. partially-mounted "
         "snapshots work, and why cold tier RAM requirements align with warm tier (1:160).",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/searchable-snapshots.html"),
        ("Frozen tier",
         "Frozen tier architecture detail: partial mount strategy, local cache sizing guidance "
         "(1–10% of dataset; 5% starting point), and object store interaction.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/data-tiers.html#frozen-tier"),
        ("Snapshot and restore",
         "Documents incremental snapshot behavior and segment deduplication — basis for the "
         "note that actual snapshot storage is typically 30–60% below the calculator's upper bound.",
         "https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshot-restore.html"),
    ]),
]

for section_title, refs in ref_sections:
    story.append(h3(section_title))
    ref_data = [[Paragraph("Source", sTH), Paragraph("Description", sTH), Paragraph("URL", sTH)]]
    for title, desc, url in refs:
        ref_data.append([
            Paragraph(f"<b>{title}</b>", sTD),
            Paragraph(desc, sTDm),
            Paragraph(f'<a href="{url}" color="#01696F">{url}</a>',
                      ParagraphStyle("refurl", parent=sRef, fontSize=7.5, leading=11, wordWrap="CJK")),
        ])
    story.append(tbl(ref_data, [1.3*inch, 2.5*inch, 2.05*inch]))
    story.append(sp(10))

story += [
    sp(4),
    rule(),
    callout("<b>About this document:</b> This guide is generated from the same codebase as the "
            "calculator at ece-sizer.pplx.app. Formula corrections and new features are reflected "
            "in updated PDF versions. Current version: v1.0.11."),
]

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(
    story,
    onFirstPage=cover_page,
    onLaterPages=header_footer,
)
print(f"PDF written to {OUT}")
