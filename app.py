"""StackTrack — peptide protocol tracker."""

import os
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

# ─── Global CSS ───────────────────────────────────────────────────────────────
# Tasks 1 & 6: Chrome hiding + typography + theme
st.markdown("""
<style>
/* ── Hide Streamlit chrome ──────────────────────────────────────────────────── */
[data-testid="stToolbar"]         { display: none !important; }
[data-testid="stDecoration"]      { display: none !important; }
[data-testid="stAppDeployButton"] { display: none !important; }
footer                            { display: none !important; }
footer + div                      { display: none !important; }
#MainMenu                         { display: none !important; }
.block-container                  { padding-top: 1.5rem !important; }

/* ── Typography ─────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }
h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: #ffffff !important;
}
h2 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    color: rgba(255,255,255,0.85) !important;
    margin-top: 1.5rem !important;
}
h3 {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: rgba(255,255,255,0.75) !important;
}
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: #a78bfa !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: rgba(255,255,255,0.45) !important;
}
[data-testid="stBaseButton-primary"] > button,
button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
}
[data-testid="stBaseButton-primary"] > button:hover,
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: rgba(255,255,255,0.04) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.25) !important;
}
[data-testid="stTab"] {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
button[data-baseweb="tab"][aria-selected="true"] { color: #a78bfa !important; }
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left: 3px solid #7c3aed !important;
}

/* ── Metric cards ────────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #161622;
    border: 1px solid #1E1E2E;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}

/* ── Buttons ─────────────────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7C3AED, #5B21B6);
    border: none;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: transform 0.1s, box-shadow 0.1s;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6D28D9, #4C1D95);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(124,58,237,0.35);
}
.stButton > button[kind="secondary"] { border-color: #2D2D3A; color: #888; }

/* ── Sidebar shell ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0a0a0f !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Sidebar nav radio → menu items ──────────────────────────────────────────── */
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] {
    padding: 7px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"]:hover { background: #1A1A2E; }
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] > div:first-child { display: none; }
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"]
    [data-testid="stMarkdownContainer"] p {
    color: #6B7280;
    font-size: 0.9rem;
    margin: 0;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"][aria-checked="true"]
    [data-testid="stMarkdownContainer"] p {
    color: #A78BFA !important;
    font-weight: 600;
}
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"][aria-checked="true"] {
    background: #1A1A2E;
}

/* ── Streak pill ──────────────────────────────────────────────────────────────── */
.streak-pill {
    background: linear-gradient(135deg, #1E1230, #16122A);
    border: 1px solid #3D1F7A;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 10px 0 14px;
    text-align: center;
}

/* ── Onboarding card ─────────────────────────────────────────────────────────── */
.onboard-step {
    background: #111120;
    border: 1px solid #1E1E2E;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    height: 100%;
}

/* ── Containers ──────────────────────────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #1E1E2E !important;
    border-radius: 10px;
    background: #161622;
}
[data-testid="stForm"] {
    border: 1px solid #1E1E2E !important;
    border-radius: 12px;
    background: #161622;
}

/* ── Inputs ───────────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: #0D0D0D !important;
    border-color: #2D2D3A !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1E1E2E;
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] { color: #666; }
.stTabs [aria-selected="true"] {
    color: #A78BFA !important;
    border-bottom-color: #7C3AED !important;
}

/* ── Misc ─────────────────────────────────────────────────────────────────────── */
hr { border-color: #1E1E2E !important; }
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
    color: #A78BFA;
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
    for k in ("user", "access_token", "refresh_token"):
        st.session_state.pop(k, None)


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
            # Streak started yesterday — still alive
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


# ─── Chart constants ──────────────────────────────────────────────────────────

METRICS = ["energy", "sleep", "recovery", "libido", "mood"]

METRIC_COLORS = {
    "energy":   "#7C3AED",
    "sleep":    "#10B981",
    "recovery": "#3B82F6",
    "libido":   "#F59E0B",
    "mood":     "#EF4444",
}

_BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=20),
    font=dict(size=12, color="#9CA3AF", family="Inter, system-ui, sans-serif"),
    yaxis=dict(
        range=[0, 11],
        tickvals=list(range(1, 11)),
        gridcolor="#1A1A2E",
        gridwidth=0.5,
        zeroline=False,
        showline=False,
        tickfont=dict(color="#6B7280", size=10),
    ),
    xaxis=dict(
        gridcolor="#1A1A2E",
        gridwidth=0.5,
        zeroline=False,
        showline=False,
        tickfont=dict(color="#6B7280", size=10),
    ),
    hoverlabel=dict(
        bgcolor="#1E1E2E",
        bordercolor="#2D2D3A",
        font=dict(color="#E2E8F0", size=12),
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
        gridcolor="rgba(255,255,255,0.05)",
        zeroline=False,
        range=[0, 11],
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )
    return fig


# ─── Auth page ────────────────────────────────────────────────────────────────

def page_auth():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown(
            "<h1 style='text-align:center;color:#A78BFA;font-size:2.4rem;margin-bottom:0'>⚗️ StackTrack</h1>"
            "<p style='text-align:center;color:#555;margin-top:6px;margin-bottom:2rem'>"
            "Peptide protocol tracker</p>",
            unsafe_allow_html=True,
        )

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
            email = st.text_input("Email", key="su_email")
            pw1   = st.text_input("Password (min 8 chars)", type="password", key="su_pw1")
            pw2   = st.text_input("Confirm password", type="password", key="su_pw2")
            if st.button("Create account", key="su_btn", type="primary", use_container_width=True):
                if len(pw1) < 8:
                    st.error("Password must be at least 8 characters.")
                elif pw1 != pw2:
                    st.error("Passwords don't match.")
                else:
                    try:
                        db().auth.sign_up({"email": email, "password": pw1})
                        st.success("Account created — check your email to confirm, then log in.")
                    except Exception as e:
                        st.error(str(e))


# ─── Onboarding ───────────────────────────────────────────────────────────────

def page_onboarding():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            "<div style='text-align:center;padding:2.5rem 0 2rem'>"
            "<div style='font-size:3.5rem;margin-bottom:0.5rem'>⚗️</div>"
            "<h1 style='color:#A78BFA;font-size:1.9rem;margin:0 0 1rem'>Welcome to StackTrack</h1>"
            "<p style='color:#9CA3AF;font-size:0.95rem;line-height:1.75;margin-bottom:2rem'>"
            "StackTrack lets you log your peptide and biohacking protocols — tracking dose, "
            "frequency, and how you feel across energy, sleep, recovery, libido, and mood. "
            "Compare your personal scores anonymously against others running the same compound."
            "</p></div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        steps = [
            ("1. Add a protocol", "Name the compound, set dose, frequency, and route of administration."),
            ("2. Log daily",       "Rate energy, sleep, recovery, libido, and mood 1–10 each day."),
            ("3. Track trends",    "Plotly charts show how every metric evolves across your protocol."),
            ("4. Compare",         "See anonymous community averages for anyone running the same compound."),
        ]
        for i, (title, body) in enumerate(steps):
            with (c1 if i % 2 == 0 else c2):
                st.markdown(
                    f"<div class='onboard-step'>"
                    f"<p style='font-weight:600;color:#E2E8F0;margin:0 0 4px'>{title}</p>"
                    f"<p style='color:#6B7280;font-size:0.85rem;margin:0'>{body}</p>"
                    f"</div><br>",
                    unsafe_allow_html=True,
                )

        if st.button(
            "Get started — add your first protocol →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["nav_page"] = "🧪 My Protocols"
            st.rerun()


# ─── Stop-and-Reflect helper ──────────────────────────────────────────────────

def _render_stop_reflect(protocol: dict, button_key: str):
    """Two-step stop flow: first click prompts reflection, second confirms."""
    pid = protocol["id"]
    confirm_key = f"confirm_stop_{pid}"

    if st.button("Stop ✕", key=button_key, use_container_width=True):
        st.session_state[confirm_key] = True

    if st.session_state.get(confirm_key, False):
        st.markdown(
            "<div style='margin-top:12px;padding:12px;background:rgba(124,58,237,0.08);"
            "border:1px solid rgba(124,58,237,0.2);border-radius:8px'>",
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

def page_dashboard():
    all_protocols = get_protocols()
    all_logs      = get_logs()

    if not all_protocols and not all_logs:
        page_onboarding()
        return

    protocols = [p for p in all_protocols if p["is_active"]]
    streak    = calculate_streak()

    st.markdown("## Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Active Protocols", len(protocols))
    c2.metric("🔥 Streak", f"{streak} day{'s' if streak != 1 else ''}")
    c3.metric("Total Logs", len(all_logs))

    st.divider()
    st.markdown("### Active Protocols")

    if not protocols:
        st.info("No active protocols — head to **My Protocols** to start one.")
    else:
        for p in protocols:
            with st.container(border=True):
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

    # Task 5: Fixed Recent Logs table with explicit column order and ProgressColumn
    if all_logs:
        st.divider()
        st.markdown("### Recent Logs")
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

    # Task 7: Protocol selector outside the form so the context banner reacts instantly
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
                avg_note = f" · Last 7 days avg energy: **{avg_energy:.1f}/10**"

        log_word = "log" if logs_this_protocol == 1 else "logs"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(109,40,217,0.06));
            border: 1px solid rgba(124,58,237,0.25);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-size: 0.875rem;
        ">
            📅 <strong>Day {days_on_protocol}</strong> of {protocol_row['compound']}
            · <span style="color:rgba(255,255,255,0.55)">{logs_this_protocol}
            {log_word} recorded{avg_note}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Log form ──────────────────────────────────────────────────────────────
    with st.form("daily_log"):
        log_date = st.date_input("Date", value=date.today())

        st.divider()
        st.markdown(
            "#### Rate your day &nbsp;"
            "<span style='color:#555;font-size:0.85rem'>1 = terrible · 10 = optimal</span>",
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

    # 2-column grid of per-metric area charts
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
            # Task 4: fix x-axis for sparse/single-point charts
            _apply_trend_xaxis(fig, df)
            col.plotly_chart(fig, use_container_width=True)

    # Combined overlay chart
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


# ─── My Protocols (composite: list + trends + add) ────────────────────────────

def page_my_protocols():
    st.markdown("## My Protocols")

    all_protocols = get_protocols()
    active = [p for p in all_protocols if p["is_active"]]
    past   = [p for p in all_protocols if not p["is_active"]]

    tab_active, tab_trends, tab_add = st.tabs(["  Active  ", "  Trends  ", "  Add New  "])

    # ── Active protocols ──────────────────────────────────────────────────────
    with tab_active:
        if not active:
            st.info("No active protocols. Use **Add New** to start tracking a compound.")
        else:
            for p in active:
                with st.container(border=True):
                    lc, rc = st.columns([4, 1])
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
                        # Task 9: two-step stop-and-reflect flow
                        _render_stop_reflect(p, button_key=f"mp_stop_{p['id']}")

        if past:
            with st.expander(f"Past protocols ({len(past)})"):
                for p in past:
                    ended = p.get("ended_at") or "—"
                    st.markdown(
                        f"**{p['compound']}** · {p['dose_amount']} {p['dose_unit']} "
                        f"· {p['started_at']} → {ended}"
                    )

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

                # Per-metric area charts, 2-column grid
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
                            marker=dict(
                                size=6, color=color,
                                line=dict(color="#0D0D0D", width=1.5),
                            ),
                            fill="tozeroy",
                            fillcolor=f"rgba({r},{g},{b},0.07)",
                            hovertemplate=f"<b>{metric.capitalize()}</b>: %{{y}}<br>%{{x|%b %d}}<extra></extra>",
                        ))
                        fig.update_layout(
                            **_chart_layout(
                                title=metric.capitalize(),
                                height=250,
                                showlegend=False,
                                hovermode="x",
                            )
                        )
                        # Task 4: fix x-axis for sparse/single-point charts
                        _apply_trend_xaxis(fig, df)
                        col.plotly_chart(fig, use_container_width=True)

                # Combined overlay
                st.markdown("#### All metrics")
                fig_all = go.Figure()
                for metric in METRICS:
                    color = METRIC_COLORS[metric]
                    fig_all.add_trace(go.Scatter(
                        x=df["log_date"],
                        y=df[metric],
                        mode="lines+markers",
                        name=metric.capitalize(),
                        line=dict(color=color, width=2, shape="spline", smoothing=0.8),
                        marker=dict(size=5, color=color),
                        hovertemplate=f"{metric.capitalize()}: %{{y}}<br>%{{x|%b %d}}<extra></extra>",
                    ))
                fig_all.update_layout(
                    **_chart_layout(
                        height=400,
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    )
                )
                _apply_trend_xaxis(fig_all, df)
                st.plotly_chart(fig_all, use_container_width=True)

    # ── Add new protocol ──────────────────────────────────────────────────────
    with tab_add:
        with st.form("add_protocol_mp"):
            c1, c2 = st.columns(2)
            with c1:
                compound    = st.text_input("Compound *", placeholder="BPC-157, TB-500, GHK-Cu…")
                dose_amount = st.number_input("Dose amount *", min_value=0.001, value=250.0, step=0.001, format="%.3f")
                dose_unit   = st.selectbox("Unit", ["mcg", "mg", "IU", "ml", "other"])
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
                    # Task 3: navigate back to Active tab on next render
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
        f"<p style='color:#666;font-size:0.85rem'>"
        f"{compound_row['total_users']} users · {compound_row['total_log_entries']} log entries</p>",
        unsafe_allow_html=True,
    )

    community_avgs = [float(compound_row.get(f"avg_{m}") or 0) for m in METRICS]

    # Fetch user's own averages for this compound
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
                title=f"{title}  <sup style='color:#666'>{subtitle}</sup>",
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

    # Day-by-day community progression
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
    st.markdown("## 🌐 Community Insights")
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
    st.markdown("### 🔥 Trending This Week")
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
                        f"<div style='font-size:1.6rem;line-height:1'>{medal}</div>"
                        f"<div style='font-size:1.05rem;font-weight:700;margin-top:6px'>{compound}</div>",
                        unsafe_allow_html=True,
                    )
                    # Task 8: guard on user count — 1 user looks sad
                    if user_count >= 2:
                        st.markdown(
                            f"<div style='color:#666;font-size:0.82rem;margin-top:3px'>"
                            f"{user_count} users active this week</div>",
                            unsafe_allow_html=True,
                        )
                        if best_metric:
                            color = METRIC_COLORS[best_metric]
                            st.markdown(
                                f"<div style='margin-top:10px;color:{color};font-size:0.85rem'>"
                                f"Highest: {best_metric.capitalize()} {best_val:.1f}/10</div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown(
                            "<div style='font-size:0.82rem;color:rgba(255,255,255,0.35);padding:8px 0'>"
                            "Be among the first to build community data for this compound.</div>",
                            unsafe_allow_html=True,
                        )

    st.divider()

    # ── All compounds overview ────────────────────────────────────────────────
    st.markdown("### 📋 All Compounds Overview")
    st.caption("Compounds with fewer than 3 reporting users are hidden to preserve anonymity.")

    if not summary or len(summary) < 3:
        # Task 8: richer empty state
        st.markdown("""
        <div style="
            background: rgba(255,255,255,0.02);
            border: 1px dashed rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 28px 24px;
            text-align: center;
            margin: 8px 0;
        ">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">🔬</div>
            <div style="font-weight: 600; color: rgba(255,255,255,0.8);
                        margin-bottom: 6px;">Community benchmarks coming soon</div>
            <div style="font-size: 0.82rem; color: rgba(255,255,255,0.4);
                        max-width: 380px; margin: 0 auto;">
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

    # ── You vs Community grouped bar chart ────────────────────────────────────
    st.markdown("### 👤 You vs Community")

    if not summary or len(summary) < 3:
        # Task 8: richer empty state
        st.markdown("""
        <div style="
            background: rgba(255,255,255,0.02);
            border: 1px dashed rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 28px 24px;
            text-align: center;
            margin: 8px 0;
        ">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">🔬</div>
            <div style="font-weight: 600; color: rgba(255,255,255,0.8);
                        margin-bottom: 6px;">Community benchmarks coming soon</div>
            <div style="font-size: 0.82rem; color: rgba(255,255,255,0.4);
                        max-width: 380px; margin: 0 auto;">
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
        marker_color="#374151",
        marker_line=dict(color="#4B5563", width=1),
        text=[f"{v:.1f}" for v in community_avgs],
        textposition="outside",
        textfont=dict(color="#9CA3AF"),
        hovertemplate="%{x}: %{y:.1f}<extra>Community</extra>",
    ))
    if has_my_data:
        fig.add_trace(go.Bar(
            name="You",
            x=metric_labels,
            y=my_avgs,
            marker_color="#7C3AED",
            text=[f"{v:.1f}" for v in my_avgs],
            textposition="outside",
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


# ─── Navigation + main ────────────────────────────────────────────────────────

PAGES = {
    "📊 Dashboard":          page_dashboard,
    "📝 Log Today":          page_daily_log,
    "🧪 My Protocols":       page_my_protocols,
    "🌐 Community Insights": page_community_insights,
}


def main():
    if not logged_in():
        page_auth()
        return

    nav_options = list(PAGES.keys())

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = nav_options[0]

    with st.sidebar:
        st.markdown(
            "<h1 style='color:#A78BFA;font-size:1.45rem;margin-bottom:2px'>⚗️ StackTrack</h1>",
            unsafe_allow_html=True,
        )

        # Task 2: display name instead of raw email
        raw_email = st.session_state["user"].get("email", "")
        display_name = raw_email.split("@")[0].replace(".", " ").replace("_", " ").title()
        st.sidebar.markdown(f"""
        <div style="
            padding: 6px 10px;
            background: rgba(123, 47, 190, 0.15);
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 0.8rem;
            color: rgba(255,255,255,0.6);
        ">👤 {display_name}</div>
        """, unsafe_allow_html=True)

        # ── Streak pill ───────────────────────────────────────────────────────
        streak = calculate_streak()
        if streak > 0:
            flames = "🔥" * min(streak // 7 + 1, 3)
            st.markdown(
                f"<div class='streak-pill'>"
                f"<span style='font-size:1.1rem'>{flames}</span>&nbsp;"
                f"<span style='color:#A78BFA;font-weight:700;font-size:1.05rem'>{streak}</span>"
                f"<span style='color:#4B5563;font-size:0.8rem'> day streak</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='streak-pill'>"
                "<span style='color:#4B5563;font-size:0.85rem'>Log today to start a streak</span>"
                "</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Navigation ────────────────────────────────────────────────────────
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

        st.divider()
        if st.button("Logout", use_container_width=True):
            try:
                db().auth.sign_out()
            except Exception:
                pass
            _clear_session()
            st.rerun()

    PAGES[page]()


if __name__ == "__main__":
    main()
