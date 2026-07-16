"""
SamaAudit — AI Lending Decision Audit Trail
Streamlit Web Interface with Arabic UI

Run: streamlit run app/main.py
"""

import json
import streamlit as st
from pathlib import Path

# ── Local imports ──
import sys
sys.path.insert(0, str(Path(__file__).parent))

from agent import evaluate_application, load_scenarios
from regulatory import generate_compliance_report
from report import generate_pdf

# ════════════════════════════════════════════════════════
# Page Config
# ════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SamaAudit | نظام تدقيق قرارات الإقراض",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════
# Custom CSS — All colors are hardcoded hex, no variables
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Force dark background everywhere ── */
    .stApp {
        background-color: #0e1117 !important;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Naskh Arabic', sans-serif !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1100px;
    }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #0a2647 0%, #006B3F 50%, #0a2647 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 107, 63, 0.4);
        box-shadow: 0 8px 40px rgba(0, 107, 63, 0.2);
        position: relative;
        overflow: hidden;
    }

    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0,107,63,0.15) 0%, transparent 70%);
        animation: hero-pulse 4s ease-in-out infinite;
    }

    @keyframes hero-pulse {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.05); }
    }

    .hero-banner .hero-title {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        font-family: 'Noto Naskh Arabic', serif;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }

    .hero-banner .hero-sub {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.95rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
        font-family: 'Noto Naskh Arabic', serif;
    }

    .hero-banner .hero-tag {
        color: rgba(255, 255, 255, 0.55);
        font-size: 0.8rem;
        margin-top: 0.3rem;
        position: relative;
        z-index: 1;
    }

    /* ── Info Cards ── */
    .info-card {
        background: linear-gradient(145deg, #16213e, #1a1a2e);
        border: 1px solid #2d3561;
        border-radius: 14px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .info-card:hover {
        border-color: #006B3F;
        box-shadow: 0 6px 30px rgba(0, 107, 63, 0.2);
        transform: translateY(-2px);
    }

    .info-card .card-title {
        color: #00c853;
        font-family: 'Noto Naskh Arabic', serif;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: right;
        direction: rtl;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(0, 200, 83, 0.15);
    }

    .info-card .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.45rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        direction: rtl;
    }

    .info-card .data-row:last-child {
        border-bottom: none;
    }

    .info-card .data-label {
        color: #8899aa;
        font-size: 0.84rem;
        font-family: 'Noto Naskh Arabic', serif;
    }

    .info-card .data-value {
        color: #ffffff;
        font-weight: 600;
        font-size: 0.84rem;
        font-family: 'Noto Naskh Arabic', serif;
    }

    /* ── Decision Badge ── */
    .decision-container {
        text-align: center;
        margin: 1.5rem 0;
    }

    .decision-badge {
        display: inline-block;
        padding: 0.7rem 3rem;
        border-radius: 50px;
        font-size: 1.4rem;
        font-weight: 700;
        font-family: 'Noto Naskh Arabic', serif;
        color: #ffffff;
        letter-spacing: 1px;
    }

    .decision-approved {
        background: linear-gradient(135deg, #1b8a4a, #27ae60);
        box-shadow: 0 6px 25px rgba(39, 174, 96, 0.5);
        border: 1px solid rgba(39, 174, 96, 0.6);
    }

    .decision-rejected {
        background: linear-gradient(135deg, #a93226, #e74c3c);
        box-shadow: 0 6px 25px rgba(231, 76, 60, 0.5);
        border: 1px solid rgba(231, 76, 60, 0.6);
    }

    /* ── Metrics Row ── */
    .metrics-row {
        display: flex;
        gap: 1rem;
        margin: 1.2rem 0;
        direction: rtl;
    }

    .metric-box {
        flex: 1;
        background: linear-gradient(145deg, #16213e, #1a1a2e);
        border: 1px solid #2d3561;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 3px 15px rgba(0, 0, 0, 0.2);
    }

    .metric-box .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #00c853;
        line-height: 1;
    }

    .metric-box .metric-lbl {
        font-size: 0.78rem;
        color: #8899aa;
        font-family: 'Noto Naskh Arabic', serif;
        margin-top: 0.4rem;
    }

    /* ── Rule Rows ── */
    .rule-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.2rem;
        margin: 0.4rem 0;
        border-radius: 10px;
        direction: rtl;
        transition: all 0.25s ease;
    }

    .rule-item:hover {
        transform: translateX(-4px);
    }

    .rule-pass {
        background: rgba(39, 174, 96, 0.1);
        border-right: 4px solid #27ae60;
        border-left: none;
    }

    .rule-fail {
        background: rgba(231, 76, 60, 0.1);
        border-right: 4px solid #e74c3c;
        border-left: none;
    }

    .rule-item .rule-name {
        font-family: 'Noto Naskh Arabic', serif;
        font-weight: 700;
        color: #e8e8e8;
        font-size: 0.9rem;
    }

    .rule-item .rule-detail {
        font-family: 'Noto Naskh Arabic', serif;
        color: #8899aa;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    .rule-item .rule-id-tag {
        color: #556677;
        font-size: 0.7rem;
        margin-top: 0.15rem;
    }

    .rule-item .rule-icon {
        font-size: 1.3rem;
        min-width: 35px;
        text-align: center;
    }

    /* ── Compliance Entries ── */
    .compliance-card {
        background: linear-gradient(145deg, #16213e, #1a1a2e);
        border: 1px solid #2d3561;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin: 0.5rem 0;
        direction: rtl;
        text-align: right;
        transition: all 0.3s ease;
    }

    .compliance-card:hover {
        border-color: #006B3F;
        box-shadow: 0 4px 20px rgba(0, 107, 63, 0.15);
    }

    .compliance-card .comp-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .compliance-card .comp-principle {
        color: #00c853;
        font-family: 'Noto Naskh Arabic', serif;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .compliance-card .comp-reference {
        color: #667788;
        font-size: 0.72rem;
        font-family: 'Noto Naskh Arabic', serif;
    }

    .compliance-card .comp-statement {
        color: #c8d0d8;
        font-family: 'Noto Naskh Arabic', serif;
        font-size: 0.8rem;
        line-height: 1.7;
        margin-top: 0.4rem;
    }

    .comp-badge {
        font-size: 0.72rem;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-family: 'Noto Naskh Arabic', serif;
        font-weight: 600;
    }

    .comp-badge-pass {
        background: rgba(39, 174, 96, 0.15);
        color: #27ae60;
        border: 1px solid rgba(39, 174, 96, 0.3);
    }

    .comp-badge-fail {
        background: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }

    /* ── Fairness Card ── */
    .fairness-card {
        background: linear-gradient(135deg, rgba(0, 107, 63, 0.12), rgba(0, 107, 63, 0.04));
        border: 1px solid rgba(0, 107, 63, 0.35);
        border-radius: 14px;
        padding: 1.6rem;
        direction: rtl;
        text-align: right;
        margin: 1.2rem 0;
        box-shadow: 0 4px 20px rgba(0, 107, 63, 0.1);
    }

    .fairness-card .fair-title {
        color: #00c853;
        font-family: 'Noto Naskh Arabic', serif;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .fairness-card .fair-text {
        color: #c8d0d8;
        font-family: 'Noto Naskh Arabic', serif;
        font-size: 0.85rem;
        line-height: 1.9;
    }

    .fairness-card .fair-ref {
        font-size: 0.73rem;
        color: #667788;
        margin-top: 0.8rem;
        font-family: 'Noto Naskh Arabic', serif;
    }

    /* ── Section Separator ── */
    .section-sep {
        height: 1px;
        background: linear-gradient(90deg, transparent, #006B3F, transparent);
        margin: 1.5rem 0;
        border: none;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a2647 0%, #0e1117 100%) !important;
        border-right: 1px solid #1a2744 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        font-family: 'Noto Naskh Arabic', serif !important;
        color: #c8d0d8 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        color: #00c853 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        border-radius: 12px !important;
        font-family: 'Noto Naskh Arabic', serif !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        background: linear-gradient(135deg, #006B3F, #00a65a) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 107, 63, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 107, 63, 0.5) !important;
        background: linear-gradient(135deg, #008B4F, #00c853) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    .stDownloadButton > button {
        width: 100%;
        border-radius: 12px !important;
        font-family: 'Noto Naskh Arabic', serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        background: linear-gradient(135deg, #0a2647, #16213e) !important;
        color: #ffffff !important;
        border: 2px solid #006B3F !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #006B3F, #00a65a) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 107, 63, 0.4) !important;
        border-color: #00c853 !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #8899aa !important;
        background: #16213e !important;
        border-radius: 8px !important;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #2d3561; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #006B3F; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# Render Functions
# ════════════════════════════════════════════════════════

def render_hero():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🏦 SamaAudit</div>
        <div class="hero-sub">نظام تدقيق قرارات الإقراض بالذكاء الاصطناعي</div>
        <div class="hero-tag">AI Lending Decision Audit Trail — Regulatory Translation Engine</div>
    </div>
    """, unsafe_allow_html=True)


def render_company_card(s):
    rev = f"{s['annual_revenue_sar']:,.0f}"
    debt = f"{s['existing_debt_sar']:,.0f}"
    loan = f"{s['requested_loan_sar']:,.0f}"
    absher_icon = "✅" if s["absher_verified"] else "❌"
    absher_text = "تم التحقق" if s["absher_verified"] else "لم يتم التحقق"

    st.markdown(f"""
    <div class="info-card">
        <div class="card-title">📋 بيانات الشركة</div>
        <div class="data-row"><span class="data-label">اسم الشركة</span><span class="data-value">{s['company_name']}</span></div>
        <div class="data-row"><span class="data-label">الاسم بالإنجليزية</span><span class="data-value" style="color:#8899aa">{s['company_name_en']}</span></div>
        <div class="data-row"><span class="data-label">رقم السجل التجاري</span><span class="data-value" style="color:#5dade2">{s['cr_number']}</span></div>
        <div class="data-row"><span class="data-label">النشاط التجاري</span><span class="data-value">{s['business_activity_ar']}</span></div>
        <div class="data-row"><span class="data-label">عمر المنشأة</span><span class="data-value">{s['business_age_years']} سنوات</span></div>
        <div class="data-row"><span class="data-label">الإيرادات السنوية</span><span class="data-value" style="color:#00c853">{rev} ريال</span></div>
        <div class="data-row"><span class="data-label">الديون الحالية</span><span class="data-value" style="color:#ff8a65">{debt} ريال</span></div>
        <div class="data-row"><span class="data-label">مبلغ التمويل المطلوب</span><span class="data-value" style="color:#ffd54f">{loan} ريال</span></div>
        <div class="data-row"><span class="data-label">المالك</span><span class="data-value">{s['owner_name']}</span></div>
        <div class="data-row"><span class="data-label">التحقق من الهوية (أبشر)</span><span class="data-value">{absher_icon} {absher_text}</span></div>
    </div>
    """, unsafe_allow_html=True)


def render_decision(r):
    is_approved = r["decision"] == "approved"
    badge_cls = "decision-approved" if is_approved else "decision-rejected"
    icon = "✅" if is_approved else "❌"

    st.markdown(f"""
    <div class="decision-container">
        <div class="decision-badge {badge_cls}">{icon} {r['decision_ar']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    passed_color = "#27ae60"
    failed_color = "#e74c3c" if r["failed_rules"] > 0 else "#27ae60"
    risk_color = "#27ae60" if r["risk_score"] == "low" else ("#ffa726" if r["risk_score"] == "medium" else "#e74c3c")

    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-box">
            <div class="metric-val" style="color:#5dade2">{r['total_rules']}</div>
            <div class="metric-lbl">إجمالي القواعد</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="color:{passed_color}">{r['passed_rules']}</div>
            <div class="metric-lbl">قواعد ناجحة</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="color:{failed_color}">{r['failed_rules']}</div>
            <div class="metric-lbl">قواعد مخالفة</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="color:{risk_color}">{r['risk_score_ar']}</div>
            <div class="metric-lbl">مستوى المخاطر</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_rules(r):
    st.markdown("""
    <div class="info-card">
        <div class="card-title">📊 تفاصيل تقييم القواعد</div>
    </div>
    """, unsafe_allow_html=True)

    for rule in r["rules_evaluated"]:
        cls = "rule-pass" if rule["passed"] else "rule-fail"
        icon = "✅" if rule["passed"] else "❌"

        st.markdown(f"""
        <div class="rule-item {cls}">
            <div>
                <div class="rule-name">{rule['rule_name_ar']}</div>
                <div class="rule-detail">{rule['details_ar']}</div>
                <div class="rule-id-tag">{rule['rule_id']} | {rule['rule_name_en']}</div>
            </div>
            <div class="rule-icon">{icon}</div>
        </div>
        """, unsafe_allow_html=True)


def render_compliance(c):
    st.markdown("""
    <div class="section-sep"></div>
    <div class="info-card">
        <div class="card-title">🗺️ خريطة الالتزام التنظيمي — Regulatory Compliance Map</div>
    </div>
    """, unsafe_allow_html=True)

    for e in c["compliance_entries"]:
        badge_cls = "comp-badge-pass" if e["passed"] else "comp-badge-fail"

        st.markdown(f"""
        <div class="compliance-card">
            <div class="comp-header">
                <span class="comp-principle">{e['sama_principle_name_ar']} ({e['sama_principle_id']})</span>
                <span class="comp-badge {badge_cls}">{e['compliance_status_ar']}</span>
            </div>
            <div class="comp-reference">{e['rule_id']} | {e['regulatory_reference_ar']}</div>
            <div class="comp-statement">{e['audit_statement_ar']}</div>
        </div>
        """, unsafe_allow_html=True)


def render_fairness(c):
    ref = c.get("fairness_principle", {}).get("regulatory_reference_ar", "")

    st.markdown(f"""
    <div class="section-sep"></div>
    <div class="fairness-card">
        <div class="fair-title">⚖️ بيان العدالة — Fairness Statement</div>
        <div class="fair-text">{c['fairness_statement_ar']}</div>
        <div class="fair-ref">المرجع: {ref}</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# Main Application
# ════════════════════════════════════════════════════════

def main():
    render_hero()

    scenarios = load_scenarios()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-family: 'Noto Naskh Arabic', serif; font-size: 1.15rem;
                        color: #00c853; font-weight: 700;">
                📋 لوحة التحكم
            </div>
            <div style="font-size: 0.7rem; color: #556677; margin-top: 0.3rem;">
                Control Panel
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("""
        <div style="font-family: 'Noto Naskh Arabic', serif; text-align: right; direction: rtl;
                    color: #8899aa; font-size: 0.85rem; margin-bottom: 0.5rem;">
            اختر سيناريو للتقييم:
        </div>
        """, unsafe_allow_html=True)

        labels = [s["label"] for s in scenarios]
        selected_label = st.radio(
            "اختيار السيناريو",
            labels,
            index=0,
            label_visibility="collapsed",
        )
        selected = next(s for s in scenarios if s["label"] == selected_label)

        st.markdown("---")

        st.markdown("""
        <div style="text-align: right; direction: rtl; padding: 0.5rem 0.3rem;">
            <div style="font-family: 'Noto Naskh Arabic', serif; font-size: 0.73rem; color: #556677; line-height: 1.8;">
                🔒 يعمل محلياً — بدون اتصال بالإنترنت<br>
                📦 نسخة تجريبية — MVP<br>
                🏛️ مُصمم لمتطلبات البنك المركزي السعودي<br>
                🛡️ بدون إرسال بيانات لأي خادم خارجي
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Company Card ──
    render_company_card(selected)

    # ── Detect scenario change & reset ──
    if st.session_state.get("_prev_id") != selected["id"]:
        st.session_state["_prev_id"] = selected["id"]
        st.session_state["ran"] = False

    # ── Run Agent Button ──
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 تشغيل الوكيل — Run Agent", use_container_width=True):
            st.session_state["ran"] = True

    # ── Results ──
    if st.session_state.get("ran"):
        app_data = {k: v for k, v in selected.items() if k not in ("id", "label", "label_en")}
        agent_result = evaluate_application(app_data)
        compliance_data = generate_compliance_report(agent_result)

        render_decision(agent_result)
        render_rules(agent_result)
        render_compliance(compliance_data)
        render_fairness(compliance_data)

        # ── PDF Download ──
        st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            try:
                pdf_bytes = generate_pdf(compliance_data)
                st.download_button(
                    label="📄 توليد وتحميل تقرير SAMA — Generate PDF Report",
                    data=pdf_bytes,
                    file_name=f"SamaAudit_{agent_result['decision_id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"خطأ في إنشاء التقرير: {e}")
                st.info("تأكد من تثبيت الخطوط العربية في مجلد fonts/  — راجع fonts/README.md")

        # ── JSON for Engineers ──
        with st.expander("🔧 Agent JSON Output (For Engineers)"):
            st.json(agent_result)
        with st.expander("🔧 Compliance Report JSON"):
            st.json(compliance_data)


if __name__ == "__main__":
    main()
