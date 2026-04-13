import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Tuple

import altair as alt
import streamlit as st


st.set_page_config(
    page_title="Pulse Budget",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed",
)


DATA_FILE = Path(__file__).with_name("budget_data.json")
DEFAULT_ALLOWANCE = 150.0
CATEGORIES = [
    "Restaurant / Food",
    "Grocery / Supermarket",
    "Online Shopping",
    "Transport",
    "Coffee / Drinks",
    "Entertainment",
    "School / Supplies",
    "Other",
]


def current_week_id(today: date | None = None) -> str:
    d = today or date.today()
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def default_data() -> Dict:
    return {
        "weekly_allowance": DEFAULT_ALLOWANCE,
        "current_week_id": current_week_id(),
        "remaining_balance": DEFAULT_ALLOWANCE,
        "transactions": [],
        "weekly_history": [],
    }


def load_data() -> Dict:
    if not DATA_FILE.exists():
        data = default_data()
        save_data(data)
        return data
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = default_data()
        save_data(data)
        return data

    baseline = default_data()
    baseline.update(data)
    return baseline


def save_data(data: Dict) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def start_new_week(data: Dict, new_week_id: str) -> None:
    existing_transactions = data.get("transactions", [])
    if existing_transactions:
        data.setdefault("weekly_history", []).append(
            {
                "week_id": data.get("current_week_id", current_week_id()),
                "transactions": existing_transactions,
                "remaining_balance": data.get("remaining_balance", data["weekly_allowance"]),
                "archived_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
    data["current_week_id"] = new_week_id
    data["remaining_balance"] = float(data["weekly_allowance"])
    data["transactions"] = []


def ensure_week_is_current(data: Dict) -> bool:
    today_week = current_week_id()
    if data.get("current_week_id") != today_week:
        start_new_week(data, today_week)
        save_data(data)
        return True
    return False


def days_left_in_week(today: date | None = None) -> int:
    d = today or date.today()
    return max(1, 7 - d.weekday())


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def status_state(remaining: float, allowance: float) -> Tuple[str, str]:
    if remaining < 0:
        return "🚨 Panic Mode", "panic"
    ratio = 0 if allowance <= 0 else remaining / allowance
    if ratio > 0.5:
        return "🟢 Chill", "chill"
    if ratio >= 0.2:
        return "🟡 Careful", "careful"
    return "🔴 Danger", "danger"


def burn_rate_message(remaining: float, allowance: float, days_left: int) -> str:
    if remaining < 0:
        return "At this pace, you are already over budget."

    ideal_remaining = (allowance / 7.0) * days_left
    if remaining >= ideal_remaining * 1.05:
        return "You are on track."
    if remaining >= ideal_remaining * 0.8:
        return "Spending a little fast."
    return "At this pace, you may run out early."


def category_summary(transactions: List[Dict]) -> Tuple[Dict[str, float], float]:
    summary = {category: 0.0 for category in CATEGORIES}
    total = 0.0
    for tx in transactions:
        charged = float(tx.get("amount_charged", 0))
        category = tx.get("category", "Other")
        if category not in summary:
            summary[category] = 0.0
        summary[category] += charged
        total += charged
    summary = {k: v for k, v in summary.items() if v > 0}
    return summary, total


st.markdown(
    """
    <style>
        :root {
            --bg: #eee1ce;
            --card: #fffdfa;
            --card-soft: #f8f1e6;
            --text: #2f2922;
            --muted: #7e7264;
            --border: rgba(73, 58, 39, 0.12);
            --green: #4f8a5f;
            --yellow: #c89d4f;
            --red: #bb5d4a;
            --accent: #9c7651;
        }
        html, body, [data-testid="stAppViewContainer"], .main {
            background: var(--bg) !important;
        }
        .stApp {
            background: radial-gradient(1100px 450px at 95% -10%, #d7be9f 0%, var(--bg) 58%);
            color: var(--text);
        }
        header[data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }
        [data-testid="stToolbar"], #MainMenu, footer {
            visibility: hidden;
            height: 0;
            position: fixed;
        }
        .block-container {
            padding-top: 0.45rem;
            padding-bottom: 2rem;
            max-width: 780px;
        }
        .card {
            background: linear-gradient(180deg, #fffefc 0%, var(--card) 100%);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 10px 24px rgba(93, 74, 51, 0.10);
            margin-bottom: 0.8rem;
        }
        .hero-card {
            padding: 1.2rem 1.1rem;
            border-radius: 24px;
            background: linear-gradient(145deg, #fffaf3 0%, #fffdf9 100%);
            border: 1px solid rgba(111, 84, 54, 0.16);
        }
        .brand {
            font-size: 0.95rem;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.2rem;
            font-weight: 600;
        }
        .hero-label {
            color: #75695d;
            font-size: 0.95rem;
        }
        .hero-amount {
            font-size: clamp(2rem, 7.8vw, 3.25rem);
            line-height: 1.1;
            font-weight: 750;
            margin: 0.3rem 0 0.45rem 0;
            letter-spacing: -0.02em;
            animation: fadeup 0.45s ease;
        }
        .state-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.35rem 0.72rem;
            font-size: 0.82rem;
            border: 1px solid transparent;
            font-weight: 600;
        }
        .chill { background: rgba(79, 138, 95, 0.12); color: #3f7650; border-color: rgba(79, 138, 95, 0.28); }
        .careful { background: rgba(200, 157, 79, 0.14); color: #8f6b2f; border-color: rgba(200, 157, 79, 0.30); }
        .danger, .panic { background: rgba(187, 93, 74, 0.14); color: #8a4337; border-color: rgba(187, 93, 74, 0.30); }
        .metric-label { color: var(--muted); font-size: 0.86rem; margin-bottom: 0.2rem; }
        .metric-value { font-size: 1.55rem; font-weight: 700; margin-bottom: 0.1rem; }
        .metric-sub { color: #6f655a; font-size: 0.82rem; }
        .section-title {
            font-size: 1.02rem;
            color: #4a3f34;
            font-weight: 680;
            margin: 0.75rem 0 0.5rem 0.1rem;
        }
        .small-muted { color: var(--muted); font-size: 0.78rem; margin-top: 0.18rem; }
        .progress-track {
            width: 100%;
            height: 12px;
            border-radius: 999px;
            background: rgba(90, 70, 48, 0.12);
            overflow: hidden;
            margin: 0.45rem 0 0.2rem 0;
        }
        .progress-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.3s ease;
        }
        .bar-row { margin: 0.48rem 0 0.72rem 0; }
        .bar-head {
            display: flex; justify-content: space-between; gap: 0.8rem;
            font-size: 0.86rem; margin-bottom: 0.28rem; color: #5f5448;
        }
        .mini-track {
            width: 100%; height: 8px; border-radius: 999px;
            background: rgba(90, 70, 48, 0.12); overflow: hidden;
        }
        .mini-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #b78b5a, #8f6b44);
        }
        .tx-item {
            background: var(--card-soft);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.72rem 0.82rem;
            margin-bottom: 0.45rem;
        }
        .tx-top { display: flex; justify-content: space-between; gap: 0.8rem; align-items: center; }
        .tx-cat { font-weight: 620; font-size: 0.91rem; }
        .tx-charge { font-size: 0.95rem; font-weight: 700; }
        .tx-meta { color: var(--muted); font-size: 0.77rem; margin-top: 0.17rem; }
        .tx-note { color: #61574c; font-size: 0.81rem; margin-top: 0.2rem; }
        div[data-testid="stForm"] {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 0.95rem 0.95rem 0.35rem 0.95rem;
            margin-bottom: 0.7rem;
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 12px;
            border: 1px solid rgba(90, 70, 48, 0.2);
            background: #fffaf3;
            color: #3f342a;
            min-height: 2.75rem;
            font-weight: 620;
        }
        div[data-baseweb="input"] input, div[data-baseweb="select"] > div {
            min-height: 2.7rem;
            font-size: 1rem;
            background: #fffefb;
        }
        .floating-fab {
            position: fixed;
            right: 1rem;
            bottom: calc(0.8rem + env(safe-area-inset-bottom));
            z-index: 999;
            background: linear-gradient(135deg, #b88958, #9c7651);
            color: #fffdf8 !important;
            border-radius: 999px;
            padding: 0.68rem 1rem;
            font-weight: 700;
            text-decoration: none !important;
            box-shadow: 0 12px 24px rgba(87, 64, 40, 0.26);
        }
        .app-tabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
            padding-bottom: 0.35rem;
        }
        .app-tabs button[role="tab"] {
            border-radius: 999px;
            background: rgba(103, 81, 56, 0.08);
        }
        @keyframes fadeup {
            from { transform: translateY(7px); opacity: 0.15; }
            to { transform: translateY(0); opacity: 1; }
        }
        @media (max-width: 640px) {
            .block-container { padding-top: 0.3rem; padding-left: 0.7rem; padding-right: 0.7rem; padding-bottom: calc(2.5rem + env(safe-area-inset-bottom)); }
            .hero-card { border-radius: 20px; }
            .card { border-radius: 16px; }
            .hero-amount { font-size: 2.35rem; }
            .floating-fab { right: 0.75rem; bottom: calc(0.7rem + env(safe-area-inset-bottom)); padding: 0.65rem 0.95rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


data = load_data()
if ensure_week_is_current(data):
    st.session_state["flash_info"] = "New week detected. Budget has been reset automatically."
data["weekly_allowance"] = float(data.get("weekly_allowance", DEFAULT_ALLOWANCE))
data["remaining_balance"] = float(data.get("remaining_balance", data["weekly_allowance"]))


if "flash_info" in st.session_state:
    st.info(st.session_state.pop("flash_info"))
if "flash_success" in st.session_state:
    st.success(st.session_state.pop("flash_success"))


allowance = data["weekly_allowance"]
remaining = data["remaining_balance"]
days_left = days_left_in_week()
safe_today = remaining / days_left
state_label, state_class = status_state(remaining, allowance)
burn_msg = burn_rate_message(remaining, allowance, days_left)

if remaining > allowance * 0.5:
    progress_color = "#5f9b6e"
elif remaining >= allowance * 0.2:
    progress_color = "#c99f56"
else:
    progress_color = "#ba6a58"
progress_pct = max(0.0, min(100.0, (remaining / allowance * 100.0) if allowance > 0 else 0.0))

st.markdown(
    f"""
    <div class="card hero-card">
        <div class="brand">Pulse Budget</div>
        <div class="hero-label">Remaining This Week</div>
        <div class="hero-amount">{format_money(remaining)}</div>
        <span class="state-pill {state_class}">{state_label}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Weekly Allowance Settings", expanded=False):
    st.markdown('<div class="small-muted">Adjust your weekly cap without losing this week\'s spending history.</div>', unsafe_allow_html=True)
    new_allowance = st.number_input(
        "Weekly Allowance",
        min_value=1.0,
        value=float(data["weekly_allowance"]),
        step=5.0,
        format="%.2f",
        key="allowance_input",
    )
    if st.button("Save Weekly Allowance", use_container_width=True):
        old_allowance = float(data["weekly_allowance"])
        spent_so_far = old_allowance - float(data["remaining_balance"])
        data["weekly_allowance"] = round(float(new_allowance), 2)
        data["remaining_balance"] = round(data["weekly_allowance"] - spent_so_far, 2)
        save_data(data)
        st.session_state["flash_success"] = (
            f"Weekly allowance updated to {format_money(data['weekly_allowance'])}."
        )
        st.rerun()

col_a, col_b = st.columns(2, gap="small")
with col_a:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-label">Safe to Spend Today</div>
            <div class="metric-value">{format_money(safe_today)}</div>
            <div class="metric-sub">{days_left} day(s) left in this week</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-label">Burn Rate Check</div>
            <div class="metric-value" style="font-size:1.18rem;">{burn_msg}</div>
            <div class="metric-sub">Stay near your daily pace target</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="card">
        <div class="metric-label">Budget Remaining Progress</div>
        <div class="progress-track"><div class="progress-fill" style="width:{progress_pct:.1f}%; background:{progress_color};"></div></div>
        <div class="metric-sub">{progress_pct:.0f}% of weekly budget left</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if remaining < 0:
    st.error(f"Panic Mode: You are {format_money(abs(remaining))} over budget.")

st.markdown('<div id="quick-log-expense" class="section-title">Quick Log Expense</div>', unsafe_allow_html=True)
with st.form("expense_form", clear_on_submit=True):
    amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
    category = st.selectbox("Category", CATEGORIES)
    note = st.text_input("Optional note")
    amortized = st.checkbox("Amortize this?")
    submitted = st.form_submit_button("Add Expense", use_container_width=True)

if submitted:
    if amount <= 0:
        st.warning("Enter an amount greater than $0.")
    else:
        charged = round(amount * 0.5, 2) if amortized else round(amount, 2)
        transaction = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "amount_entered": round(float(amount), 2),
            "amount_charged": charged,
            "category": category,
            "note": note.strip(),
            "amortized": bool(amortized),
        }
        data["transactions"].append(transaction)
        data["remaining_balance"] = round(data["remaining_balance"] - charged, 2)
        save_data(data)

        if amortized:
            st.session_state["flash_success"] = (
                f"Logged {format_money(amount)} in {category}. "
                f"Only {format_money(charged)} counted this week. "
                "Remember to log the other half next week."
            )
        else:
            st.session_state["flash_success"] = f"Logged {format_money(charged)} in {category}."
        st.rerun()


quick_left, quick_right = st.columns(2, gap="small")
with quick_left:
    if st.button("Undo Last Transaction", use_container_width=True):
        if data["transactions"]:
            last_tx = data["transactions"].pop()
            data["remaining_balance"] = round(data["remaining_balance"] + float(last_tx["amount_charged"]), 2)
            save_data(data)
            st.session_state["flash_info"] = "Last transaction removed and balance restored."
            st.rerun()
        else:
            st.warning("No transactions to undo.")

with quick_right:
    if st.button("Start New Week", use_container_width=True):
        start_new_week(data, current_week_id())
        save_data(data)
        st.session_state["flash_info"] = "Fresh week started. Your balance is reset."
        st.rerun()


summary, total_spent = category_summary(data["transactions"])
st.markdown('<div class="section-title">Where Your Money Is Going</div>', unsafe_allow_html=True)
if total_spent <= 0:
    st.markdown(
        """
        <div class="card">
            <div class="metric-sub">No spending logged yet this week. Add your first expense to unlock category insights.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    sorted_cats = sorted(summary.items(), key=lambda x: x[1], reverse=True)
    chart_rows = []
    for cat, value in sorted_cats:
        pct = (value / total_spent) * 100
        chart_rows.append({"category": cat, "spent": value, "pct": pct})
    chart_data = chart_rows

    st.markdown('<div class="card">', unsafe_allow_html=True)
    donut = (
        alt.Chart(alt.Data(values=chart_data))
        .mark_arc(innerRadius=58, outerRadius=92, cornerRadius=4)
        .encode(
            theta=alt.Theta("spent:Q"),
            color=alt.Color(
                "category:N",
                scale=alt.Scale(
                    range=[
                        "#b1885b",
                        "#c5a171",
                        "#9d7e59",
                        "#d1b28a",
                        "#a58b69",
                        "#b79b79",
                        "#8f7355",
                        "#c8b18f",
                    ]
                ),
                legend=alt.Legend(
                    orient="bottom",
                    labelColor="#5f5347",
                    title=None,
                    columns=2,
                    symbolType="circle",
                ),
            ),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("spent:Q", title="Spent", format=",.2f"),
                alt.Tooltip("pct:Q", title="Share", format=".1f"),
            ],
        )
        .properties(height=250)
        .configure_view(strokeWidth=0)
        .configure(background="transparent")
    )
    st.altair_chart(donut, use_container_width=True)

    for cat, value in sorted_cats:
        pct = (value / total_spent) * 100
        st.markdown(
            f"""
            <div class="bar-row">
                <div class="bar-head"><span>{cat}</span><span>{format_money(value)} · {pct:.0f}%</span></div>
                <div class="mini-track"><div class="mini-fill" style="width:{pct:.1f}%"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    top_cat, top_amount = sorted_cats[0]
    top_pct = (top_amount / total_spent) * 100
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-label">Top Spend Category</div>
            <div class="metric-value" style="font-size:1.25rem;">{top_cat} ({top_pct:.0f}%)</div>
            <div class="metric-sub">Your largest spend area this week is {top_cat.lower()}.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    f"""
    <div class="card">
        <div class="metric-label">Weekly Snapshot</div>
        <div class="metric-sub">Total spent: <strong>{format_money(total_spent)}</strong></div>
        <div class="metric-sub">Remaining balance: <strong>{format_money(data["remaining_balance"])}</strong></div>
        <div class="metric-sub">Transactions: <strong>{len(data["transactions"])}</strong></div>
        <div class="metric-sub">Week: <strong>{data["current_week_id"]}</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown('<div class="section-title">Recent Transactions</div>', unsafe_allow_html=True)
recent = list(reversed(data["transactions"][-5:]))
if not recent:
    st.markdown(
        """
        <div class="card">
            <div class="metric-sub">No transactions yet.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for tx in recent:
        stamp = tx.get("timestamp", "")
        pretty_time = stamp.replace("T", " ")
        amortized_text = "Amortized" if tx.get("amortized") else "Standard"
        note = tx.get("note", "").strip()
        note_html = f'<div class="tx-note">{note}</div>' if note else ""
        st.markdown(
            f"""
            <div class="tx-item">
                <div class="tx-top">
                    <div class="tx-cat">{tx.get("category", "Other")}</div>
                    <div class="tx-charge">{format_money(float(tx.get("amount_charged", 0)))}</div>
                </div>
                <div class="tx-meta">
                    Entered: {format_money(float(tx.get("amount_entered", 0)))} · {amortized_text} · {pretty_time}
                </div>
                {note_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <a class="floating-fab" href="#quick-log-expense">+ Quick Log</a>
    """,
    unsafe_allow_html=True,
)
