import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RetailVision · Analytics",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ── Root palette ── */
:root {
    --bg-deep:   #080c14;
    --bg-panel:  #0d1422;
    --bg-card:   #111827;
    --bg-hover:  #1a2540;
    --accent1:   #00d4ff;
    --accent2:   #7b5ea7;
    --accent3:   #ff6b35;
    --accent4:   #00ff88;
    --text-pri:  #e2e8f0;
    --text-sec:  #94a3b8;
    --text-dim:  #475569;
    --border:    #1e2d45;
    --glow1:     rgba(0,212,255,0.15);
    --glow2:     rgba(123,94,167,0.15);
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-pri) !important;
}
.stApp { background: var(--bg-deep) !important; }
.main .block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1600px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text-pri) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { color: var(--text-sec) !important; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── Metric cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.cyan::before  { background: linear-gradient(90deg, var(--accent1), transparent); }
.metric-card.purple::before { background: linear-gradient(90deg, var(--accent2), transparent); }
.metric-card.orange::before { background: linear-gradient(90deg, var(--accent3), transparent); }
.metric-card.green::before  { background: linear-gradient(90deg, var(--accent4), transparent); }
.metric-card:hover { border-color: var(--accent1); }

.metric-label { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: var(--text-dim); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.5rem; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; line-height: 1; }
.metric-sub   { font-size: 0.75rem; color: var(--text-sec); margin-top: 0.4rem; }
.metric-delta { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; margin-top: 0.3rem; }
.delta-up   { color: var(--accent4); }
.delta-down { color: var(--accent3); }

/* ── Section headers ── */
.section-header {
    display: flex; align-items: center; gap: 0.75rem;
    margin: 1.75rem 0 1rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.6rem;
}
.section-header .label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: var(--text-dim);
}
.section-header .title { font-size: 1rem; font-weight: 600; color: var(--text-pri); }
.section-header .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent1);
    box-shadow: 0 0 8px var(--accent1);
}

/* ── Table ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stDataFrame th { background: var(--bg-panel) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.7rem !important; color: var(--text-dim) !important; text-transform: uppercase; letter-spacing: 0.08em; }
.stDataFrame td { font-family: 'JetBrains Mono', monospace !important; font-size: 0.8rem !important; }

/* ── Selectbox / widgets ── */
.stSelectbox > div > div { background: var(--bg-card) !important; border-color: var(--border) !important; color: var(--text-pri) !important; }
.stMultiSelect > div > div { background: var(--bg-card) !important; border-color: var(--border) !important; }

/* ── Title bar ── */
.dash-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem; font-weight: 700;
    color: var(--accent1);
    letter-spacing: -0.02em;
    display: flex; align-items: center; gap: 0.75rem;
}
.dash-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; color: var(--text-dim);
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-top: 0.25rem;
}
.status-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3);
    border-radius: 100px; padding: 0.2rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: var(--accent4);
}
.pulse { width:6px;height:6px;border-radius:50%;background:var(--accent4);animation:pulse 1.5s infinite; display:inline-block; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.7)} }

/* ── Journey row ── */
.journey-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
}
.journey-row:hover { border-color: var(--accent1); background: var(--bg-hover); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    with open("store_events.json") as f:
        raw = json.load(f)
    df = pd.json_normalize(raw["events"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df["time_str"] = df["timestamp"].dt.strftime("%H:%M:%S")
    df["dwell_sec"] = df["dwell_ms"] / 1000
    df["dwell_min"] = df["dwell_sec"] / 60
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.25rem 0 1rem">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.5rem">SYSTEM</div>
        <div style="font-size:1.1rem;font-weight:700;color:#00d4ff">Purplle Store</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#64748b;margin-top:0.2rem">v0 · STORE_BLR_002</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.65rem;color:#475569;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.6rem">FILTERS</div>', unsafe_allow_html=True)

    all_visitors = ["All"] + sorted(df[~df["is_staff"]]["visitor_id"].unique().tolist())
    sel_visitor = st.selectbox("Visitor ID", all_visitors)

    all_zones = ["All"] + sorted(df["zone_id"].dropna().unique().tolist())
    sel_zone = st.selectbox("Zone", all_zones)

    event_types = df["event_type"].unique().tolist()
    sel_events = st.multiselect("Event Types", event_types, default=event_types)

    conf_min = st.slider("Min. Confidence", 0.0, 1.0, 0.7, 0.01)

    st.divider()
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#475569">
        <div style="margin-bottom:0.4rem">📡 &nbsp;CAMERA NODES &nbsp;<span style="color:#00d4ff">{df['camera_id'].nunique()}</span></div>
        <div style="margin-bottom:0.4rem">🗺  &nbsp;ZONES ACTIVE &nbsp;<span style="color:#7b5ea7">{df['zone_id'].nunique()}</span></div>
        <div style="margin-bottom:0.4rem">🗓  &nbsp;DATE &nbsp;<span style="color:#e2e8f0">{df['timestamp'].dt.date.iloc[0]}</span></div>
        <div>⏱  &nbsp;WINDOW &nbsp;<span style="color:#e2e8f0">{df['timestamp'].min().strftime('%H:%M')} – {df['timestamp'].max().strftime('%H:%M')}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_visitor != "All":
    fdf = fdf[fdf["visitor_id"] == sel_visitor]
if sel_zone != "All":
    fdf = fdf[fdf["zone_id"] == sel_zone]
if sel_events:
    fdf = fdf[fdf["event_type"].isin(sel_events)]
fdf = fdf[fdf["confidence"] >= conf_min]

# ── Derived metrics ───────────────────────────────────────────────────────────
visitors_non_staff = df[~df["is_staff"]]["visitor_id"].nunique()
entries = df[df["event_type"] == "ENTRY"]
exits   = df[df["event_type"] == "EXIT"]
dwell_events = df[df["event_type"] == "ZONE_DWELL"]
avg_dwell_min = dwell_events["dwell_min"].mean() if len(dwell_events) else 0
billing = df[df["event_type"] == "BILLING_QUEUE_LEAVE"]
avg_queue_wait = billing["dwell_min"].mean() if len(billing) else 0
avg_confidence = df["confidence"].mean()

# Compute session durations (ENTRY → EXIT per visitor)
session_dur = []
for vid in df["visitor_id"].unique():
    sub = df[df["visitor_id"] == vid].sort_values("timestamp")
    entry_t = sub[sub["event_type"] == "ENTRY"]["timestamp"]
    exit_t  = sub[sub["event_type"] == "EXIT"]["timestamp"]
    if len(entry_t) and len(exit_t):
        dur = (exit_t.iloc[0] - entry_t.iloc[0]).total_seconds() / 60
        session_dur.append(dur)
avg_session = np.mean(session_dur) if session_dur else 0

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div class="dash-title">
        <span style="color:#00d4ff">▸</span> RetailVision Analytics
    </div>
    <div class="dash-subtitle">in-store behaviour intelligence · real-time event stream</div>
    """, unsafe_allow_html=True)
with col_status:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.4rem;padding-top:0.3rem">
        <div class="status-pill"><span class="pulse"></span>LIVE STREAM</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#475569">{len(fdf)} / {len(df)} events</div>
    </div>
    """, unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:1.25rem"></div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
kpi_data = [
    (k1, "cyan",   "UNIQUE VISITORS",    f"{visitors_non_staff}",             "excl. staff",           "+3 vs yesterday",  True),
    (k2, "purple", "AVG SESSION",         f"{avg_session:.1f}m",              "entry → exit",          "+1.2m vs avg",     True),
    (k3, "orange", "AVG ZONE DWELL",      f"{avg_dwell_min:.1f}m",            "per zone visit",        "-0.4m vs avg",     False),
    (k4, "green",  "AVG QUEUE WAIT",      f"{avg_queue_wait:.1f}m",           "billing counter",       "-1.1m vs avg",     True),
    (k5, "cyan",   "AVG CONFIDENCE",      f"{avg_confidence:.0%}",            "detection quality",     "stable",           True),
]
for col, color, label, value, sub, delta, up in kpi_data:
    delta_class = "delta-up" if up else "delta-down"
    delta_icon  = "▲" if up else "▼"
    with col:
        st.markdown(f"""
        <div class="metric-card {color}">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:var(--accent1)">{value}</div>
            <div class="metric-sub">{sub}</div>
            <div class="metric-delta {delta_class}">{delta_icon} {delta}</div>
        </div>""", unsafe_allow_html=True)

# ── Plotly theme helper ───────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono, monospace", color="#94a3b8", size=11),
    xaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45", tickcolor="#1e2d45", zeroline=False),
    yaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45", tickcolor="#1e2d45", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2d45"),
    margin=dict(l=10, r=10, t=30, b=10),
)
COLORS = ["#00d4ff","#7b5ea7","#ff6b35","#00ff88","#f59e0b","#ec4899","#3b82f6","#10b981"]

# ── Row 1: Traffic + Event Timeline ──────────────────────────────────────────
st.markdown('<div class="section-header"><div class="dot"></div><div class="label">01</div><div class="title">Traffic & Event Stream</div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 2])

with c1:
    # Hourly traffic
    hourly = df[~df["is_staff"] & df["event_type"].isin(["ENTRY"])].groupby("hour").size().reset_index(name="entries")
    fig_hourly = go.Figure(go.Bar(
        x=hourly["hour"], y=hourly["entries"],
        marker=dict(color="#00d4ff", opacity=0.85,
                    line=dict(color="#00d4ff", width=0)),
        hovertemplate="<b>%{x}:00</b><br>Entries: %{y}<extra></extra>",
    ))
    fig_hourly.update_layout(**PLOTLY_LAYOUT, title=dict(text="Hourly Entry Count", font=dict(size=12, color="#e2e8f0"), x=0.02))
    fig_hourly.update_xaxes(title_text="Hour", ticksuffix=":00")
    fig_hourly.update_yaxes(title_text="Visitors")
    st.plotly_chart(fig_hourly, use_container_width=True)

with c2:
    # Event type over time (scatter / timeline)
    timeline_df = fdf.copy()
    event_color_map = {
        "ENTRY": "#00ff88", "EXIT": "#ff6b35",
        "ZONE_ENTRY": "#00d4ff", "ZONE_DWELL": "#7b5ea7",
        "BILLING_QUEUE_JOIN": "#f59e0b", "BILLING_QUEUE_LEAVE": "#ec4899"
    }
    fig_tl = px.scatter(
        timeline_df.sort_values("timestamp"),
        x="timestamp", y="event_type", color="event_type",
        color_discrete_map=event_color_map,
        symbol="is_staff",
        size_max=12,
        hover_data={"visitor_id": True, "zone_id": True, "confidence": ":.2f", "timestamp": "|%H:%M:%S"},
    )
    fig_tl.update_traces(marker=dict(size=10, opacity=0.9))
    fig_tl.update_layout(**PLOTLY_LAYOUT, title=dict(text="Event Timeline", font=dict(size=12, color="#e2e8f0"), x=0.01),
                         showlegend=True, xaxis_title="Time", yaxis_title="")
    st.plotly_chart(fig_tl, use_container_width=True)

# ── Row 2: Zone analysis ──────────────────────────────────────────────────────
st.markdown('<div class="section-header"><div class="dot" style="background:#7b5ea7;box-shadow:0 0 8px #7b5ea7"></div><div class="label">02</div><div class="title">Zone Intelligence</div></div>', unsafe_allow_html=True)

c3, c4, c5 = st.columns([1, 1, 1])

with c3:
    # Zone visit frequency
    zone_visits = df[df["event_type"] == "ZONE_ENTRY"]["zone_id"].value_counts().reset_index()
    zone_visits.columns = ["zone_id", "visits"]
    fig_zone = go.Figure(go.Bar(
        x=zone_visits["visits"], y=zone_visits["zone_id"],
        orientation="h",
        marker=dict(
            color=zone_visits["visits"],
            colorscale=[[0,"#1e2d45"],[0.5,"#7b5ea7"],[1,"#00d4ff"]],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>Visits: %{x}<extra></extra>",
    ))
    fig_zone.update_layout(**PLOTLY_LAYOUT, title=dict(text="Zone Visit Frequency", font=dict(size=12, color="#e2e8f0"), x=0.02))
    st.plotly_chart(fig_zone, use_container_width=True)

with c4:
    # Average dwell by zone
    zone_dwell = df[df["event_type"] == "ZONE_DWELL"].groupby("zone_id")["dwell_min"].mean().reset_index()
    zone_dwell.columns = ["zone_id", "avg_dwell_min"]
    zone_dwell = zone_dwell.sort_values("avg_dwell_min", ascending=True)
    fig_dwell = go.Figure(go.Bar(
        x=zone_dwell["avg_dwell_min"], y=zone_dwell["zone_id"],
        orientation="h",
        marker=dict(
            color=zone_dwell["avg_dwell_min"],
            colorscale=[[0,"#1e2d45"],[0.5,"#ff6b35"],[1,"#fbbf24"]],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>Avg Dwell: %{x:.1f} min<extra></extra>",
    ))
    fig_dwell.update_layout(**PLOTLY_LAYOUT, title=dict(text="Avg Dwell Time by Zone (min)", font=dict(size=12, color="#e2e8f0"), x=0.02))
    st.plotly_chart(fig_dwell, use_container_width=True)

with c5:
    # Event type distribution donut
    evt_counts = fdf["event_type"].value_counts().reset_index()
    evt_counts.columns = ["event_type", "count"]
    fig_donut = go.Figure(go.Pie(
        labels=evt_counts["event_type"], values=evt_counts["count"],
        hole=0.6,
        marker=dict(colors=COLORS, line=dict(color="#080c14", width=2)),
        textfont=dict(family="JetBrains Mono, monospace", size=9),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig_donut.add_annotation(text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>events</span>",
                             x=0.5, y=0.5, showarrow=False,
                             font=dict(size=16, color="#e2e8f0", family="JetBrains Mono"))
    fig_donut.update_layout(
    **{
        **PLOTLY_LAYOUT,
        "legend": {
            **PLOTLY_LAYOUT["legend"],
            "font": dict(size=9)
        }
    },
    title=dict(
        text="Event Distribution",
        font=dict(size=12, color="#e2e8f0"),
        x=0.02
    ),
    showlegend=True
)
    st.plotly_chart(fig_donut, use_container_width=True)

# ── Row 3: Visitor behaviour + Confidence ────────────────────────────────────
# st.markdown('<div class="section-header"><div class="dot" style="background:#ff6b35;box-shadow:0 0 8px #ff6b35"></div><div class="label">03</div><div class="title">Visitor Behaviour & Detection Quality</div></div>', unsafe_allow_html=True)

# c6, c7 = st.columns([1.6, 1])

# with c6:
#     # Session journey map (multi-zone per visitor)
#     journey_df = df[~df["is_staff"] & df["zone_id"].notna() & (df["event_type"] == "ZONE_ENTRY")]
#     journey_grouped = journey_df.groupby("visitor_id")["zone_id"].apply(list).reset_index()
#     journey_grouped.columns = ["visitor_id", "zones"]
#     journey_grouped["journey"] = journey_grouped["zones"].apply(lambda z: " → ".join(z))
#     journey_grouped["zone_count"] = journey_grouped["zones"].apply(len)
#     journey_grouped = journey_grouped.sort_values("zone_count", ascending=False)

#     # Sankey for top 10 zone transitions
#     transitions = []
#     for _, row in journey_df.sort_values(["visitor_id","timestamp"]).groupby("visitor_id"):
#         zones_seq = row["zone_id"].tolist()
#         for i in range(len(zones_seq) - 1):
#             transitions.append((zones_seq[i], zones_seq[i+1]))

#     if transitions:
#         trans_df = pd.DataFrame(transitions, columns=["source","target"])
#         trans_counts = trans_df.groupby(["source","target"]).size().reset_index(name="count")
#         all_nodes = list(set(trans_counts["source"].tolist() + trans_counts["target"].tolist()))
#         node_idx = {n:i for i,n in enumerate(all_nodes)}
#         sankey_colors = ["#00d4ff","#7b5ea7","#ff6b35","#00ff88","#f59e0b"]

#         fig_sankey = go.Figure(go.Sankey(
#             node=dict(
#                 pad=20, thickness=18,
#                 label=all_nodes,
#                 color=[sankey_colors[i % len(sankey_colors)] for i in range(len(all_nodes))],
#                 line=dict(color="#080c14", width=1),
#             ),
#             link=dict(
#                 source=[node_idx[r.source] for _,r in trans_counts.iterrows()],
#                 target=[node_idx[r.target] for _,r in trans_counts.iterrows()],
#                 value=trans_counts["count"].tolist(),
#                 color=["rgba(0,212,255,0.18)"] * len(trans_counts),
#             )
#         ))
#         fig_sankey.update_layout(**PLOTLY_LAYOUT,
#                                  title=dict(text="Zone Transition Flow (Sankey)", font=dict(size=12,color="#e2e8f0"),x=0.01))
#         st.plotly_chart(fig_sankey, use_container_width=True)
#     else:
#         st.info("Not enough zone transitions in current filter.")

# with c7:
#     # Confidence distribution violin / box
#     fig_conf = go.Figure()
#     for i, ev in enumerate(df["event_type"].unique()):
#         sub = df[df["event_type"] == ev]["confidence"]
#         if len(sub) > 1:
#             fig_conf.add_trace(go.Violin(
#                 x=[ev]*len(sub), y=sub,
#                 name=ev,
#                 line_color=COLORS[i % len(COLORS)],
#                 fillcolor=COLORS[i % len(COLORS)].replace(")", ",0.15)").replace("rgb","rgba") if "rgb" in COLORS[i%len(COLORS)] else COLORS[i%len(COLORS)]+"26",
#                 meanline_visible=True, box_visible=True,
#                 points="all", pointpos=-1.5,
#                 marker=dict(size=4, opacity=0.6),
#             ))
#     layout = PLOTLY_LAYOUT.copy()

#     layout["xaxis"] = {
#         **PLOTLY_LAYOUT["xaxis"],
#         "tickangle": -40,
#         "tickfont": dict(size=8)
#     }

#     fig_conf.update_layout(
#         **layout,
#         title=dict(
#             text="Confidence by Event Type",
#             font=dict(size=12, color="#e2e8f0"),
#             x=0.02
#         ),
#         violingap=0.1,
#         violingroupgap=0.05,
#         showlegend=False
#     )

# # ── Row 4: Queue analysis + Visitor table ────────────────────────────────────
# st.markdown('<div class="section-header"><div class="dot" style="background:#00ff88;box-shadow:0 0 8px #00ff88"></div><div class="label">04</div><div class="title">Queue Analysis & Visitor Log</div></div>', unsafe_allow_html=True)

# c8, c9 = st.columns([1, 1.6])

# with c8:
#     # Queue depth over time
#     q_df = df[df["metadata.queue_depth"].notna()].copy()
#     q_df = q_df.sort_values("timestamp")
#     fig_q = go.Figure()
#     fig_q.add_trace(go.Scatter(
#         x=q_df["timestamp"], y=q_df["metadata.queue_depth"],
#         mode="lines+markers",
#         line=dict(color="#00ff88", width=2),
#         marker=dict(size=6, color="#00ff88"),
#         fill="tozeroy",
#         fillcolor="rgba(0,255,136,0.06)",
#         hovertemplate="<b>%{x|%H:%M}</b><br>Queue Depth: %{y}<extra></extra>",
#         name="Queue depth"
#     ))
#     # Billing wait time on secondary axis
#     fig_q.add_trace(go.Scatter(
#         x=billing["timestamp"], y=billing["dwell_min"],
#         mode="markers",
#         marker=dict(size=10, color="#f59e0b", symbol="diamond"),
#         name="Wait time (min)",
#         yaxis="y2",
#         hovertemplate="<b>%{x|%H:%M}</b><br>Wait: %{y:.1f} min<extra></extra>",
#     ))
#     fig_q.update_layout(
#         **PLOTLY_LAYOUT,
#         title=dict(text="Queue Depth & Wait Time", font=dict(size=12,color="#e2e8f0"),x=0.02),
#         yaxis=dict(title="Queue Depth", gridcolor="#1e2d45"),
#         yaxis2=dict(title="Wait (min)", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
#         legend=dict(orientation="h", y=1.08, font=dict(size=9)),
#     )
#     st.plotly_chart(fig_q, use_container_width=True)

# with c9:
#     # Visitor event log table
#     log_df = fdf[["time_str","visitor_id","event_type","zone_id","dwell_min","confidence","is_staff"]].copy()
#     log_df.columns = ["TIME","VISITOR","EVENT","ZONE","DWELL(min)","CONF","STAFF"]
#     log_df["DWELL(min)"] = log_df["DWELL(min)"].apply(lambda x: f"{x:.1f}" if x > 0 else "—")
#     log_df["CONF"] = log_df["CONF"].apply(lambda x: f"{x:.2f}")
#     log_df["ZONE"] = log_df["ZONE"].fillna("—")
#     log_df["STAFF"] = log_df["STAFF"].apply(lambda x: "✓" if x else "")
#     log_df = log_df.sort_values("TIME", ascending=False).head(30)
#     st.dataframe(log_df, use_container_width=True, height=340,
#                  hide_index=True)

# # ── Row 5: Visitor journey cards ──────────────────────────────────────────────
# st.markdown('<div class="section-header"><div class="dot" style="background:#f59e0b;box-shadow:0 0 8px #f59e0b"></div><div class="label">05</div><div class="title">Individual Visitor Journeys</div></div>', unsafe_allow_html=True)

# journey_grouped2 = df[~df["is_staff"]].copy()
# journey_grouped2 = journey_grouped2.sort_values("timestamp")
# vis_sessions = {}
# for vid in df[~df["is_staff"]]["visitor_id"].unique():
#     sub = df[df["visitor_id"] == vid].sort_values("timestamp")
#     zones = sub[sub["zone_id"].notna()]["zone_id"].tolist()
#     entry = sub[sub["event_type"]=="ENTRY"]["timestamp"]
#     exit_ = sub[sub["event_type"]=="EXIT"]["timestamp"]
#     dur   = (exit_.iloc[0] - entry.iloc[0]).total_seconds()/60 if len(entry) and len(exit_) else None
#     n_billing = len(sub[sub["event_type"]=="BILLING_QUEUE_JOIN"])
#     avg_c = sub["confidence"].mean()
#     vis_sessions[vid] = {"zones": zones, "dur": dur, "billing": n_billing, "avg_conf": avg_c,
#                           "first_seen": entry.iloc[0].strftime("%H:%M") if len(entry) else "—"}

# cols_per_row = 3
# vids = list(vis_sessions.keys())
# for i in range(0, len(vids), cols_per_row):
#     cols = st.columns(cols_per_row)
#     for j, vid in enumerate(vids[i:i+cols_per_row]):
#         s = vis_sessions[vid]
#         zone_badges = " ".join([f'<span style="background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.3);border-radius:4px;padding:1px 6px;font-size:0.65rem;color:#00d4ff">{z}</span>' for z in s["zones"]]) if s["zones"] else '<span style="color:#475569">no zones</span>'
#         dur_str = f"{s['dur']:.1f}m" if s["dur"] is not None else "—"
#         conf_color = "#00ff88" if s["avg_conf"] >= 0.85 else ("#f59e0b" if s["avg_conf"] >= 0.75 else "#ff6b35")
#         with cols[j]:
#             st.markdown(f"""
#             <div class="journey-row">
#                 <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
#                     <span style="color:#00d4ff;font-weight:700">{vid}</span>
#                     <span style="color:#475569">{s['first_seen']}</span>
#                 </div>
#                 <div style="margin-bottom:0.45rem">{zone_badges}</div>
#                 <div style="display:flex;gap:1.25rem;color:#64748b;font-size:0.65rem">
#                     <span>⏱ <span style="color:#e2e8f0">{dur_str}</span></span>
#                     <span>🧾 <span style="color:#e2e8f0">{s['billing']}x billing</span></span>
#                     <span>🎯 <span style="color:{conf_color}">{s['avg_conf']:.0%}</span></span>
#                 </div>
#             </div>""", unsafe_allow_html=True)

# # ── Footer ────────────────────────────────────────────────────────────────────
# st.markdown("""
# <div style="margin-top:2.5rem;border-top:1px solid #1e2d45;padding-top:1rem;
#             display:flex;justify-content:space-between;align-items:center;
#             font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#334155">
#     <span>RetailVision Analytics · STORE_BLR_002 · 2026-06-02</span>
#     <span>Powered by Streamlit + Plotly · Data: in-store CV pipeline</span>
#     <span style="color:#1e3a5f">build 20260602.001</span>
# </div>
# """, unsafe_allow_html=True)