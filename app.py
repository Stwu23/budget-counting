"""
Pulse — behavior-driven weekly budget app.
Single-file Streamlit · JSON persistence · i18n · warm wood-tone UI.
Inline editing · custom categories · minimal language toggle.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import altair as alt
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Pulse", page_icon="◉", layout="centered",
                   initial_sidebar_state="collapsed")

DATA_FILE = Path(__file__).with_name("budget_data.json")
DEFAULT_ALLOWANCE = 150.0

DEFAULT_CATS_ZH = [
    "餐厅 / 外食", "超市 / 杂货", "网购", "交通",
    "咖啡 / 饮品", "娱乐", "学习 / 文具", "其他",
]
DEFAULT_CATS_EN = [
    "Restaurant / Food", "Grocery / Supermarket", "Online Shopping", "Transport",
    "Coffee / Drinks", "Entertainment", "School / Supplies", "Other",
]

# ── i18n ──────────────────────────────────────────────────────────────────

LANG: dict[str, dict[str, str]] = {
    "zh": {
        "brand": "Pulse",
        "remaining_week": "本周剩余",
        "safe_today": "今日可花",
        "days_left": "天",
        "remaining_div_days": "剩余 ÷ 天数",
        "burn_rate": "支出节奏",
        "burn_vs_ideal": "与理想日节奏对比",
        "budget_progress": "本周预算进度",
        "pct_left": "剩余占周预算",
        "panic_over": "Panic Mode：你已超支",
        "weekly_allowance": "每周额度",
        "save": "保存",
        "cancel": "取消",
        "done": "完成",
        "allowance_saved": "周额度已更新为 {v}。",
        "target_name": "目标名称",
        "target_total": "目标总价",
        "monthly_goal": "月度目标",
        "target_saved_msg": "储蓄目标已保存。",
        "log_expense": "快速记账",
        "amount": "金额",
        "category": "分类",
        "note": "备注（可选）",
        "amortize": "分期计入？仅计本周一半",
        "add_btn": "记一笔",
        "enter_positive": "请输入大于 $0 的金额。",
        "logged": "已记录 {v} · {c}",
        "amortize_msg": "仅一半计入本周，记得下周补记另一半。",
        "undo": "撤销上一笔",
        "undo_done": "已撤销上一笔，余额已恢复。",
        "no_undo": "没有可撤销的记录。",
        "new_week": "新一周",
        "new_week_done": "已开始新一周，流水已清空，结余已计入目标。",
        "auto_week": "新的一周已开始，预算已自动重置。",
        "category_insights": "分类洞察",
        "no_spending": "本周尚无支出，记账后即可查看分类占比。",
        "insight": "洞察",
        "top_spend": "最大支出: {c} ({p}%)",
        "top_spend_sub": "本周最大支出类别是 {c}。",
        "target_section": "储蓄目标",
        "completed": "已完成",
        "projected_save": "本周预计结余",
        "formula_save": "= max(周额度 − 已花, 0)",
        "last_week_credit": "上周计入目标",
        "auto_credit": "关周时自动入账",
        "extra_deposit": "额外存入",
        "extra_deposit_desc": "手动向目标存入（不影响周余额）",
        "extra_note": "备注（可选）",
        "add_deposit": "存入目标",
        "deposit_done": "已向目标额外存入 {v}。",
        "breakdown_auto": "自动结余",
        "breakdown_extra": "额外存入",
        "breakdown_total": "目标合计",
        "target_pace": "目标节奏",
        "monthly_goal_label": "月度目标",
        "month_auto": "本月自动结余",
        "month_extra": "本月额外存入",
        "month_total": "本月合计",
        "pace_ratio_label": "节奏比",
        "pace_tip": "若节奏落后，适当放慢消费更有利于完成「{n}」。",
        "history": "最近流水",
        "no_tx": "暂无记录。",
        "entered": "录入",
        "burn_on": "节奏正常",
        "burn_fast": "花得有点快",
        "burn_early": "照此速度可能提前花完",
        "burn_over": "已超支 — 先稳住节奏",
        "chill": "🟢 轻松",
        "careful": "🟡 注意",
        "danger": "🔴 危险",
        "panic": "🚨 超支",
        "ahead": "🟢 领先节奏",
        "on_track": "🟡 节奏正常",
        "behind": "🔴 落后节奏",
        "week_col": "周",
        "budget_col": "额度",
        "spent_col": "支出",
        "saved_col": "省下",
        "manage_cats": "管理分类",
        "add_category": "添加新分类",
        "add": "添加",
        "cat_added": "已添加分类「{c}」。",
        "cat_deleted": "已删除分类「{c}」。",
        "cat_exists": "该分类已存在。",
        "cat_empty": "请输入分类名称。",
        "pace_saved": "月度目标已更新。",
        "tx_deleted": "已删除该笔记录，余额已恢复。",
        "tx_updated": "记录已更新。",
        "edit_amount": "金额",
        "edit_cat": "分类",
        "edit_note": "备注",
    },
    "en": {
        "brand": "Pulse",
        "remaining_week": "Remaining This Week",
        "safe_today": "Safe to Spend Today",
        "days_left": "day(s)",
        "remaining_div_days": "remaining ÷ days",
        "burn_rate": "Burn Rate",
        "burn_vs_ideal": "vs. ideal daily pace",
        "budget_progress": "Budget Progress",
        "pct_left": "of weekly budget left",
        "panic_over": "Panic Mode: You are over budget by",
        "weekly_allowance": "Weekly Allowance",
        "save": "Save",
        "cancel": "Cancel",
        "done": "Done",
        "allowance_saved": "Weekly allowance updated to {v}.",
        "target_name": "Target Name",
        "target_total": "Total Price",
        "monthly_goal": "Monthly Goal",
        "target_saved_msg": "Savings target saved.",
        "log_expense": "Log Expense",
        "amount": "Amount",
        "category": "Category",
        "note": "Note (optional)",
        "amortize": "Amortize? Count only half this week",
        "add_btn": "Add Expense",
        "enter_positive": "Enter an amount greater than $0.",
        "logged": "Logged {v} · {c}",
        "amortize_msg": "Only half counted this week. Remember to log the other half next week.",
        "undo": "Undo Last",
        "undo_done": "Last transaction removed, balance restored.",
        "no_undo": "No transactions to undo.",
        "new_week": "New Week",
        "new_week_done": "New week started. Savings credited to target.",
        "auto_week": "New week detected — budget reset automatically.",
        "category_insights": "Category Insights",
        "no_spending": "No spending logged yet this week.",
        "insight": "Insight",
        "top_spend": "Top spend: {c} ({p}%)",
        "top_spend_sub": "Your largest spend area this week is {c}.",
        "target_section": "Savings Target",
        "completed": "completed",
        "projected_save": "Projected Savings",
        "formula_save": "= max(allowance − spent, 0)",
        "last_week_credit": "Last Week Credit",
        "auto_credit": "Auto-credited on week close",
        "extra_deposit": "Extra Deposit",
        "extra_deposit_desc": "Add money to target (does not affect weekly balance)",
        "extra_note": "Note (optional)",
        "add_deposit": "Add to Target",
        "deposit_done": "Added {v} to target.",
        "breakdown_auto": "Auto Saved",
        "breakdown_extra": "Extra Deposits",
        "breakdown_total": "Total Saved",
        "target_pace": "Target Pace",
        "monthly_goal_label": "Monthly Goal",
        "month_auto": "Auto saved this month",
        "month_extra": "Extra deposits this month",
        "month_total": "Total this month",
        "pace_ratio_label": "Pace ratio",
        "pace_tip": "Slow down spending to stay on track for \"{n}\".",
        "history": "History",
        "no_tx": "No transactions yet.",
        "entered": "Entered",
        "burn_on": "On track",
        "burn_fast": "Spending a bit fast",
        "burn_early": "At this pace you may run out early",
        "burn_over": "Over budget — hold steady",
        "chill": "🟢 Chill",
        "careful": "🟡 Careful",
        "danger": "🔴 Danger",
        "panic": "🚨 Panic Mode",
        "ahead": "🟢 Ahead of pace",
        "on_track": "🟡 On track",
        "behind": "🔴 Behind pace",
        "week_col": "Week",
        "budget_col": "Budget",
        "spent_col": "Spent",
        "saved_col": "Saved",
        "manage_cats": "Manage Categories",
        "add_category": "Add new category",
        "add": "Add",
        "cat_added": "Category \"{c}\" added.",
        "cat_deleted": "Category \"{c}\" deleted.",
        "cat_exists": "This category already exists.",
        "cat_empty": "Enter a category name.",
        "pace_saved": "Monthly goal updated.",
        "tx_deleted": "Transaction deleted, balance restored.",
        "tx_updated": "Transaction updated.",
        "edit_amount": "Amount",
        "edit_cat": "Category",
        "edit_note": "Note",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "zh")
    return LANG.get(lang, LANG["zh"]).get(key, key)


# ── Inline edit helpers ───────────────────────────────────────────────────

def _editing(key: str) -> bool:
    return st.session_state.get(f"_edit_{key}", False)


def _toggle(key: str) -> None:
    st.session_state[f"_edit_{key}"] = not st.session_state.get(f"_edit_{key}", False)


# ── Helpers ───────────────────────────────────────────────────────────────

def current_week_id(today: date | None = None) -> str:
    d = today or date.today()
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def current_month_key(today: date | None = None) -> str:
    d = today or date.today()
    return f"{d.year}-{d.month:02d}"


def fmt(v: float) -> str:
    return f"${v:,.2f}"


def days_left_in_week(today: date | None = None) -> int:
    d = today or date.today()
    return max(1, 7 - d.weekday())


# ── Data model ────────────────────────────────────────────────────────────

def _default_target() -> dict[str, Any]:
    return {"name": "MacBook Pro", "total": 3600.0,
            "auto_saved": 0.0, "extra_total": 0.0, "monthly_goal": 300.0}


def _default_data() -> dict[str, Any]:
    return {
        "lang": "zh",
        "weekly_allowance": DEFAULT_ALLOWANCE,
        "current_week_id": current_week_id(),
        "remaining_balance": DEFAULT_ALLOWANCE,
        "transactions": [],
        "categories": list(DEFAULT_CATS_ZH),
        "target": _default_target(),
        "extra_deposits": [],
        "weekly_savings_log": [],
        "monthly_auto_saved": {},
        "monthly_extra_deposits": {},
    }


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    base = _default_data()
    base.update(raw or {})
    base["lang"] = str(base.get("lang", "zh"))
    base["weekly_allowance"] = float(base.get("weekly_allowance", DEFAULT_ALLOWANCE))
    base["remaining_balance"] = float(base.get("remaining_balance", base["weekly_allowance"]))
    base["transactions"] = list(base.get("transactions", []))

    if "categories" not in raw or not raw["categories"]:
        base["categories"] = list(
            DEFAULT_CATS_ZH if base["lang"] == "zh" else DEFAULT_CATS_EN)
    else:
        base["categories"] = list(base["categories"])

    tgt = base.get("target") or {}
    dt = _default_target()
    dt.update(tgt)
    dt["total"] = float(dt.get("total", 3600))
    dt["auto_saved"] = float(dt.get("auto_saved", dt.get("saved", 0)))
    dt["extra_total"] = float(dt.get("extra_total", 0))
    dt["monthly_goal"] = float(dt.get("monthly_goal", 300))
    dt["name"] = str(dt.get("name", "My Goal")).strip() or "My Goal"
    base["target"] = dt

    base["extra_deposits"] = list(base.get("extra_deposits", []))
    base["weekly_savings_log"] = list(base.get("weekly_savings_log", []))
    base["monthly_auto_saved"] = dict(
        base.get("monthly_auto_saved", base.get("monthly_saved", {})))
    base["monthly_extra_deposits"] = dict(base.get("monthly_extra_deposits", {}))
    return base


def load_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        d = _default_data()
        save_data(d)
        return d
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError):
        d = _default_data()
        save_data(d)
        return d
    return _normalize(d)


def save_data(d: dict[str, Any]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def sum_charged(txs: list[dict]) -> float:
    return round(sum(float(x.get("amount_charged", 0)) for x in txs), 2)


def _credit_week(data: dict, week_id: str, txs: list[dict], allow: float) -> float:
    spent = sum_charged(txs)
    saved = max(round(allow - spent, 2), 0.0)
    data["target"]["auto_saved"] = round(data["target"]["auto_saved"] + saved, 2)
    mk = current_month_key()
    data["monthly_auto_saved"][mk] = round(
        float(data["monthly_auto_saved"].get(mk, 0)) + saved, 2)
    log = data["weekly_savings_log"]
    log.append({"week_id": week_id, "budget": round(allow, 2),
                "spent": spent, "saved": saved,
                "closed_at": datetime.now().isoformat(timespec="seconds")})
    data["weekly_savings_log"] = log[-24:]
    return saved


def start_new_week(data: dict, new_wk: str) -> None:
    old_id = data.get("current_week_id", current_week_id())
    old_tx = list(data.get("transactions", []))
    allow = float(data.get("weekly_allowance", DEFAULT_ALLOWANCE))
    rem = float(data.get("remaining_balance", allow))
    if old_id != new_wk:
        _credit_week(data, old_id, old_tx, allow)
    elif old_tx or abs(rem - allow) > 0.02:
        _credit_week(data, old_id, old_tx, allow)
    data["current_week_id"] = new_wk
    data["remaining_balance"] = round(allow, 2)
    data["transactions"] = []


def ensure_week_current(data: dict) -> bool:
    wk = current_week_id()
    if data.get("current_week_id") != wk:
        start_new_week(data, wk)
        save_data(data)
        return True
    return False


def status_state(rem: float, allow: float) -> tuple[str, str]:
    if rem < 0:
        return t("panic"), "panic"
    if allow <= 0:
        return t("danger"), "danger"
    r = rem / allow
    if r > 0.6:
        return t("chill"), "chill"
    if r >= 0.3:
        return t("careful"), "careful"
    return t("danger"), "danger"


def progress_style(rem: float, allow: float) -> tuple[float, str]:
    if allow <= 0:
        return 0.0, "#bb5d4a"
    pct = max(0.0, min(100.0, rem / allow * 100))
    if pct > 50:
        return pct, "#4f8a5f"
    if pct >= 20:
        return pct, "#c89d4f"
    return pct, "#bb5d4a"


def burn_msg(rem: float, allow: float, dl: int) -> str:
    if rem < 0:
        return t("burn_over")
    ideal = (allow / 7.0) * dl
    if rem >= ideal * 1.05:
        return t("burn_on")
    if rem >= ideal * 0.8:
        return t("burn_fast")
    return t("burn_early")


def tx_category(tx: dict) -> str:
    """Get display name from transaction (supports legacy category_key and new category field)."""
    if "category" in tx:
        return tx["category"]
    return tx.get("category_key", "Other")


def cat_summary(txs: list[dict]) -> tuple[dict[str, float], float]:
    s: dict[str, float] = {}
    tot = 0.0
    for tx in txs:
        ch = float(tx.get("amount_charged", 0))
        cat = tx_category(tx)
        s[cat] = s.get(cat, 0) + ch
        tot += ch
    return {k: v for k, v in s.items() if v > 0}, tot


def pace_status(ratio: float) -> tuple[str, str]:
    if ratio > 1.1:
        return t("ahead"), "pace-ahead"
    if ratio >= 0.8:
        return t("on_track"), "pace-ok"
    return t("behind"), "pace-behind"


# ── CSS — Japanese wood-tone + inline edit styling ────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
:root{
  --bg:#eee1ce;--card:#fffdfa;--card-soft:#f8f1e6;--text:#2f2922;
  --muted:#7e7264;--border:rgba(73,58,39,.12);
  --green:#4f8a5f;--yellow:#c89d4f;--red:#bb5d4a;--accent:#9c7651;
}
html,body,[data-testid="stAppViewContainer"],.stApp,.main{
  background:var(--bg)!important;color:var(--text);
  font-family:'DM Sans','Noto Sans JP',system-ui,sans-serif;
}
.stApp{background:radial-gradient(1100px 450px at 95% -10%,#d7be9f 0%,var(--bg) 58%)!important}
header[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbar"],#MainMenu,footer{visibility:hidden;height:0;position:fixed}
.block-container{padding-top:.5rem;padding-bottom:calc(2rem + env(safe-area-inset-bottom));max-width:520px}

.pulse-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:.15rem}
.pulse-brand{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);font-weight:600}
.lang-pill{
  font-size:.7rem;padding:.22rem .55rem;border-radius:999px;
  border:1px solid rgba(73,58,39,.18);background:rgba(255,253,250,.7);
  color:var(--muted);cursor:pointer;font-weight:600;text-decoration:none;
  display:inline-flex;align-items:center;gap:.25rem;
}

.card{
  background:linear-gradient(180deg,#fffefc,var(--card));
  border:1px solid var(--border);border-radius:20px;padding:1rem 1.05rem;
  box-shadow:0 10px 24px rgba(93,74,51,.10);margin-bottom:.75rem;
}
.hero-card{
  padding:1.2rem 1.1rem;border-radius:24px;
  background:linear-gradient(145deg,#fffaf3,#fffdf9);
  border:1px solid rgba(111,84,54,.16);
}
.hero-label{color:#75695d;font-size:.95rem;font-weight:500}
.hero-amount{
  font-size:clamp(2rem,7.8vw,3.25rem);line-height:1.1;font-weight:750;
  margin:.3rem 0 .45rem;letter-spacing:-.02em;color:var(--text);
}
.state-pill{
  display:inline-flex;align-items:center;border-radius:999px;
  padding:.35rem .72rem;font-size:.82rem;font-weight:600;border:1px solid transparent;
}
.chill{background:rgba(79,138,95,.12);color:#3f7650;border-color:rgba(79,138,95,.28)}
.careful{background:rgba(200,157,79,.14);color:#8f6b2f;border-color:rgba(200,157,79,.30)}
.danger,.panic{background:rgba(187,93,74,.14);color:#8a4337;border-color:rgba(187,93,74,.30)}

.metric-label{color:var(--muted);font-size:.86rem;margin-bottom:.2rem;font-weight:500}
.metric-value{font-size:1.55rem;font-weight:700;letter-spacing:-.02em;color:var(--text)}
.metric-sub{color:#6f655a;font-size:.82rem;margin-top:.12rem;line-height:1.35}
.section-title{
  font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;
  color:#8a7e72;font-weight:600;margin:1rem 0 .45rem .15rem;
}
.section-head{display:flex;justify-content:space-between;align-items:center;margin:1rem 0 .45rem .15rem}
.section-head-label{font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:#8a7e72;font-weight:600}

.progress-track{width:100%;height:12px;border-radius:999px;background:rgba(90,70,48,.12);overflow:hidden;margin:.4rem 0 .15rem}
.progress-fill{height:100%;border-radius:999px;transition:width .35s ease}

.bar-row{margin:.42rem 0 .65rem}
.bar-head{display:flex;justify-content:space-between;gap:.6rem;font-size:.86rem;margin-bottom:.25rem;color:#5f5448}
.mini-track{width:100%;height:8px;border-radius:999px;background:rgba(90,70,48,.12);overflow:hidden}
.mini-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#b78b5a,#8f6b44)}

.tx-item{background:var(--card-soft);border:1px solid var(--border);border-radius:14px;padding:.72rem .82rem;margin-bottom:.42rem}
.tx-top{display:flex;justify-content:space-between;gap:.8rem;align-items:center}
.tx-cat{font-weight:620;font-size:.91rem}
.tx-charge{font-size:.95rem;font-weight:700;color:var(--text)}
.tx-meta{color:var(--muted);font-size:.77rem;margin-top:.15rem}
.tx-note{color:#61574c;font-size:.81rem;margin-top:.2rem}

div[data-testid="stForm"]{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:.95rem .95rem .35rem;margin-bottom:.65rem}
.stButton>button,.stFormSubmitButton>button{
  border-radius:12px!important;border:1px solid rgba(90,70,48,.2)!important;
  background:#fffaf3!important;color:#3f342a!important;
  min-height:2.75rem;font-weight:620;font-size:.95rem;
}
.stButton>button:hover{background:#f5ece0!important;border-color:rgba(156,118,81,.4)!important}

div[data-baseweb="input"] input,div[data-baseweb="textarea"] textarea{
  background:#fffefb!important;color:var(--text)!important;
  border-radius:12px!important;border:1px solid var(--border)!important;
  min-height:2.7rem;font-size:1rem;
}
div[data-baseweb="select"]>div{
  background:#fffefb!important;border-radius:12px!important;
  min-height:2.7rem;border:1px solid var(--border)!important;
}
div[data-testid="stNotification"],.stAlert{
  background:#fffbf5!important;border:1px solid rgba(90,70,48,.15)!important;
  border-radius:14px!important;color:var(--text)!important;
}
.streamlit-expanderHeader{font-weight:600!important;color:#4a3f34!important}
[data-testid="stMarkdownContainer"] table{width:100%;border-collapse:collapse;font-size:.82rem}
[data-testid="stMarkdownContainer"] th,[data-testid="stMarkdownContainer"] td{border-bottom:1px solid var(--border);padding:.45rem .35rem;text-align:left}
[data-testid="stMarkdownContainer"] th{color:var(--muted);font-weight:600}

.pace-ahead{color:#3f7650}.pace-ok{color:#8f6b2f}.pace-behind{color:#8a4337}
.cat-row{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0;border-bottom:1px solid var(--border)}
.cat-name{font-size:.9rem;color:var(--text)}

@media(max-width:640px){
  .block-container{padding-left:.7rem;padding-right:.7rem}
  .hero-card{border-radius:20px}.card{border-radius:16px}
  .hero-amount{font-size:2.35rem}
}
</style>
""", unsafe_allow_html=True)

# ── Load data & init ──────────────────────────────────────────────────────

data = load_data()

if "lang" not in st.session_state:
    st.session_state["lang"] = data.get("lang", "zh")

# ── Top bar: brand + language pill ────────────────────────────────────────

_top_l, _top_r = st.columns([6, 1])
with _top_l:
    st.markdown('<div class="pulse-brand">Pulse</div>', unsafe_allow_html=True)
with _top_r:
    cur_lang = st.session_state["lang"]
    pill = "EN" if cur_lang == "zh" else "中文"
    if st.button(pill, key="_lang", use_container_width=True):
        nl = "en" if cur_lang == "zh" else "zh"
        st.session_state["lang"] = nl
        data["lang"] = nl
        save_data(data)
        st.rerun()

if ensure_week_current(data):
    st.session_state["flash_info"] = t("auto_week")

data["weekly_allowance"] = float(data.get("weekly_allowance", DEFAULT_ALLOWANCE))
data["remaining_balance"] = float(data.get("remaining_balance", data["weekly_allowance"]))

if "flash_info" in st.session_state:
    st.info(st.session_state.pop("flash_info"))
if "flash_success" in st.session_state:
    st.success(st.session_state.pop("flash_success"))

# ── Computed ──────────────────────────────────────────────────────────────

allow = data["weekly_allowance"]
rem = data["remaining_balance"]
spent_wk = sum_charged(data["transactions"])
dl = days_left_in_week()
safe = rem / dl
st_label, st_class = status_state(rem, allow)
burn = burn_msg(rem, allow, dl)
prog_pct, prog_color = progress_style(rem, allow)

tgt = data["target"]
tgt_total = float(tgt["total"])
tgt_auto = float(tgt["auto_saved"])
tgt_extra = float(tgt["extra_total"])
tgt_saved = round(tgt_auto + tgt_extra, 2)
tgt_pct = max(0.0, min(100.0, (tgt_saved / tgt_total * 100) if tgt_total > 0 else 0))
m_goal = float(tgt["monthly_goal"])

mk = current_month_key()
m_auto = float(data["monthly_auto_saved"].get(mk, 0))
m_extra = float(data["monthly_extra_deposits"].get(mk, 0))
m_total = round(m_auto + m_extra, 2)
pace_r = m_total / m_goal if m_goal > 0 else 0
pace_lbl, pace_cls = pace_status(pace_r)

proj_save = max(round(allow - spent_wk, 2), 0.0)
last_wk_save = 0.0
if data["weekly_savings_log"]:
    last_wk_save = float(data["weekly_savings_log"][-1].get("saved", 0))

cats = data.get("categories", list(DEFAULT_CATS_ZH))

# ══════════════════════════════════════════════════════════════════════════
# HERO — with inline allowance editing
# ══════════════════════════════════════════════════════════════════════════

if _editing("allowance"):
    st.markdown(f"""
    <div class="card hero-card">
      <div class="hero-label">{t("weekly_allowance")}</div>
    </div>""", unsafe_allow_html=True)
    new_a = st.number_input(t("weekly_allowance"), min_value=1.0,
                            value=float(data["weekly_allowance"]),
                            step=5.0, format="%.2f",
                            key="edit_allow_val", label_visibility="collapsed")
    sa, sc = st.columns(2, gap="small")
    with sa:
        if st.button(t("save"), key="save_allow", use_container_width=True):
            old_a = float(data["weekly_allowance"])
            spent_so = round(old_a - float(data["remaining_balance"]), 2)
            data["weekly_allowance"] = round(float(new_a), 2)
            data["remaining_balance"] = round(data["weekly_allowance"] - spent_so, 2)
            save_data(data)
            _toggle("allowance")
            st.session_state["flash_success"] = t("allowance_saved").format(
                v=fmt(data["weekly_allowance"]))
            st.rerun()
    with sc:
        if st.button(t("cancel"), key="cancel_allow", use_container_width=True):
            _toggle("allowance")
            st.rerun()
else:
    _hero_l, _hero_r = st.columns([20, 1])
    with _hero_l:
        st.markdown(f"""
        <div class="card hero-card">
          <div class="hero-label">{t("remaining_week")}</div>
          <div class="hero-amount">{fmt(rem)}</div>
          <span class="state-pill {st_class}">{st_label}</span>
          <div class="metric-sub" style="margin-top:.5rem">{t("weekly_allowance")}: {fmt(allow)}</div>
        </div>""", unsafe_allow_html=True)
    with _hero_r:
        if st.button("✏️", key="edit_allow_btn", use_container_width=True):
            _toggle("allowance")
            st.rerun()

cA, cB = st.columns(2, gap="small")
with cA:
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">{t("safe_today")}</div>
      <div class="metric-value">{fmt(safe)}</div>
      <div class="metric-sub">{dl} {t("days_left")} · {t("remaining_div_days")}</div>
    </div>""", unsafe_allow_html=True)
with cB:
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">{t("burn_rate")}</div>
      <div class="metric-value" style="font-size:1.05rem;line-height:1.25">{burn}</div>
      <div class="metric-sub">{t("burn_vs_ideal")}</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="card">
  <div class="metric-label">{t("budget_progress")}</div>
  <div class="progress-track"><div class="progress-fill" style="width:{prog_pct:.1f}%;background:{prog_color}"></div></div>
  <div class="metric-sub">{prog_pct:.0f}% {t("pct_left")}</div>
</div>""", unsafe_allow_html=True)

if rem < 0:
    st.error(f"{t('panic_over')} {fmt(abs(rem))}")

# ══════════════════════════════════════════════════════════════════════════
# Log Expense + Category Manager
# ══════════════════════════════════════════════════════════════════════════

_log_l, _log_r = st.columns([20, 1])
with _log_l:
    st.markdown(f'<div id="log" class="section-title">{t("log_expense")}</div>',
                unsafe_allow_html=True)
with _log_r:
    if st.button("⚙️", key="manage_cats_btn", use_container_width=True):
        _toggle("cats")
        st.rerun()

if _editing("cats"):
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">{t("manage_cats")}</div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    for i, c in enumerate(cats):
        cl, cr = st.columns([6, 1])
        with cl:
            st.markdown(f'<div style="padding:.35rem 0;font-size:.9rem">{c}</div>',
                        unsafe_allow_html=True)
        with cr:
            if st.button("✕", key=f"del_cat_{i}", use_container_width=True):
                removed = cats.pop(i)
                data["categories"] = cats
                save_data(data)
                st.session_state["flash_info"] = t("cat_deleted").format(c=removed)
                st.rerun()

    nc_l, nc_r = st.columns([4, 1])
    with nc_l:
        new_cat = st.text_input(t("add_category"), key="new_cat_input",
                                label_visibility="collapsed",
                                placeholder=t("add_category"))
    with nc_r:
        if st.button(t("add"), key="add_cat_btn", use_container_width=True):
            nc = new_cat.strip()
            if not nc:
                st.warning(t("cat_empty"))
            elif nc in cats:
                st.warning(t("cat_exists"))
            else:
                cats.append(nc)
                data["categories"] = cats
                save_data(data)
                st.session_state["flash_success"] = t("cat_added").format(c=nc)
                st.rerun()

    if st.button(t("done"), key="done_cats", use_container_width=True):
        _toggle("cats")
        st.rerun()
else:
    with st.form("expense_form", clear_on_submit=True):
        amt = st.number_input(t("amount"), min_value=0.0, step=1.0, format="%.2f")
        cat_label = st.selectbox(t("category"), cats)
        note = st.text_input(t("note"))
        amor = st.checkbox(t("amortize"))
        submitted = st.form_submit_button(t("add_btn"), use_container_width=True)

    if submitted:
        if amt <= 0:
            st.warning(t("enter_positive"))
        else:
            charged = round(amt * 0.5, 2) if amor else round(amt, 2)
            tx = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "amount_entered": round(float(amt), 2),
                "amount_charged": charged,
                "category": cat_label,
                "note": note.strip(),
                "amortized": bool(amor),
            }
            data["transactions"].append(tx)
            data["remaining_balance"] = round(data["remaining_balance"] - charged, 2)
            save_data(data)
            if amor:
                st.session_state["flash_success"] = t("amortize_msg")
            else:
                st.session_state["flash_success"] = t("logged").format(
                    v=fmt(charged), c=cat_label)
            st.rerun()

    u1, u2 = st.columns(2, gap="small")
    with u1:
        if st.button(t("undo"), use_container_width=True):
            if data["transactions"]:
                ltx = data["transactions"].pop()
                data["remaining_balance"] = round(
                    data["remaining_balance"] + float(ltx["amount_charged"]), 2)
                save_data(data)
                st.session_state["flash_info"] = t("undo_done")
                st.rerun()
            else:
                st.warning(t("no_undo"))
    with u2:
        if st.button(t("new_week"), use_container_width=True):
            start_new_week(data, current_week_id())
            save_data(data)
            st.session_state["flash_info"] = t("new_week_done")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# Category Insights
# ══════════════════════════════════════════════════════════════════════════

summary, total_spent = cat_summary(data["transactions"])
st.markdown(f'<div class="section-title">{t("category_insights")}</div>',
            unsafe_allow_html=True)

if total_spent <= 0:
    st.markdown(
        f'<div class="card"><div class="metric-sub">{t("no_spending")}</div></div>',
        unsafe_allow_html=True)
else:
    sorted_cats = sorted(summary.items(), key=lambda x: x[1], reverse=True)
    chart_rows = [{"category": c, "spent": v, "pct": (v / total_spent) * 100}
                  for c, v in sorted_cats]

    palette = ["#b1885b", "#c5a171", "#9d7e59", "#d1b28a",
               "#a58b69", "#b79b79", "#8f7355", "#c8b18f"]

    donut = (
        alt.Chart(alt.Data(values=chart_rows))
        .mark_arc(innerRadius=58, outerRadius=92, cornerRadius=4)
        .encode(
            theta=alt.Theta("spent:Q", stack=True),
            color=alt.Color("category:N",
                            scale=alt.Scale(range=palette),
                            legend=alt.Legend(orient="bottom", columns=2,
                                             labelColor="#5f5347",
                                             symbolType="circle", title=None)),
            tooltip=[alt.Tooltip("category:N", title=t("category")),
                     alt.Tooltip("spent:Q", title="$", format=",.2f"),
                     alt.Tooltip("pct:Q", title="%", format=".1f")],
        )
        .properties(height=250)
        .configure_view(strokeWidth=0)
        .configure(background="transparent")
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.altair_chart(donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    for c, v in sorted_cats:
        pct = (v / total_spent) * 100
        st.markdown(f"""
        <div class="bar-row">
          <div class="bar-head"><span>{c}</span><span>{fmt(v)} · {pct:.0f}%</span></div>
          <div class="mini-track"><div class="mini-fill" style="width:{min(100,pct):.1f}%"></div></div>
        </div>""", unsafe_allow_html=True)

    top_c, top_v = sorted_cats[0]
    top_p = int((top_v / total_spent) * 100)
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">{t("insight")}</div>
      <div class="metric-value" style="font-size:1.1rem">{t("top_spend").format(c=top_c, p=top_p)}</div>
      <div class="metric-sub">{t("top_spend_sub").format(c=top_c)}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# Target — inline editing
# ══════════════════════════════════════════════════════════════════════════

if _editing("target"):
    st.markdown(f'<div class="section-title">{t("target_section")}</div>',
                unsafe_allow_html=True)
    tn = st.text_input(t("target_name"), value=str(tgt["name"]), key="ed_tgt_n")
    tc1, tc2 = st.columns(2)
    with tc1:
        tt = st.number_input(t("target_total"), min_value=1.0,
                             value=float(tgt["total"]), step=50.0, key="ed_tgt_t")
    with tc2:
        tm = st.number_input(t("monthly_goal"), min_value=0.0,
                             value=float(tgt["monthly_goal"]), step=25.0, key="ed_tgt_m")
    sa, sc = st.columns(2, gap="small")
    with sa:
        if st.button(t("save"), key="save_tgt", use_container_width=True):
            data["target"]["name"] = tn.strip() or "My Goal"
            data["target"]["total"] = round(float(tt), 2)
            data["target"]["monthly_goal"] = round(float(tm), 2)
            save_data(data)
            _toggle("target")
            st.session_state["flash_success"] = t("target_saved_msg")
            st.rerun()
    with sc:
        if st.button(t("cancel"), key="cancel_tgt", use_container_width=True):
            _toggle("target")
            st.rerun()
else:
    _tgt_l, _tgt_r = st.columns([20, 1])
    with _tgt_l:
        st.markdown(f'<div class="section-title">{t("target_section")}</div>',
                    unsafe_allow_html=True)
    with _tgt_r:
        if st.button("✏️", key="edit_tgt_btn", use_container_width=True):
            _toggle("target")
            st.rerun()

    st.markdown(f"""
    <div class="card">
      <div class="metric-label">🎯 {tgt["name"]}</div>
      <div class="metric-value" style="font-size:1.65rem">{fmt(tgt_saved)} / {fmt(tgt_total)}</div>
      <div class="metric-sub">{tgt_pct:.1f}% {t("completed")}</div>
      <div class="progress-track" style="margin-top:.55rem">
        <div class="progress-fill" style="width:{tgt_pct:.1f}%;background:linear-gradient(90deg,#b78b5a,#8f6b44)"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
      <div class="metric-sub" style="margin-bottom:.35rem">{t("breakdown_auto")}: <strong>{fmt(tgt_auto)}</strong></div>
      <div class="metric-sub">{t("breakdown_extra")}: <strong>{fmt(tgt_extra)}</strong></div>
      <div class="metric-sub" style="margin-top:.35rem;font-size:.88rem"><strong>{t("breakdown_total")}: {fmt(tgt_saved)}</strong></div>
    </div>""", unsafe_allow_html=True)

# Weekly contribution
cw1, cw2 = st.columns(2)
with cw1:
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">{t("projected_save")}</div>
      <div class="metric-value" style="font-size:1.2rem">{fmt(proj_save)}</div>
      <div class="metric-sub">{t("formula_save")}</div>
    </div>""", unsafe_allow_html=True)
with cw2:
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">{t("last_week_credit")}</div>
      <div class="metric-value" style="font-size:1.2rem">{fmt(last_wk_save)}</div>
      <div class="metric-sub">{t("auto_credit")}</div>
    </div>""", unsafe_allow_html=True)

rows_md = []
for row in data.get("weekly_savings_log", [])[-6:]:
    rows_md.append(
        f"| {row.get('week_id','')} | {fmt(float(row.get('budget',0)))} | "
        f"{fmt(float(row.get('spent',0)))} | {fmt(float(row.get('saved',0)))} |")
if rows_md:
    st.markdown(
        f"| {t('week_col')} | {t('budget_col')} | {t('spent_col')} | {t('saved_col')} |\n"
        "| --- | --- | --- | --- |\n" + "\n".join(rows_md))

# ══════════════════════════════════════════════════════════════════════════
# Extra Deposit
# ══════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="section-title">{t("extra_deposit")}</div>',
            unsafe_allow_html=True)
st.markdown(
    f'<div class="metric-sub" style="margin-bottom:.5rem">{t("extra_deposit_desc")}</div>',
    unsafe_allow_html=True)

with st.form("deposit_form", clear_on_submit=True):
    dep_amt = st.number_input(t("amount"), min_value=0.0, step=10.0,
                              format="%.2f", key="dep_amt")
    dep_note = st.text_input(t("extra_note"), key="dep_note")
    dep_sub = st.form_submit_button(t("add_deposit"), use_container_width=True)

if dep_sub:
    if dep_amt <= 0:
        st.warning(t("enter_positive"))
    else:
        dep_val = round(float(dep_amt), 2)
        data["target"]["extra_total"] = round(tgt_extra + dep_val, 2)
        data["extra_deposits"].append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "amount": dep_val, "note": dep_note.strip(),
        })
        data["extra_deposits"] = data["extra_deposits"][-50:]
        data["monthly_extra_deposits"][mk] = round(m_extra + dep_val, 2)
        save_data(data)
        st.session_state["flash_success"] = t("deposit_done").format(v=fmt(dep_val))
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# Target Pace — inline monthly goal editing
# ══════════════════════════════════════════════════════════════════════════

if _editing("pace"):
    st.markdown(f'<div class="section-title">{t("target_pace")}</div>',
                unsafe_allow_html=True)
    new_mg = st.number_input(t("monthly_goal"), min_value=0.0,
                             value=float(tgt["monthly_goal"]),
                             step=25.0, key="ed_pace_mg")
    sa, sc = st.columns(2, gap="small")
    with sa:
        if st.button(t("save"), key="save_pace", use_container_width=True):
            data["target"]["monthly_goal"] = round(float(new_mg), 2)
            save_data(data)
            _toggle("pace")
            st.session_state["flash_success"] = t("pace_saved")
            st.rerun()
    with sc:
        if st.button(t("cancel"), key="cancel_pace", use_container_width=True):
            _toggle("pace")
            st.rerun()
else:
    _pc_l, _pc_r = st.columns([20, 1])
    with _pc_l:
        st.markdown(f'<div class="section-title">{t("target_pace")}</div>',
                    unsafe_allow_html=True)
    with _pc_r:
        if st.button("✏️", key="edit_pace_btn", use_container_width=True):
            _toggle("pace")
            st.rerun()

    st.markdown(f"""
    <div class="card">
      <div class="metric-label">{t("monthly_goal_label")}</div>
      <div class="metric-value">{fmt(m_goal)}</div>
      <div class="metric-sub" style="margin-top:.6rem">{t("month_auto")}: <strong>{fmt(m_auto)}</strong></div>
      <div class="metric-sub">{t("month_extra")}: <strong>{fmt(m_extra)}</strong></div>
      <div class="metric-sub">{t("month_total")}: <strong>{fmt(m_total)}</strong></div>
      <div class="metric-sub" style="margin-top:.3rem">{t("pace_ratio_label")}: <strong>{pace_r:.2f}</strong></div>
      <div class="metric-sub"><span class="{pace_cls}"><strong>{pace_lbl}</strong></span></div>
      <div class="metric-sub" style="margin-top:.45rem">{t("pace_tip").format(n=tgt["name"])}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# History — with per-item edit & delete
# ══════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="section-title">{t("history")}</div>',
            unsafe_allow_html=True)

tx_list = data["transactions"]
num_tx = len(tx_list)
show_indices = list(range(max(0, num_tx - 5), num_tx))[::-1]

if not show_indices:
    st.markdown(
        f'<div class="card"><div class="metric-sub">{t("no_tx")}</div></div>',
        unsafe_allow_html=True)
else:
    for idx in show_indices:
        tx = tx_list[idx]
        edit_key = f"_edit_tx_{idx}"

        if st.session_state.get(edit_key, False):
            # ── inline edit mode ──
            st.markdown(f'<div class="card" style="padding:.85rem .9rem">',
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            e_amt = st.number_input(
                t("edit_amount"), min_value=0.01,
                value=float(tx.get("amount_entered", 0)),
                step=1.0, format="%.2f", key=f"eamt_{idx}")
            e_cat = st.selectbox(
                t("edit_cat"), cats,
                index=cats.index(tx_category(tx)) if tx_category(tx) in cats else 0,
                key=f"ecat_{idx}")
            e_note = st.text_input(
                t("edit_note"),
                value=tx.get("note", ""), key=f"enote_{idx}")
            e_amor = st.checkbox(
                t("amortize"),
                value=bool(tx.get("amortized", False)), key=f"eamor_{idx}")

            s_col, c_col = st.columns(2, gap="small")
            with s_col:
                if st.button(t("save"), key=f"save_tx_{idx}",
                             use_container_width=True):
                    old_charged = float(tx.get("amount_charged", 0))
                    new_charged = round(float(e_amt) * 0.5, 2) if e_amor \
                        else round(float(e_amt), 2)

                    data["remaining_balance"] = round(
                        data["remaining_balance"] + old_charged - new_charged, 2)

                    tx["amount_entered"] = round(float(e_amt), 2)
                    tx["amount_charged"] = new_charged
                    tx["category"] = e_cat
                    tx.pop("category_key", None)
                    tx["note"] = e_note.strip()
                    tx["amortized"] = bool(e_amor)

                    save_data(data)
                    st.session_state[edit_key] = False
                    st.session_state["flash_success"] = t("tx_updated")
                    st.rerun()
            with c_col:
                if st.button(t("cancel"), key=f"cancel_tx_{idx}",
                             use_container_width=True):
                    st.session_state[edit_key] = False
                    st.rerun()
        else:
            # ── display mode ──
            ts = tx.get("timestamp", "").replace("T", " ")
            cat = tx_category(tx)
            amr = "Amortized" if tx.get("amortized") else "Standard"
            n = tx.get("note", "").strip()
            n_html = f'<div class="tx-note">{n}</div>' if n else ""
            st.markdown(f"""
            <div class="tx-item">
              <div class="tx-top">
                <div class="tx-cat">{cat}</div>
                <div class="tx-charge">{fmt(float(tx.get("amount_charged",0)))}</div>
              </div>
              <div class="tx-meta">{ts} · {t("entered")} {fmt(float(tx.get("amount_entered",0)))} · {amr}</div>
              {n_html}
            </div>""", unsafe_allow_html=True)

            act_l, act_r, act_pad = st.columns([1, 1, 4])
            with act_l:
                if st.button("✏️", key=f"editbtn_{idx}",
                             use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
            with act_r:
                if st.button("✕", key=f"delbtn_{idx}",
                             use_container_width=True):
                    removed = tx_list.pop(idx)
                    data["remaining_balance"] = round(
                        data["remaining_balance"]
                        + float(removed.get("amount_charged", 0)), 2)
                    save_data(data)
                    st.session_state["flash_info"] = t("tx_deleted")
                    st.rerun()
