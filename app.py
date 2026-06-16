"""StackTrack — peptide protocol tracker."""

import os
import re
import time
import pandas as pd
from datetime import date, timedelta, datetime

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StackTrack",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ════════════════════════════════════════════════════════════════════════════
   StackTrack Design System — Inspired by Whoop & Levels CGM
   ════════════════════════════════════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

/* ── Reset & base ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}
.stApp { background: #0a0a0a !important; }
.block-container {
    background: #0a0a0a !important;
    padding-top: 1.75rem !important;
    max-width: 1180px !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────────────────── */
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
[data-testid="InputInstructions"],
footer, footer + div,
#MainMenu { display: none !important; }

/* Make toolbar invisible but keep it in the DOM so the sidebar
   expand/collapse button (a child of stToolbar) stays functional */
[data-testid="stToolbar"] {
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: none !important;
}
/* Hide toolbar action buttons (deploy, share, etc.) but not sidebar toggle */
[data-testid="stToolbarActions"] { display: none !important; }

/* ── Typography ───────────────────────────────────────────────────────────── */
h1 {
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: #ffffff !important;
}
h2 {
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: rgba(255,255,255,0.3) !important;
    margin-top: 2rem !important;
}
h3 {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: rgba(255,255,255,0.3) !important;
}

/* ── Metric cards ─────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: rgba(167,139,250,0.06) !important;
    border: 1px solid rgba(167,139,250,0.12) !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.5rem !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="metric-container"]::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.4), transparent);
    pointer-events: none;
}
[data-testid="stMetricValue"] {
    font-size: 3rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: -0.04em !important;
    line-height: 1 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: rgba(255,255,255,0.3) !important;
}

/* ── Primary button ───────────────────────────────────────────────────────── */
[data-testid="stBaseButton-primary"] > button,
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.005em !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.3) !important;
}
[data-testid="stBaseButton-primary"] > button:hover,
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6d28d9, #7c3aed) !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary button ─────────────────────────────────────────────────────── */
.stButton > button:not([kind="primary"]),
[data-testid="stBaseButton-secondary"] > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(255,255,255,0.55) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:not([kind="primary"]):hover,
[data-testid="stBaseButton-secondary"] > button:hover {
    border-color: rgba(255,255,255,0.22) !important;
    color: rgba(255,255,255,0.85) !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Destructive (Stop) button ────────────────────────────────────────────── */
.destructive-btn button {
    color: rgba(255,107,107,0.85) !important;
    border-color: rgba(255,107,107,0.25) !important;
}
.destructive-btn button:hover {
    color: rgb(255,107,107) !important;
    border-color: rgba(255,107,107,0.5) !important;
    background: rgba(255,107,107,0.05) !important;
}

/* ── Sidebar shell ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #050505 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

/* ── Sidebar collapse/expand toggle ──────────────────────────────────────── */
/* Counteract any broad rule that could hide this wrapper */
[data-testid="stSidebarCollapsedControl"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 999 !important;
}
/* Purple-tinted toggle button to match app theme */
[data-testid="collapsedControl"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    color: #A78BFA !important;
    background: rgba(167,139,250,0.08) !important;
    border: 1px solid rgba(167,139,250,0.2) !important;
    border-radius: 8px !important;
    transition: background 0.15s, border-color 0.15s !important;
}
[data-testid="collapsedControl"]:hover {
    background: rgba(167,139,250,0.15) !important;
    border-color: rgba(167,139,250,0.35) !important;
}
[data-testid="collapsedControl"] svg {
    fill: #A78BFA !important;
    color: #A78BFA !important;
}

/* ── Sidebar logout button ────────────────────────────────────────────────── */
[data-testid="stSidebar"] .stButton > button {
    color: rgba(255,255,255,0.35) !important;
    border-color: rgba(255,255,255,0.07) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    color: rgba(255,255,255,0.7) !important;
    border-color: rgba(255,255,255,0.15) !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Sidebar nav radio → menu items ──────────────────────────────────────── */
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 1px;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] {
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.12s, border-color 0.12s;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"]:hover {
    background: rgba(255,255,255,0.03);
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] > div:first-child { display: none; }
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"]
    [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.38);
    font-size: 0.875rem;
    font-weight: 500;
    margin: 0;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"][aria-checked="true"] {
    background: rgba(124,58,237,0.08);
    border: 1px solid transparent !important;
    border-left: 3px solid #7c3aed !important;
    padding-left: 9px;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"][aria-checked="true"]
    [data-testid="stMarkdownContainer"] p {
    color: #a78bfa !important;
    font-weight: 600;
}

/* ── Streak pill ──────────────────────────────────────────────────────────── */
.streak-pill {
    background: rgba(167,139,250,0.04);
    border: 1px solid rgba(167,139,250,0.12);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 8px 0 14px;
    text-align: center;
}
.streak-pill span:last-child { color: rgba(255,255,255,0.5) !important; }

/* ── User badge ───────────────────────────────────────────────────────────── */
.user-badge {
    padding: 6px 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    margin-bottom: 10px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.4);
    display: block;
}

/* ── Cards / containers ───────────────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111111 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
}
[data-testid="stForm"] {
    background: #111111 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.5rem !important;
}

/* ── Onboarding cards ─────────────────────────────────────────────────────── */
.onboard-step {
    background: #111111;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.25rem;
    height: 100%;
}

/* ── Inputs ───────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #0f0f0f !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.9) !important;
}
.stTextInput > div > div > input:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.18) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #0f0f0f !important;
    border-color: rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.3) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 1rem !important;
    transition: color 0.15s !important;
}
.stTabs [aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom-color: #7c3aed !important;
}
.stTabs [data-baseweb="tab"]:hover { color: rgba(255,255,255,0.6) !important; }

/* ── Alerts ───────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(167,139,250,0.08) !important;
    border: 1px solid rgba(167,139,250,0.12) !important;
    border-left: 3px solid #7c3aed !important;
    border-radius: 10px !important;
}

/* ── Slider ───────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
    color: #a78bfa;
}
[data-testid="stSlider"] [role="slider"] {
    background: #7c3aed !important;
    border-color: #7c3aed !important;
}

/* ── Caption ──────────────────────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: rgba(255,255,255,0.3) !important;
    font-size: 0.72rem !important;
}

/* ── Danger zone (delete account) button ─────────────────────────────────── */
.danger-btn button {
    color: rgba(255,107,107,0.5) !important;
    border-color: transparent !important;
    font-size: 0.78rem !important;
    background: transparent !important;
    min-height: 30px !important;
}
.danger-btn button:hover {
    color: rgba(255,107,107,0.85) !important;
    background: rgba(255,107,107,0.05) !important;
}

/* ── Danger zone section wrapper ─────────────────────────────────────────── */
.danger-zone-wrapper {
    border: 1px solid rgba(255,80,80,0.2);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-top: 0.5rem;
}

/* ── Privacy policy footer link ───────────────────────────────────────────── */
.privacy-link > button {
    background: none !important;
    border: none !important;
    color: rgba(255,255,255,0.25) !important;
    font-size: 0.7rem !important;
    padding: 2px 8px !important;
    box-shadow: none !important;
    min-height: unset !important;
    height: auto !important;
    text-decoration: underline !important;
    text-decoration-color: rgba(255,255,255,0.15) !important;
    letter-spacing: 0.01em !important;
}
.privacy-link > button:hover {
    color: rgba(255,255,255,0.5) !important;
    background: none !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.05) !important; }

/* ── Mobile ───────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    /* Sidebar: full-width overlay when open */
    [data-testid="stSidebar"] {
        width: 100vw !important;
        min-width: 100vw !important;
    }

    /* Content edges */
    .block-container { padding: 0 1rem !important; }

    /* Tap targets */
    .stButton > button,
    [data-testid="stBaseButton-primary"] > button,
    [data-testid="stBaseButton-secondary"] > button {
        min-height: 44px !important;
    }

    /* Stack columns vertically */
    .stHorizontalBlock { flex-direction: column !important; }
    .stHorizontalBlock > [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Hero font sizes */
    h1 { font-size: 1.5rem !important; }
    p  { font-size: 0.85rem !important; }

    /* Full-width pills and cards */
    .streak-pill,
    [data-testid="stVerticalBlockBorderWrapper"] {
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Sidebar toggle — keep visible and tap-friendly on mobile */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"] {
        min-height: 44px !important;
        min-width: 44px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─── Supabase clients ─────────────────────────────────────────────────────────

@st.cache_resource
def _base_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_resource
def _service_client() -> Client | None:
    key = st.secrets.get("SUPABASE_SERVICE_KEY")
    if not key:
        return None
    return create_client(st.secrets["SUPABASE_URL"], key)


def db() -> Client:
    """Base client with the current user's session attached."""
    client = _base_client()
    tok = st.session_state.get("access_token")
    ref = st.session_state.get("refresh_token")
    if tok and ref:
        try:
            client.auth.set_session(tok, ref)
        except Exception:
            _clear_session()
    return client


def svc() -> Client | None:
    """Service-role client — bypasses RLS for community aggregation."""
    return _service_client()


# ─── Session helpers ──────────────────────────────────────────────────────────

def _clear_session():
    for k in ("user", "access_token", "refresh_token", "cached_username"):
        st.session_state.pop(k, None)


def get_username() -> str | None:
    """Fetch current user's username from profiles, cached in session state."""
    if "cached_username" not in st.session_state:
        try:
            result = db().table("profiles").select("username").eq("id", uid()).execute()
            data = result.data or []
            st.session_state["cached_username"] = data[0].get("username") if data else None
        except Exception:
            st.session_state["cached_username"] = None
    return st.session_state["cached_username"]


def logged_in() -> bool:
    return "user" in st.session_state


def uid() -> str:
    return st.session_state["user"]["id"]


# ─── Data layer ───────────────────────────────────────────────────────────────

def get_protocols(active_only: bool = False) -> list[dict]:
    q = (
        db()
        .table("protocols")
        .select("*")
        .eq("user_id", uid())
        .order("created_at", desc=True)
    )
    if active_only:
        q = q.eq("is_active", True)
    return q.execute().data or []


def get_logs(protocol_id: str | None = None) -> list[dict]:
    q = (
        db()
        .table("daily_logs")
        .select("*")
        .eq("user_id", uid())
        .order("log_date", desc=True)
    )
    if protocol_id:
        q = q.eq("protocol_id", protocol_id)
    return q.execute().data or []


def calculate_streak() -> int:
    result = db().table("daily_logs").select("log_date").eq("user_id", uid()).execute()
    if not result.data:
        return 0
    dates = sorted(
        {datetime.strptime(r["log_date"], "%Y-%m-%d").date() for r in result.data},
        reverse=True,
    )
    today = date.today()
    streak, expected = 0, today
    for d in dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif streak == 0 and d == today - timedelta(days=1):
            streak += 1
            expected = d - timedelta(days=1)
        else:
            break
    return streak


def get_community_summary() -> list[dict]:
    client = svc() or db()
    return client.table("community_summary").select("*").order("total_users", desc=True).execute().data or []


def get_community_progression(compound: str) -> list[dict]:
    client = svc() or db()
    return (
        client.table("community_averages")
        .select("*")
        .eq("compound", compound.lower())
        .order("protocol_day")
        .execute()
        .data or []
    )


def get_trending_compounds(days: int = 7) -> list[dict]:
    """Top 3 compounds by distinct users who logged in the past N days."""
    client = svc() or db()
    since = str(date.today() - timedelta(days=days))
    result = (
        client.table("daily_logs")
        .select("user_id, protocols(compound)")
        .gte("log_date", since)
        .execute()
    )
    compound_users: dict[str, set] = {}
    for row in result.data or []:
        proto = row.get("protocols")
        if not proto:
            continue
        key = proto["compound"].upper()
        compound_users.setdefault(key, set()).add(row["user_id"])
    return sorted(
        [{"compound": k, "users_this_week": len(v)} for k, v in compound_users.items()],
        key=lambda x: x["users_this_week"],
        reverse=True,
    )[:3]


def get_my_compound_averages() -> dict[str, dict[str, float]]:
    """My all-time average score per metric, keyed by uppercase compound name."""
    averages: dict[str, dict[str, float]] = {}
    for p in get_protocols():
        logs = get_logs(p["id"])
        if not logs:
            continue
        df = pd.DataFrame(logs)
        avgs = {
            m: float(df[m].mean())
            for m in METRICS
            if m in df.columns and df[m].notna().any()
        }
        if avgs:
            averages[p["compound"].upper()] = avgs
    return averages


def delete_log(log_id: str) -> None:
    db().table("daily_logs").delete().eq("id", log_id).eq("user_id", uid()).execute()


def update_log(log_id: str, data: dict) -> None:
    db().table("daily_logs").update(data).eq("id", log_id).eq("user_id", uid()).execute()


def update_protocol(protocol_id: str, data: dict) -> None:
    db().table("protocols").update(data).eq("id", protocol_id).eq("user_id", uid()).execute()


def delete_protocol(protocol_id: str) -> None:
    db().table("daily_logs").delete().eq("protocol_id", protocol_id).eq("user_id", uid()).execute()
    db().table("protocols").delete().eq("id", protocol_id).eq("user_id", uid()).execute()


def delete_account() -> None:
    """Delete all user data and auth account. Caller must clear session and rerun."""
    user_id = uid()
    db().table("daily_logs").delete().eq("user_id", user_id).execute()
    db().table("protocols").delete().eq("user_id", user_id).execute()
    db().table("profiles").delete().eq("id", user_id).execute()
    service = svc()
    if service:
        service.auth.admin.delete_user(user_id)


# ─── Chart constants ──────────────────────────────────────────────────────────

METRICS = ["energy", "sleep", "recovery", "libido", "mood"]

METRIC_COLORS = {
    "energy":   "#00ff88",
    "sleep":    "#00d4ff",
    "recovery": "#7c6fff",
    "libido":   "#ff9f43",
    "mood":     "#ff6b6b",
}

_BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=20),
    font=dict(size=12, color="#555555", family="Inter, system-ui, sans-serif"),
    yaxis=dict(
        range=[0, 11],
        tickvals=list(range(1, 11)),
        gridcolor="rgba(255,255,255,0.04)",
        gridwidth=0.5,
        zeroline=False,
        showline=False,
        tickfont=dict(color="#444444", size=10),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        gridwidth=0.5,
        zeroline=False,
        showline=False,
        tickfont=dict(color="#444444", size=10),
    ),
    hoverlabel=dict(
        bgcolor="#111111",
        bordercolor="#222222",
        font=dict(color="#ffffff", size=12),
    ),
)


def _chart_layout(**overrides) -> dict:
    return {**_BASE_LAYOUT, **overrides}


def _apply_trend_xaxis(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    """Fix x-axis for sparse trend charts — show dates not millisecond timestamps."""
    date_range = None
    if len(df) > 0 and "log_date" in df.columns:
        date_range = [
            (df["log_date"].min() - pd.Timedelta(days=3)).isoformat(),
            (df["log_date"].max() + pd.Timedelta(days=3)).isoformat(),
        ]
    fig.update_layout(
        xaxis=dict(
            type="date",
            tickformat="%b %d",
            tickmode="auto",
            nticks=8,
            range=date_range,
        )
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.04)",
        zeroline=False,
        range=[0, 11],
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )
    return fig


# ─── Auth page ────────────────────────────────────────────────────────────────

def page_auth():
    # Override container border with purple accent for this page only
    st.markdown("""
    <style>
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(167,139,250,0.18) !important;
        background: #0D0D13 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 0 2rem">
        <div style="font-size:3rem;margin-bottom:1rem">⚗️</div>
        <div style="
            font-size:2rem;font-weight:800;letter-spacing:-0.04em;
            color:#A78BFA;margin-bottom:12px;line-height:1
        ">StackTrack</div>
        <p style="
            color:rgba(255,255,255,0.35);font-size:0.9rem;
            max-width:320px;margin:0 auto;line-height:1.7;font-weight:400
        ">Track your peptide protocols.<br>See what actually works.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Value props ───────────────────────────────────────────────────────────
    _, c1, c2, c3, _ = st.columns([0.75, 1, 1, 1, 0.75])
    for col, icon, label in [
        (c1, "📈", "Track outcomes"),
        (c2, "🔬", "Compare compounds"),
        (c3, "👥", "Community data"),
    ]:
        with col:
            st.markdown(
                f"<div style='"
                f"text-align:center;padding:14px 10px;"
                f"background:rgba(167,139,250,0.04);"
                f"border:1px solid rgba(167,139,250,0.12);"
                f"border-radius:12px;"
                f"'>"
                f"<div style='font-size:1.35rem;margin-bottom:6px'>{icon}</div>"
                f"<div style='font-size:0.72rem;font-weight:600;"
                f"color:rgba(255,255,255,0.4);text-transform:uppercase;"
                f"letter-spacing:0.07em'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── Form card ─────────────────────────────────────────────────────────────
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        with st.container(border=True):
            tab_in, tab_up = st.tabs(["  Login  ", "  Sign Up  "])

            with tab_in:
                email    = st.text_input("Email", key="li_email")
                password = st.text_input("Password", type="password", key="li_pw")
                if st.button("Login", key="li_btn", type="primary", use_container_width=True):
                    if not (email and password):
                        st.warning("Enter your email and password.")
                    else:
                        try:
                            res = db().auth.sign_in_with_password({"email": email, "password": password})
                            st.session_state["user"]          = {"id": res.user.id, "email": res.user.email}
                            st.session_state["access_token"]  = res.session.access_token
                            st.session_state["refresh_token"] = res.session.refresh_token
                            st.rerun()
                        except Exception:
                            st.error("Invalid email or password. Please try again.")

            with tab_up:
                email    = st.text_input("Email", key="su_email")
                username = st.text_input("Username", key="su_username", placeholder="e.g. john_doe99")
                pw1      = st.text_input("Password (min 8 chars)", type="password", key="su_pw1")
                pw2      = st.text_input("Confirm password", type="password", key="su_pw2")
                if st.button("Create account", key="su_btn", type="primary", use_container_width=True):
                    if not re.match(r'^[a-z0-9_]{3,30}$', username):
                        st.error("Username must be 3–30 characters: lowercase letters, numbers, and underscores only.")
                    elif len(pw1) < 8:
                        st.error("Password must be at least 8 characters.")
                    elif pw1 != pw2:
                        st.error("Passwords don't match.")
                    else:
                        check_client = svc() or _base_client()
                        taken = check_client.table("profiles").select("id").eq("username", username).execute()
                        if taken.data:
                            st.error("Username already taken.")
                        else:
                            try:
                                res = db().auth.sign_up({"email": email, "password": pw1})
                                # Set tokens before calling db() for the profile insert
                                st.session_state["access_token"]  = res.session.access_token
                                st.session_state["refresh_token"] = res.session.refresh_token
                                profile_client = svc() or db()
                                profile_client.table("profiles").insert({
                                    "id":       res.user.id,
                                    "username": username,
                                }).execute()
                                st.session_state["user"]            = {"id": res.user.id, "email": res.user.email}
                                st.session_state["cached_username"] = username
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        "<p style='text-align:center;color:rgba(255,255,255,0.18);font-size:0.75rem;"
        "margin-top:2.5rem;letter-spacing:0.02em'>"
        "Built for biohackers. Your data is private.</p>",
        unsafe_allow_html=True,
    )


# ─── Onboarding ───────────────────────────────────────────────────────────────

def page_onboarding():
    st.markdown(
        "<div style='max-width:680px;margin:3rem auto 0;text-align:center;padding:0 1rem'>"
        "<div style='font-size:3.5rem;margin-bottom:1.25rem'>⚗️</div>"
        "<div style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;"
        "color:#ffffff;margin:0 0 0.75rem;line-height:1.1'>Welcome to StackTrack</div>"
        "<div style='color:rgba(255,255,255,0.5);font-size:1rem;margin:0 0 2.5rem;line-height:1.6'>"
        "Track your protocols. See what works.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    _, c1, c2, c3, _ = st.columns([0.25, 1, 1, 1, 0.25])
    for col, icon, title, desc in [
        (c1, "📈", "Log daily metrics",  "Rate energy, sleep, recovery, libido, and mood 1–10 each day."),
        (c2, "🔬", "Track compounds",    "Add peptide protocols with dose, route, and timing."),
        (c3, "👥", "Community insights", "See anonymized trends from the broader StackTrack community."),
    ]:
        with col:
            st.markdown(
                f"<div style='background:#161622;border:1px solid rgba(255,255,255,0.08);"
                f"border-radius:12px;padding:20px;text-align:center;box-sizing:border-box'>"
                f"<div style='font-size:1.5rem;margin-bottom:10px'>{icon}</div>"
                f"<div style='font-weight:700;color:#ffffff;font-size:0.875rem;margin-bottom:6px'>{title}</div>"
                f"<div style='color:rgba(255,255,255,0.4);font-size:0.78rem;line-height:1.5'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 1.2, 1])
    with btn_col:
        if st.button("Add your first protocol →", type="primary", use_container_width=True):
            st.session_state["nav_page"] = "🧪 My Protocols"
            st.rerun()


# ─── Stop-and-Reflect helper ──────────────────────────────────────────────────

def _render_stop_reflect(protocol: dict, button_key: str):
    """Two-step stop flow: first click prompts reflection, second confirms."""
    pid = protocol["id"]
    confirm_key = f"confirm_stop_{pid}"

    st.markdown('<div class="destructive-btn">', unsafe_allow_html=True)
    if st.button("Stop ✕", key=button_key, use_container_width=True):
        st.session_state[confirm_key] = True
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get(confirm_key, False):
        st.markdown(
            "<div style='margin-top:12px;padding:14px;background:rgba(255,255,255,0.03);"
            "border:1px solid rgba(255,255,255,0.08);border-radius:10px'>",
            unsafe_allow_html=True,
        )
        st.markdown("**Stop & reflect**")
        reflect = st.text_area(
            "What did you notice on this protocol?",
            key=f"reflect_{pid}",
            placeholder="Effects, side effects, overall impression…",
            label_visibility="collapsed",
        )
        ca, cb = st.columns(2)
        with ca:
            if st.button("✓ Confirm stop", key=f"confirm_btn_{pid}", type="primary", use_container_width=True):
                existing = protocol.get("notes") or ""
                merged = (existing + f"\n\nExit reflection: {reflect}").strip() if reflect else existing
                db().table("protocols").update({
                    "is_active": False,
                    "ended_at":  str(date.today()),
                    "notes":     merged or None,
                }).eq("id", pid).execute()
                st.session_state.pop(confirm_key, None)
                st.rerun()
        with cb:
            if st.button("Keep going →", key=f"cancel_btn_{pid}", use_container_width=True):
                st.session_state.pop(confirm_key, None)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ─── Dashboard ────────────────────────────────────────────────────────────────

def _dash_section(title: str):
    st.markdown(
        f"<div style='font-size:0.75rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.35);margin:24px 0 12px'>{title}</div>",
        unsafe_allow_html=True,
    )


def page_dashboard():
    all_protocols = get_protocols()
    all_logs      = get_logs()

    if not all_protocols:
        page_onboarding()
        return

    protocols = [p for p in all_protocols if p["is_active"]]
    streak    = calculate_streak()

    _dash_section("Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Protocols", len(protocols))
    c2.metric("🔥 Streak", f"{streak} day{'s' if streak != 1 else ''}")
    c3.metric("Total Logs", len(all_logs))

    _dash_section("Active Protocols")
    if not protocols:
        st.info("No active protocols — head to **My Protocols** to start one.")
    else:
        for p in protocols:
            st.markdown(
                "<div style='border-left:3px solid #7c3aed;background:#0f0f17;"
                "border-radius:0 12px 12px 0;margin-bottom:10px;padding:2px 0'>",
                unsafe_allow_html=True,
            )
            with st.container():
                lc, rc = st.columns([4, 1])
                with lc:
                    st.markdown(f"**{p['compound']}**")
                    detail = f"{p['dose_amount']} {p['dose_unit']} · {p['frequency']}"
                    if p.get("timing"):
                        detail += f" · {p['timing']}"
                    if p.get("source"):
                        detail += f"  |  Source: {p['source']}"
                    st.caption(detail)
                with rc:
                    days_on = (date.today() - datetime.strptime(p["started_at"], "%Y-%m-%d").date()).days
                    st.caption(f"Day {days_on + 1}")
                    _render_stop_reflect(p, button_key=f"dash_stop_{p['id']}")
            st.markdown("</div>", unsafe_allow_html=True)

    if all_logs:
        _dash_section("Recent Logs")
        display_cols = ["log_date", "energy", "sleep", "recovery", "libido", "mood", "notes"]
        df_logs = pd.DataFrame(all_logs[:10])
        display_cols = [c for c in display_cols if c in df_logs.columns]
        df_display = df_logs[display_cols].copy()
        for col in ["energy", "sleep", "recovery", "libido", "mood"]:
            if col in df_display.columns:
                df_display[col] = pd.to_numeric(df_display[col], errors="coerce").fillna(0).astype(int)
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "log_date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
                "energy":   st.column_config.ProgressColumn("⚡ Energy",   min_value=0, max_value=10, format="%d"),
                "sleep":    st.column_config.ProgressColumn("😴 Sleep",    min_value=0, max_value=10, format="%d"),
                "recovery": st.column_config.ProgressColumn("💪 Recovery", min_value=0, max_value=10, format="%d"),
                "libido":   st.column_config.ProgressColumn("🔥 Libido",   min_value=0, max_value=10, format="%d"),
                "mood":     st.column_config.ProgressColumn("🧠 Mood",     min_value=0, max_value=10, format="%d"),
                "notes":    st.column_config.TextColumn("Notes"),
            },
        )


# ─── Add Protocol ─────────────────────────────────────────────────────────────

def page_add_protocol():
    st.markdown("## Add Protocol")

    with st.form("add_protocol"):
        c1, c2 = st.columns(2)
        with c1:
            compound    = st.text_input("Compound *", placeholder="BPC-157, TB-500, GHK-Cu…")
            dose_amount = st.number_input("Dose amount *", min_value=0.001, value=250.0, step=0.001, format="%.3f")
            dose_unit   = st.selectbox("Unit", ["mcg", "mg", "IU", "ml", "other"])
            freq_options = ["daily", "EOD", "3x/week", "2x/week", "weekly", "custom"]
            freq_sel    = st.selectbox("Frequency", freq_options)
        with c2:
            timing     = st.text_input("Timing", placeholder="morning fasted, pre-workout…")
            route      = st.selectbox("Route", ["subq", "im", "oral", "nasal", "topical", "other"])
            source     = st.text_input("Source / Vendor", placeholder="optional")
            started_at = st.date_input("Start date", value=date.today())
            notes      = st.text_area("Notes", placeholder="optional")

        custom_freq = None
        if freq_sel == "custom":
            custom_freq = st.text_input("Describe frequency", placeholder="e.g. 5 days on / 2 off")

        submitted = st.form_submit_button("Add Protocol", type="primary", use_container_width=True)

    if submitted:
        if not compound.strip():
            st.error("Compound name is required.")
            return
        frequency = custom_freq if freq_sel == "custom" else freq_sel
        try:
            db().table("protocols").insert({
                "user_id":     uid(),
                "compound":    compound.strip(),
                "dose_amount": dose_amount,
                "dose_unit":   dose_unit,
                "frequency":   frequency or freq_sel,
                "timing":      timing or None,
                "route":       route,
                "source":      source or None,
                "started_at":  str(started_at),
                "notes":       notes or None,
            }).execute()
            st.success(f"✓ {compound.strip()} protocol added.")
            st.balloons()
        except Exception as e:
            st.error(str(e))


# ─── Daily Log ────────────────────────────────────────────────────────────────

def page_daily_log():
    st.markdown("## Daily Log")

    protocols = get_protocols()
    if not protocols:
        st.warning("Add a protocol first before logging.")
        return

    protocol_map = {p["compound"]: p["id"] for p in protocols}
    df_protocols = pd.DataFrame(protocols)

    compound_sel = st.selectbox("Protocol", list(protocol_map.keys()))
    selected_protocol_id = protocol_map[compound_sel]

    # ── Day-N context banner ──────────────────────────────────────────────────
    match = df_protocols[df_protocols["id"] == selected_protocol_id]
    if not match.empty:
        protocol_row = match.iloc[0]
        start_date = pd.to_datetime(protocol_row["started_at"]).date()
        days_on_protocol = (date.today() - start_date).days + 1
        logs_for_protocol = get_logs(selected_protocol_id)
        logs_this_protocol = len(logs_for_protocol)

        avg_note = ""
        if logs_this_protocol >= 3:
            df_recent = pd.DataFrame(logs_for_protocol).head(7)
            if "energy" in df_recent.columns:
                avg_energy = pd.to_numeric(df_recent["energy"], errors="coerce").mean()
                avg_note = f" · Last 7 days avg energy: <span style='color:#a78bfa;font-weight:600'>{avg_energy:.1f}/10</span>"

        log_word = "log" if logs_this_protocol == 1 else "logs"
        st.markdown(f"""
        <div style="
            background: rgba(167,139,250,0.06);
            border: 1px solid rgba(167,139,250,0.14);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-size: 0.875rem;
        ">
            📅 <strong style='color:#ffffff'>Day {days_on_protocol}</strong>
            <span style='color:rgba(255,255,255,0.4)'> of {protocol_row['compound']}
            · {logs_this_protocol} {log_word} recorded{avg_note}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Log form ──────────────────────────────────────────────────────────────
    with st.form("daily_log"):
        log_date = st.date_input("Date", value=date.today())

        st.divider()
        st.markdown(
            "#### Rate your day &nbsp;"
            "<span style='color:rgba(255,255,255,0.25);font-size:0.82rem'>1 = terrible · 10 = optimal</span>",
            unsafe_allow_html=True,
        )

        ca, cb = st.columns(2)
        with ca:
            energy   = st.slider("⚡ Energy",   1, 10, 5)
            sleep    = st.slider("😴 Sleep",    1, 10, 5)
            recovery = st.slider("💪 Recovery", 1, 10, 5)
        with cb:
            libido = st.slider("🔥 Libido", 1, 10, 5)
            mood   = st.slider("🧠 Mood",   1, 10, 5)

        notes = st.text_area("Notes", placeholder="Side effects, observations, anything notable…")
        submitted = st.form_submit_button("Save Log", type="primary", use_container_width=True)

    if submitted:
        try:
            db().table("daily_logs").upsert(
                {
                    "user_id":     uid(),
                    "protocol_id": selected_protocol_id,
                    "log_date":    str(log_date),
                    "energy":      energy,
                    "sleep":       sleep,
                    "recovery":    recovery,
                    "libido":      libido,
                    "mood":        mood,
                    "notes":       notes or None,
                },
                on_conflict="user_id,protocol_id,log_date",
            ).execute()
            st.success("Log saved.")
        except Exception as e:
            st.error(str(e))


# ─── Trends ───────────────────────────────────────────────────────────────────

def page_trends():
    st.markdown("## Trends")

    protocols = get_protocols()
    if not protocols:
        st.info("No protocols yet.")
        return

    compound_map = {p["compound"]: p["id"] for p in protocols}
    selected = st.selectbox("Protocol", list(compound_map.keys()))

    logs = get_logs(compound_map[selected])
    if not logs:
        st.info("No logs for this protocol yet — start logging daily to see trends.")
        return

    df = pd.DataFrame(logs)
    df["log_date"] = pd.to_datetime(df["log_date"])
    df = df.sort_values("log_date")

    metric_pairs = [METRICS[i:i+2] for i in range(0, len(METRICS), 2)]
    for pair in metric_pairs:
        cols = st.columns(len(pair))
        for col, metric in zip(cols, pair):
            color = METRIC_COLORS[metric]
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["log_date"],
                y=df[metric],
                mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=7, color=color),
                fill="tozeroy",
                fillcolor=f"rgba({r},{g},{b},0.08)",
                hovertemplate="%{x|%b %d} · %{y}<extra></extra>",
            ))
            fig.update_layout(
                **_chart_layout(title=metric.capitalize(), height=260, showlegend=False)
            )
            _apply_trend_xaxis(fig, df)
            col.plotly_chart(fig, use_container_width=True)

    st.markdown("#### All Metrics Overlay")
    fig_all = go.Figure()
    for metric in METRICS:
        color = METRIC_COLORS[metric]
        fig_all.add_trace(go.Scatter(
            x=df["log_date"],
            y=df[metric],
            mode="lines+markers",
            name=metric.capitalize(),
            line=dict(color=color, width=2),
            marker=dict(size=5),
            hovertemplate=f"{metric.capitalize()}: %{{y}}<br>%{{x|%b %d}}<extra></extra>",
        ))
    fig_all.update_layout(
        **_chart_layout(
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    _apply_trend_xaxis(fig_all, df)
    st.plotly_chart(fig_all, use_container_width=True)


# ─── My Protocols ─────────────────────────────────────────────────────────────

_UNITS = ["mcg", "mg", "IU", "ml", "other"]
_METRIC_ICON = {"energy": "⚡", "sleep": "😴", "recovery": "💪", "libido": "🔥", "mood": "🧠"}


def page_my_protocols():
    st.markdown("## My Protocols")

    all_protocols = get_protocols()
    active = [p for p in all_protocols if p["is_active"]]
    past   = [p for p in all_protocols if not p["is_active"]]

    tab_active, tab_trends, tab_logs, tab_add = st.tabs(
        ["  Active  ", "  Trends  ", "  Logs  ", "  Add New  "]
    )

    # ── Active protocols ──────────────────────────────────────────────────────
    with tab_active:
        if not active:
            st.info("No active protocols. Use **Add New** to start tracking a compound.")
        else:
            for p in active:
                pid      = p["id"]
                edit_key = f"editing_protocol_{pid}"
                del_key  = f"confirm_delete_protocol_{pid}"

                with st.container(border=True):
                    if st.session_state.get(edit_key):
                        st.markdown("**Edit Protocol**")
                        with st.form(f"edit_proto_{pid}"):
                            new_compound = st.text_input("Compound", value=p["compound"])
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                new_dose = st.number_input(
                                    "Dose", min_value=0.001,
                                    value=float(p["dose_amount"]),
                                    step=0.001, format="%.3f",
                                )
                            with ec2:
                                new_unit = st.selectbox(
                                    "Unit", _UNITS,
                                    index=_UNITS.index(p["dose_unit"]) if p["dose_unit"] in _UNITS else 0,
                                )
                            new_notes = st.text_area("Notes", value=p.get("notes") or "")
                            ps, pc = st.columns(2)
                            with ps:
                                saved = st.form_submit_button("Save", type="primary", use_container_width=True)
                            with pc:
                                cancelled = st.form_submit_button("Cancel", use_container_width=True)
                        if saved:
                            update_protocol(pid, {
                                "compound":    new_compound.strip(),
                                "dose_amount": new_dose,
                                "dose_unit":   new_unit,
                                "notes":       new_notes or None,
                            })
                            st.session_state.pop(edit_key, None)
                            st.rerun()
                        if cancelled:
                            st.session_state.pop(edit_key, None)
                            st.rerun()
                    else:
                        lc, rc = st.columns([3, 1])
                        with lc:
                            st.markdown(f"**{p['compound']}**")
                            parts = [
                                f"{p['dose_amount']} {p['dose_unit']}",
                                p["frequency"],
                                p.get("timing") or "",
                                p.get("route") or "",
                            ]
                            st.caption("  ·  ".join(x for x in parts if x))
                            if p.get("source"):
                                st.caption(f"Source: {p['source']}")
                            if p.get("notes"):
                                st.caption(f"📝 {p['notes']}")
                        with rc:
                            days_on = (
                                date.today()
                                - datetime.strptime(p["started_at"], "%Y-%m-%d").date()
                            ).days
                            st.caption(f"Day {days_on + 1}")
                            st.caption(p["started_at"])
                            if st.button("Edit ✎", key=f"edit_proto_btn_{pid}", use_container_width=True):
                                st.session_state[edit_key] = True
                                st.rerun()
                            _render_stop_reflect(p, button_key=f"mp_stop_{pid}")
                            st.markdown('<div class="destructive-btn">', unsafe_allow_html=True)
                            if st.button("Delete 🗑", key=f"del_proto_btn_{pid}", use_container_width=True):
                                st.session_state[del_key] = True
                            st.markdown('</div>', unsafe_allow_html=True)

                    if st.session_state.get(del_key):
                        st.markdown(
                            "<p style='color:rgba(255,107,107,0.8);font-size:0.85rem;margin:10px 0 6px'>"
                            "⚠️ This will also delete all logs for this protocol. Are you sure?</p>",
                            unsafe_allow_html=True,
                        )
                        da, db_ = st.columns(2)
                        with da:
                            if st.button("Yes, delete", key=f"del_proto_confirm_{pid}", type="primary", use_container_width=True):
                                delete_protocol(pid)
                                st.session_state.pop(del_key, None)
                                st.rerun()
                        with db_:
                            if st.button("Cancel", key=f"del_proto_cancel_{pid}", use_container_width=True):
                                st.session_state.pop(del_key, None)
                                st.rerun()

        if past:
            with st.expander(f"Past protocols ({len(past)})"):
                for p in past:
                    pid     = p["id"]
                    del_key = f"confirm_delete_protocol_{pid}"
                    ended   = p.get("ended_at") or "—"
                    cl, cr  = st.columns([4, 1])
                    with cl:
                        st.markdown(
                            f"**{p['compound']}** · {p['dose_amount']} {p['dose_unit']} "
                            f"· {p['started_at']} → {ended}"
                        )
                        if p.get("notes"):
                            st.caption(p["notes"])
                    with cr:
                        st.markdown('<div class="destructive-btn">', unsafe_allow_html=True)
                        if st.button("Delete", key=f"past_del_{pid}", use_container_width=True):
                            st.session_state[del_key] = True
                        st.markdown('</div>', unsafe_allow_html=True)
                    if st.session_state.get(del_key):
                        st.warning("This will also delete all logs for this protocol.")
                        pa, pb = st.columns(2)
                        with pa:
                            if st.button("Confirm delete", key=f"past_del_confirm_{pid}", type="primary", use_container_width=True):
                                delete_protocol(pid)
                                st.session_state.pop(del_key, None)
                                st.rerun()
                        with pb:
                            if st.button("Cancel", key=f"past_del_cancel_{pid}", use_container_width=True):
                                st.session_state.pop(del_key, None)
                                st.rerun()

    # ── Trend charts ──────────────────────────────────────────────────────────
    with tab_trends:
        if not all_protocols:
            st.info("Add a protocol first to see trends.")
        else:
            compound_map = {p["compound"]: p["id"] for p in all_protocols}
            sel = st.selectbox("Protocol", list(compound_map.keys()), key="mp_trends_sel")
            logs = get_logs(compound_map[sel])

            if not logs:
                st.info("No logs yet — head to **Log Today** to start recording.")
            else:
                df = pd.DataFrame(logs)
                df["log_date"] = pd.to_datetime(df["log_date"])
                df = df.sort_values("log_date")

                pairs = [METRICS[i : i + 2] for i in range(0, len(METRICS), 2)]
                for pair in pairs:
                    cols = st.columns(len(pair))
                    for col, metric in zip(cols, pair):
                        color = METRIC_COLORS[metric]
                        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df["log_date"],
                            y=df[metric],
                            mode="lines+markers",
                            line=dict(color=color, width=2.5, shape="spline", smoothing=0.8),
                            marker=dict(size=6, color=color, line=dict(color="#0a0a0a", width=1.5)),
                            fill="tozeroy",
                            fillcolor=f"rgba({r},{g},{b},0.07)",
                            hovertemplate=f"<b>{metric.capitalize()}</b>: %{{y}}<br>%{{x|%b %d}}<extra></extra>",
                        ))
                        fig.update_layout(**_chart_layout(title=metric.capitalize(), height=250, showlegend=False, hovermode="x"))
                        _apply_trend_xaxis(fig, df)
                        col.plotly_chart(fig, use_container_width=True)

                st.markdown("#### All metrics")
                fig_all = go.Figure()
                for metric in METRICS:
                    color = METRIC_COLORS[metric]
                    fig_all.add_trace(go.Scatter(
                        x=df["log_date"], y=df[metric],
                        mode="lines+markers", name=metric.capitalize(),
                        line=dict(color=color, width=2, shape="spline", smoothing=0.8),
                        marker=dict(size=5, color=color),
                        hovertemplate=f"{metric.capitalize()}: %{{y}}<br>%{{x|%b %d}}<extra></extra>",
                    ))
                fig_all.update_layout(**_chart_layout(height=400, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)))
                _apply_trend_xaxis(fig_all, df)
                st.plotly_chart(fig_all, use_container_width=True)

    # ── Logs ──────────────────────────────────────────────────────────────────
    with tab_logs:
        if not all_protocols:
            st.info("No protocols yet.")
        else:
            compound_map = {p["compound"]: p["id"] for p in all_protocols}
            sel_logs = st.selectbox("Protocol", list(compound_map.keys()), key="logs_tab_sel")
            logs = get_logs(compound_map[sel_logs])

            if not logs:
                st.info("No logs for this protocol yet.")
            else:
                for log in logs:
                    lid      = log["id"]
                    edit_key = f"editing_log_{lid}"
                    del_key  = f"confirm_delete_log_{lid}"

                    with st.container(border=True):
                        if st.session_state.get(edit_key):
                            st.markdown(f"**Editing — {log['log_date']}**")
                            with st.form(f"edit_log_{lid}"):
                                ll1, ll2 = st.columns(2)
                                with ll1:
                                    e_energy   = st.slider("⚡ Energy",   1, 10, int(log.get("energy") or 5))
                                    e_sleep    = st.slider("😴 Sleep",    1, 10, int(log.get("sleep") or 5))
                                    e_recovery = st.slider("💪 Recovery", 1, 10, int(log.get("recovery") or 5))
                                with ll2:
                                    e_libido = st.slider("🔥 Libido", 1, 10, int(log.get("libido") or 5))
                                    e_mood   = st.slider("🧠 Mood",   1, 10, int(log.get("mood") or 5))
                                e_notes = st.text_area("Notes", value=log.get("notes") or "")
                                ls, lc_ = st.columns(2)
                                with ls:
                                    log_saved = st.form_submit_button("Save", type="primary", use_container_width=True)
                                with lc_:
                                    log_cancelled = st.form_submit_button("Cancel", use_container_width=True)
                            if log_saved:
                                update_log(lid, {
                                    "energy": e_energy, "sleep": e_sleep,
                                    "recovery": e_recovery, "libido": e_libido,
                                    "mood": e_mood, "notes": e_notes or None,
                                })
                                st.session_state.pop(edit_key, None)
                                st.rerun()
                            if log_cancelled:
                                st.session_state.pop(edit_key, None)
                                st.rerun()
                        else:
                            lc2, rc2 = st.columns([5, 1])
                            with lc2:
                                vals = "  ".join(
                                    f"{_METRIC_ICON[m]} **{int(log[m])}**"
                                    for m in METRICS if log.get(m) is not None
                                )
                                st.markdown(f"**{log['log_date']}** — {vals}")
                                if log.get("notes"):
                                    st.caption(log["notes"])
                            with rc2:
                                if st.button("Edit ✎", key=f"log_edit_{lid}", use_container_width=True):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                                st.markdown('<div class="destructive-btn">', unsafe_allow_html=True)
                                if st.button("Delete", key=f"log_del_{lid}", use_container_width=True):
                                    st.session_state[del_key] = True
                                st.markdown('</div>', unsafe_allow_html=True)

                        if st.session_state.get(del_key):
                            ca2, cb2 = st.columns(2)
                            with ca2:
                                if st.button("Confirm delete", key=f"log_del_confirm_{lid}", type="primary", use_container_width=True):
                                    delete_log(lid)
                                    st.session_state.pop(del_key, None)
                                    st.rerun()
                            with cb2:
                                if st.button("Cancel", key=f"log_del_cancel_{lid}", use_container_width=True):
                                    st.session_state.pop(del_key, None)
                                    st.rerun()

    # ── Add new protocol ──────────────────────────────────────────────────────
    with tab_add:
        with st.form("add_protocol_mp"):
            c1, c2 = st.columns(2)
            with c1:
                compound    = st.text_input("Compound *", placeholder="BPC-157, TB-500, GHK-Cu…")
                dose_amount = st.number_input("Dose amount *", min_value=0.001, value=250.0, step=0.001, format="%.3f")
                dose_unit   = st.selectbox("Unit", _UNITS)
                freq_sel    = st.selectbox("Frequency", ["daily", "EOD", "3x/week", "2x/week", "weekly", "custom"])
            with c2:
                timing     = st.text_input("Timing", placeholder="morning fasted, pre-workout…")
                route      = st.selectbox("Route", ["subq", "im", "oral", "nasal", "topical", "other"])
                source     = st.text_input("Source / Vendor", placeholder="optional")
                started_at = st.date_input("Start date", value=date.today())
                notes      = st.text_area("Notes", placeholder="optional")

            custom_freq = None
            if freq_sel == "custom":
                custom_freq = st.text_input("Describe frequency", placeholder="e.g. 5 days on / 2 off")

            submitted = st.form_submit_button("Add Protocol", type="primary", use_container_width=True)

        if submitted:
            if not compound.strip():
                st.error("Compound name is required.")
            else:
                frequency = custom_freq if freq_sel == "custom" else freq_sel
                try:
                    db().table("protocols").insert({
                        "user_id":     uid(),
                        "compound":    compound.strip(),
                        "dose_amount": dose_amount,
                        "dose_unit":   dose_unit,
                        "frequency":   frequency or freq_sel,
                        "timing":      timing or None,
                        "route":       route,
                        "source":      source or None,
                        "started_at":  str(started_at),
                        "notes":       notes or None,
                    }).execute()
                    st.success(f"✓ {compound.strip()} added.")
                    st.balloons()
                    st.session_state["protocols_tab"] = 0
                    time.sleep(0.8)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


# ─── Community ────────────────────────────────────────────────────────────────

def page_community():
    st.markdown("## Community")
    st.caption(
        "Anonymous aggregates from all users. Compounds only appear once 3+ people have logged data."
    )

    if svc() is None:
        st.warning(
            "Set `SUPABASE_SERVICE_KEY` in your `.env` to enable cross-user aggregation. "
            "Without it the community views may only reflect your own data.",
            icon="⚠️",
        )

    summary = get_community_summary()
    if not summary:
        st.info("No community data yet — keep logging! Data appears once 3+ users track the same compound.")
        return

    compound_options = [s["compound"].upper() for s in summary]
    selected         = st.selectbox("Compound", compound_options)
    compound_row     = next(s for s in summary if s["compound"].upper() == selected)

    st.markdown(
        f"<p style='color:rgba(255,255,255,0.25);font-size:0.8rem'>"
        f"{compound_row['total_users']} users · {compound_row['total_log_entries']} log entries</p>",
        unsafe_allow_html=True,
    )

    community_avgs = [float(compound_row.get(f"avg_{m}") or 0) for m in METRICS]

    user_protocols = [p for p in get_protocols() if p["compound"].lower() == selected.lower()]
    user_avgs, user_entries = [0.0] * len(METRICS), 0
    if user_protocols:
        user_all_logs = []
        for p in user_protocols:
            user_all_logs.extend(get_logs(p["id"]))
        if user_all_logs:
            df_u = pd.DataFrame(user_all_logs)
            user_avgs   = [float(df_u[m].mean()) for m in METRICS]
            user_entries = len(user_all_logs)

    def _bar(title: str, avgs: list[float], subtitle: str) -> go.Figure:
        fig = go.Figure(go.Bar(
            x=[m.capitalize() for m in METRICS],
            y=avgs,
            marker_color=[METRIC_COLORS[m] for m in METRICS],
            text=[f"{v:.1f}" for v in avgs],
            textposition="outside",
        ))
        fig.update_layout(
            **_chart_layout(
                title=f"{title}  <sup style='color:#444'>{subtitle}</sup>",
                height=320,
                showlegend=False,
            )
        )
        return fig

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            _bar("Community", community_avgs, f"{compound_row['total_users']} users"),
            use_container_width=True,
        )
    with c2:
        if user_entries:
            st.plotly_chart(
                _bar("You", user_avgs, f"{user_entries} entries"),
                use_container_width=True,
            )
        else:
            st.info(f"Log some **{selected}** entries to see your personal comparison here.")

    progression = get_community_progression(selected)
    if progression:
        st.markdown("#### Day-by-Day Community Progression")
        df_prog = pd.DataFrame(progression)
        fig_prog = go.Figure()
        for metric in METRICS:
            fig_prog.add_trace(go.Scatter(
                x=df_prog["protocol_day"],
                y=df_prog[f"avg_{metric}"],
                mode="lines+markers",
                name=metric.capitalize(),
                line=dict(color=METRIC_COLORS[metric], width=2),
                marker=dict(size=5),
                hovertemplate=f"Day %{{x}} · {metric.capitalize()}: %{{y:.1f}}<extra></extra>",
            ))
        fig_prog.update_layout(
            **_chart_layout(
                xaxis_title="Day of Protocol",
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
        )
        st.plotly_chart(fig_prog, use_container_width=True)


# ─── Community Insights ───────────────────────────────────────────────────────

def page_community_insights():
    st.markdown("## Community Insights")
    st.caption("All data is anonymous — no usernames or identifying information is ever shown.")

    if svc() is None:
        st.warning(
            "Set `SUPABASE_SERVICE_KEY` in your `.env` for full cross-user data. "
            "Without it these views may only reflect your own logs.",
            icon="⚠️",
        )

    summary = get_community_summary()
    summary_by_compound = {s["compound"].upper(): s for s in summary}

    # ── Trending this week ────────────────────────────────────────────────────
    st.markdown("### Trending This Week")
    trending = get_trending_compounds(days=7)

    if not trending:
        st.info("No community activity in the past 7 days yet — keep logging!")
    else:
        medals = ["🥇", "🥈", "🥉"]
        cols = st.columns(len(trending))
        for col, medal, item in zip(cols, medals, trending):
            compound = item["compound"]
            user_count = item["users_this_week"]
            row = summary_by_compound.get(compound, {})
            best_metric, best_val = None, 0.0
            for m in METRICS:
                v = float(row.get(f"avg_{m}") or 0)
                if v > best_val:
                    best_metric, best_val = m, v
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='font-size:1.4rem;line-height:1'>{medal}</div>"
                        f"<div style='font-size:1rem;font-weight:700;margin-top:6px;color:#ffffff'>{compound}</div>",
                        unsafe_allow_html=True,
                    )
                    if user_count >= 2:
                        st.markdown(
                            f"<div style='color:rgba(255,255,255,0.3);font-size:0.78rem;margin-top:3px'>"
                            f"{user_count} users active this week</div>",
                            unsafe_allow_html=True,
                        )
                        if best_metric:
                            color = METRIC_COLORS[best_metric]
                            st.markdown(
                                f"<div style='margin-top:10px;color:{color};font-size:0.82rem'>"
                                f"Highest: {best_metric.capitalize()} {best_val:.1f}/10</div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown(
                            "<div style='font-size:0.78rem;color:rgba(255,255,255,0.25);padding:8px 0'>"
                            "Be among the first to build community data for this compound.</div>",
                            unsafe_allow_html=True,
                        )

    st.divider()

    # ── All compounds overview ────────────────────────────────────────────────
    st.markdown("### All Compounds Overview")
    st.caption("Compounds with fewer than 3 reporting users are hidden to preserve anonymity.")

    if not summary or len(summary) < 3:
        st.markdown("""
        <div style="
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 32px 24px;
            text-align: center;
            margin: 8px 0;
        ">
            <div style="font-size: 1.6rem; margin-bottom: 10px;">🔬</div>
            <div style="font-weight: 600; color: rgba(255,255,255,0.7);
                        margin-bottom: 6px; font-size: 0.95rem;">Community benchmarks coming soon</div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.3);
                        max-width: 380px; margin: 0 auto; line-height: 1.7;">
                Once 3+ users track the same compound, you'll see:<br>
                average scores by week of protocol · dose response data ·
                most reported side effects
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_sum = pd.DataFrame(summary)
        df_sum["compound"] = df_sum["compound"].str.upper()
        df_sum = df_sum.rename(columns={
            "compound":          "Compound",
            "total_users":       "Users",
            "total_log_entries": "Entries",
            "avg_energy":        "Energy",
            "avg_sleep":         "Sleep",
            "avg_recovery":      "Recovery",
            "avg_libido":        "Libido",
            "avg_mood":          "Mood",
        }).sort_values("Users", ascending=False).reset_index(drop=True)

        score_cols = ["Energy", "Sleep", "Recovery", "Libido", "Mood"]
        styled = (
            df_sum[["Compound", "Users", "Entries"] + score_cols]
            .style
            .background_gradient(subset=score_cols, cmap="RdYlGn", vmin=1, vmax=10)
            .format({c: "{:.1f}" for c in score_cols})
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.divider()

    # ── You vs Community ──────────────────────────────────────────────────────
    st.markdown("### You vs Community")

    if not summary or len(summary) < 3:
        st.markdown("""
        <div style="
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 32px 24px;
            text-align: center;
            margin: 8px 0;
        ">
            <div style="font-size: 1.6rem; margin-bottom: 10px;">🔬</div>
            <div style="font-weight: 600; color: rgba(255,255,255,0.7);
                        margin-bottom: 6px; font-size: 0.95rem;">Community benchmarks coming soon</div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.3);
                        max-width: 380px; margin: 0 auto; line-height: 1.7;">
                Once 3+ users track the same compound, you'll see how your scores
                compare against the community average.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    my_avgs_by_compound = get_my_compound_averages()
    compound_options = [s["compound"].upper() for s in summary]

    default_idx = next(
        (i for i, c in enumerate(compound_options) if c in my_avgs_by_compound),
        0,
    )
    selected = st.selectbox("Select compound", compound_options, index=default_idx)
    compound_row = summary_by_compound[selected]

    community_avgs = [float(compound_row.get(f"avg_{m}") or 0) for m in METRICS]
    my_avgs_map    = my_avgs_by_compound.get(selected, {})
    my_avgs        = [my_avgs_map.get(m, 0.0) for m in METRICS]
    has_my_data    = any(v > 0 for v in my_avgs)

    metric_labels = [m.capitalize() for m in METRICS]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Community avg",
        x=metric_labels,
        y=community_avgs,
        marker_color="#1a1a1a",
        marker_line=dict(color="#333333", width=1),
        text=[f"{v:.1f}" for v in community_avgs],
        textposition="outside",
        textfont=dict(color="#555555"),
        hovertemplate="%{x}: %{y:.1f}<extra>Community</extra>",
    ))
    if has_my_data:
        fig.add_trace(go.Bar(
            name="You",
            x=metric_labels,
            y=my_avgs,
            marker_color="#7c3aed",
            text=[f"{v:.1f}" for v in my_avgs],
            textposition="outside",
            textfont=dict(color="#a78bfa"),
            hovertemplate="%{x}: %{y:.1f}<extra>You</extra>",
        ))
    fig.update_layout(
        **_chart_layout(
            barmode="group",
            height=420,
            bargap=0.25,
            bargroupgap=0.1,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    if not has_my_data:
        st.caption(f"Log some **{selected}** entries to add your bar to the chart.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Community users", int(compound_row["total_users"]))
    c2.metric("Community log entries", int(compound_row["total_log_entries"]))
    if has_my_data:
        my_overall   = sum(my_avgs) / len(my_avgs)
        comm_overall = sum(community_avgs) / len(community_avgs)
        c3.metric(
            "Your overall avg",
            f"{my_overall:.1f}",
            delta=f"{my_overall - comm_overall:+.1f} vs community",
        )


# ─── Privacy Policy ───────────────────────────────────────────────────────────

def page_privacy_policy():
    st.markdown("## Privacy Policy")
    st.caption("Effective June 2025")
    st.divider()

    st.markdown("### What we collect")
    st.markdown(
        "- **Account data** — your email address and username, used only to identify your account\n"
        "- **Protocol data** — compound name, dose, frequency, route, timing, source, and any notes you enter\n"
        "- **Log data** — daily ratings (energy, sleep, recovery, libido, mood 1–10) and optional notes"
    )

    st.markdown("### How we use it")
    st.markdown(
        "- To power your personal dashboard, trend charts, and protocol history\n"
        "- To generate **anonymous** community benchmarks — your individual entries are never attributed to you\n"
        "- We do not use your data for advertising, model training, or any purpose outside the app"
    )

    st.markdown("### Data sharing")
    st.markdown(
        "- We never sell your data to third parties\n"
        "- Community insights are fully anonymized. A compound only appears in community views once "
        "**3 or more distinct users** have logged data for it — making individual identification statistically impossible\n"
        "- Infrastructure is provided by Supabase (database and auth) and Streamlit Community Cloud (hosting). "
        "Each has its own privacy policy governing their infrastructure"
    )

    st.markdown("### Your rights")
    st.markdown(
        "- **Delete your account** at any time from the sidebar — this permanently removes your account "
        "and all associated protocols, logs, and profile data\n"
        "- Deletion is immediate and irreversible. We do not retain backups of deleted accounts\n"
        "- You may request a copy of your data by contacting us"
    )

    st.markdown("### Contact")
    st.markdown("Questions or concerns: **privacy@stacktrack.app**")
    st.caption("This is a placeholder address — update before public launch.")


# ─── Settings ─────────────────────────────────────────────────────────────────

def _settings_section(title: str):
    st.markdown(
        f"<div style='font-size:0.75rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.35);margin:0 0 12px'>{title}</div>",
        unsafe_allow_html=True,
    )


def page_settings():
    st.markdown("## Settings")

    # ── Account ───────────────────────────────────────────────────────────────
    _settings_section("Account")
    with st.container(border=True):
        raw_email = st.session_state["user"].get("email", "")
        st.text_input("Email", value=raw_email, disabled=True)
        _uname = get_username()
        with st.form("change_username_form"):
            new_username = st.text_input(
                "Username",
                value=_uname or "",
                placeholder="e.g. john_doe99",
            )
            if st.form_submit_button("Update username", type="primary"):
                if not re.match(r'^[a-z0-9_]{3,30}$', new_username):
                    st.error("Username must be 3–30 characters: lowercase letters, numbers, and underscores only.")
                elif new_username == _uname:
                    st.info("That's already your username.")
                else:
                    check_client = svc() or _base_client()
                    taken = check_client.table("profiles").select("id").eq("username", new_username).execute()
                    if taken.data and taken.data[0].get("id") != uid():
                        st.error("Username already taken.")
                    else:
                        try:
                            db().table("profiles").update({"username": new_username}).eq("id", uid()).execute()
                            st.session_state["cached_username"] = new_username
                            st.success("Username updated.")
                        except Exception as e:
                            st.error(str(e))

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Appearance ────────────────────────────────────────────────────────────
    _settings_section("Appearance")
    with st.container(border=True):
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:space-between;padding:4px 0'>"
            "<span style='color:rgba(255,255,255,0.7);font-size:0.875rem'>Dark mode</span>"
            "<span style='font-size:0.72rem;color:rgba(255,255,255,0.3);"
            "background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);"
            "border-radius:20px;padding:2px 10px'>Default</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Additional theme options coming soon.")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Session ───────────────────────────────────────────────────────────────
    _settings_section("Session")
    with st.container(border=True):
        if st.button("Logout", use_container_width=True):
            try:
                db().auth.sign_out()
            except Exception:
                pass
            _clear_session()
            st.rerun()

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Danger zone ───────────────────────────────────────────────────────────
    st.markdown('<div class="danger-zone-wrapper">', unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.75rem;font-weight:600;text-transform:uppercase;"
        "letter-spacing:0.1em;color:rgba(255,107,107,0.6);margin-bottom:0.75rem'>Danger Zone</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:rgba(255,255,255,0.45);font-size:0.875rem;margin:0 0 1rem'>"
        "Permanently deletes your account and <strong>all</strong> your data. "
        "This cannot be undone.</p>",
        unsafe_allow_html=True,
    )
    del_confirm = st.text_input(
        "Type DELETE to confirm",
        key="delete_account_confirm",
        label_visibility="collapsed",
        placeholder="Type DELETE to confirm",
    )
    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
    if st.button(
        "Delete my account",
        key="delete_account_btn",
        disabled=(del_confirm != "DELETE"),
        use_container_width=True,
    ):
        try:
            delete_account()
        except Exception as e:
            st.error(str(e))
        _clear_session()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Privacy dialog ───────────────────────────────────────────────────────────

@st.dialog("Privacy Policy", width="large")
def _show_privacy_dialog():
    page_privacy_policy()


# ─── Navigation + main ────────────────────────────────────────────────────────

PAGES = {
    "📊 Dashboard":          page_dashboard,
    "📝 Log Today":          page_daily_log,
    "🧪 My Protocols":       page_my_protocols,
    "🌐 Community Insights": page_community_insights,
    "⚙️ Settings":           page_settings,
}


def main():
    if not logged_in():
        page_auth()
        return

    nav_options = list(PAGES.keys())

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = nav_options[0]

    with st.sidebar:
        # Wordmark
        st.markdown(
            "<div style='padding:4px 4px 20px'>"
            "<div style='display:flex;align-items:center;gap:8px'>"
            "<span style='font-size:1.15rem'>⚗️</span>"
            "<span style='font-size:1.1rem;font-weight:800;letter-spacing:-0.03em;color:#ffffff'>Stack</span>"
            "<span style='font-size:1.1rem;font-weight:800;letter-spacing:-0.03em;color:#a78bfa'>Track</span>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        # User badge — prefer username from profiles, fall back to email-derived name
        _uname = get_username()
        if _uname:
            display_name = f"@{_uname}"
        else:
            raw_email = st.session_state["user"].get("email", "")
            display_name = raw_email.split("@")[0].replace(".", " ").replace("_", " ").title()
        st.sidebar.markdown(
            f"<span class='user-badge'>👤 {display_name}</span>",
            unsafe_allow_html=True,
        )

        # Streak pill
        streak = calculate_streak()
        if streak > 0:
            flames = "🔥" * min(streak // 7 + 1, 3)
            st.markdown(
                f"<div class='streak-pill'>"
                f"<span style='font-size:1.1rem'>{flames}</span>&nbsp;"
                f"<span style='color:#a78bfa;font-weight:700;font-size:1.05rem'>{streak}</span>"
                f"<span style='font-size:0.8rem'> day streak</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='streak-pill'>"
                "<span style='font-size:0.82rem'>Log today to start a streak</span>"
                "</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # Navigation
        default_idx = (
            nav_options.index(st.session_state["nav_page"])
            if st.session_state["nav_page"] in nav_options
            else 0
        )
        page = st.radio(
            "nav",
            nav_options,
            index=default_idx,
            label_visibility="collapsed",
        )
        st.session_state["nav_page"] = page

        # Privacy policy — tiny muted footer link
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="privacy-link" style="text-align:center">', unsafe_allow_html=True)
        if st.button("Privacy Policy", key="sidebar_privacy_btn"):
            _show_privacy_dialog()
        st.markdown('</div>', unsafe_allow_html=True)

    PAGES[page]()


if __name__ == "__main__":
    main()
