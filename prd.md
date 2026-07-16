# SamaAudit — Stage 2: Product Requirements Document (PRD)

> **Version**: 1.0 | **Date**: July 15, 2026  
> **Author**: Technical Product Manager  
> **Status**: Final — Ready for Engineering

---

## 1. Executive Summary

**SamaAudit** is an MVP tool that provides a regulatory-grade audit trail for AI-powered SME lending decisions in Saudi banks. It bridges the gap between technical AI agent outputs and SAMA regulatory compliance requirements by automatically mapping every agent decision to specific SAMA principles and generating Arabic-language audit reports.

**Core Value Proposition**: Reduce the time to produce a SAMA-compliant audit report from 2-3 days of manual work to under 5 minutes, with a single button click.

**Target Market**: Saudi banks operating in or applying to the SAMA Regulatory Sandbox for AI-powered lending products.

**MVP Scope**: A Dockerized, offline-capable demo with a mock lending agent, regulatory mapping engine, and Arabic PDF report generator, accessed through a Streamlit web interface.

---

## 2. User Stories

### 2.1 Compliance Officer (Noura)

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-01 | As a compliance officer, I want to select a demo SME application so I can see how the AI agent evaluates it. | Dropdown with 3 pre-loaded scenarios. Selection displays company details in Arabic. |
| US-02 | As a compliance officer, I want to see the agent's decision with Arabic explanations so I can understand why it approved or rejected. | Decision card shows: decision (Arabic), all triggered rules with Arabic rationale, pass/fail status for each rule. |
| US-03 | As a compliance officer, I want to generate a SAMA-compliant Arabic PDF report so I can submit it to auditors. | PDF downloads with all 4 sections (Summary, Rules, Regulatory Map, Fairness Statement) in correct RTL Arabic. |
| US-04 | As a compliance officer, I want to see the regulatory mapping so I can verify which SAMA principles were checked. | Table shows rule ID → SAMA principle → article → compliance statement in Arabic. |

### 2.2 AI/ML Engineer (Fahad)

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-05 | As an ML engineer, I want to see the raw JSON decision output so I can debug agent behavior. | Expandable JSON viewer in the UI showing complete agent output. |
| US-06 | As an ML engineer, I want to run multiple scenarios quickly so I can validate rule coverage. | Can switch between 3 scenarios and re-run without page refresh. |
| US-07 | As an ML engineer, I want the system to run offline in Docker so I can demo in air-gapped environments. | `docker-compose up --build` launches fully functional system on port 8501. |

---

## 3. Functional Requirements

### 3.1 Mock Agent Engine (`agent.py`)

#### 3.1.1 Input Schema

```json
{
  "company_name": "string (Arabic)",
  "company_name_en": "string (English)",
  "cr_number": "string (10-digit CR)",
  "business_activity": "string",
  "business_activity_ar": "string (Arabic)",
  "business_age_years": "number",
  "annual_revenue_sar": "number",
  "existing_debt_sar": "number",
  "requested_loan_sar": "number",
  "absher_verified": "boolean",
  "owner_name": "string (Arabic)",
  "owner_national_id": "string"
}
```

#### 3.1.2 Rule Definitions (`rules.json`)

| Rule ID | Name (EN) | Name (AR) | Logic | Arabic Rationale |
|---|---|---|---|---|
| `RULE-001` | Debt-to-Revenue Ratio | نسبة الدين إلى الإيرادات | `(existing_debt + requested_loan) / annual_revenue > 0.50` | نسبة الدين إلى الإيرادات تتجاوز الحد المسموح (50%) وفقاً لإرشادات الإقراض المسؤول |
| `RULE-002` | Excluded Activity | النشاط المحظور | `business_activity in EXCLUDED_LIST` | النشاط التجاري مدرج في قائمة الأنشطة المحظورة من قبل البنك المركزي السعودي |
| `RULE-003` | Business Age | عمر السجل التجاري | `business_age_years < 1` | عمر السجل التجاري أقل من الحد الأدنى المطلوب (سنة واحدة) |
| `RULE-004` | Identity Verification | التحقق من الهوية | `absher_verified == false` | فشل التحقق من هوية مالك المنشأة عبر منصة أبشر/نفاذ |
| `RULE-005` | Loan Amount Limit | حد مبلغ التمويل | `requested_loan > 2,000,000` | مبلغ التمويل المطلوب يتجاوز الحد الأقصى المسموح (2,000,000 ريال) |

**Excluded Activities List**: `["tobacco_trading", "gambling", "weapons", "money_exchange_unlicensed", "speculative_real_estate"]`

#### 3.1.3 Output Schema

```json
{
  "decision_id": "AUD-2026-XXXXX",
  "timestamp": "ISO 8601",
  "application": { "...input data..." },
  "decision": "approved | rejected",
  "decision_ar": "موافقة | مرفوض",
  "rules_evaluated": [
    {
      "rule_id": "RULE-001",
      "rule_name": "Debt-to-Revenue Ratio",
      "rule_name_ar": "نسبة الدين إلى الإيرادات",
      "passed": true/false,
      "details": "Computed DTR: 35%",
      "details_ar": "نسبة الدين المحسوبة: 35%",
      "rationale_ar": "..."
    }
  ],
  "triggered_rules": ["RULE-IDs that failed"],
  "risk_score": "low | medium | high"
}
```

---

### 3.2 Regulatory Mapping Engine (`regulatory.py`)

#### 3.2.1 Mapping Table (`reg_map.json`)

Each entry links an agent rule to SAMA regulatory context:

```json
{
  "RULE-001": {
    "sama_principle_id": "PRINCIPLE-04",
    "sama_principle_name": "Transparency",
    "sama_principle_name_ar": "الشفافية",
    "regulatory_reference": "إرشادات الإقراض المسؤول - المادة 12",
    "regulatory_reference_en": "Responsible Lending Guidelines - Article 12",
    "audit_statement_ar": "تم تقييم نسبة الدين إلى الإيرادات وفقاً للحد الأقصى المنصوص عليه في إرشادات الإقراض المسؤول الصادرة عن البنك المركزي السعودي (المادة 12). الحد المسموح: 50%.",
    "compliance_status_pass_ar": "ملتزم - النسبة ضمن الحد المسموح",
    "compliance_status_fail_ar": "غير ملتزم - النسبة تتجاوز الحد المسموح"
  }
}
```

#### 3.2.2 Engine Functions

| Function | Description |
|---|---|
| `get_regulatory_mapping(rule_id)` | Returns the full SAMA mapping for a given rule ID. |
| `generate_compliance_report(agent_output)` | Takes agent output, enriches each rule evaluation with regulatory mapping, returns compliance-enriched output. |
| `get_fairness_statement()` | Returns the standardized Arabic fairness statement. |
| `get_all_mappings()` | Returns the complete mapping table for display. |

---

### 3.3 Report Generator (`report.py`)

#### 3.3.1 PDF Specifications

| Spec | Value |
|---|---|
| **Page Size** | A4 |
| **Font** | Noto Naskh Arabic (Regular + Bold) |
| **Direction** | RTL (Right-to-Left) |
| **Library** | reportlab 4.x |
| **Arabic Processing** | arabic-reshaper + python-bidi |
| **Sections** | 4: Decision Summary, Rule Rationale, Regulatory Map, Fairness Statement |
| **Color Scheme** | SAMA green (#006B3F), Header dark (#1a1a2e), Approved green (#27ae60), Rejected red (#e74c3c) |

#### 3.3.2 PDF Sections

1. **Header**: Report title "تقرير تدقيق قرار الإقراض بالذكاء الاصطناعي", report ID, generation timestamp.
2. **Decision Summary (ملخص القرار)**: Company name, CR, amount, decision badge (green/red), date.
3. **Rule Rationale Table (جدول مبررات القواعد)**: Table with columns: Rule ID, Rule Name (AR), Result (✓/✗), Arabic Rationale.
4. **Regulatory Compliance Map (خريطة الالتزام التنظيمي)**: Table with columns: Rule ID, SAMA Principle (AR), Regulatory Reference, Arabic Audit Statement.
5. **Fairness Statement (بيان العدالة)**: Full Arabic paragraph on non-discrimination.
6. **Footer**: Signature line, date, "تم إنشاء هذا التقرير آلياً بواسطة نظام SamaAudit".

---

### 3.4 Web Interface (`main.py` — Streamlit)

#### 3.4.1 Page Layout

```
┌──────────────────────────────────────────┐
│  🏦 SamaAudit                            │
│  نظام تدقيق قرارات الإقراض بالذكاء       │
│  الاصطناعي                                │
├──────────────────────────────────────────┤
│  [Sidebar]                               │
│  📋 اختيار السيناريو (Scenario Selector) │
│  ├─ شركة النخبة للتجارة (Approved)       │
│  ├─ مؤسسة الفجر (High Debt Rejected)     │
│  └─ شركة الدخان العربية (Excluded)        │
│                                           │
│  [Main Area]                             │
│  ┌─ بيانات الشركة (Company Data Card) ─┐ │
│  │  Name, CR, Revenue, Debt, etc.       │ │
│  └──────────────────────────────────────┘ │
│                                           │
│  [ 🚀 تشغيل الوكيل (Run Agent) ]        │
│                                           │
│  ┌─ نتيجة القرار (Decision Result) ────┐ │
│  │  ✅ موافقة / ❌ مرفوض + reason      │ │
│  └──────────────────────────────────────┘ │
│                                           │
│  ┌─ تفاصيل القواعد (Rule Details) ─────┐ │
│  │  Table: Rules + Pass/Fail + Arabic   │ │
│  └──────────────────────────────────────┘ │
│                                           │
│  ┌─ خريطة الالتزام (Compliance Map) ───┐ │
│  │  Table: Rules → SAMA Principles      │ │
│  └──────────────────────────────────────┘ │
│                                           │
│  [ 📄 توليد تقرير SAMA (Generate PDF) ] │
│                                           │
│  ┌─ عرض التقرير (Report Preview) ──────┐ │
│  │  PDF download link                   │ │
│  └──────────────────────────────────────┘ │
│                                           │
│  [Expander: JSON Output for Engineers]   │
└──────────────────────────────────────────┘
```

---

## 4. Non-Functional Requirements

| Requirement | Specification |
|---|---|
| **Language** | UI primary language: Arabic (RTL). Technical elements (JSON, code) in English. |
| **Deployment** | Docker container via docker-compose. Single command: `docker-compose up --build`. |
| **Offline** | No external API calls. All data, fonts, and logic bundled in container. |
| **Performance** | Agent evaluation < 100ms. PDF generation < 2 seconds. |
| **Browser** | Chrome, Edge, Safari (modern versions). |
| **Accessibility** | Arabic text properly reshaped and displayed RTL. |

---

## 5. Demo Scenarios

### Scenario 1: ✅ Approved — شركة النخبة للتجارة (Al-Nukhba Trading Co.)

```json
{
  "company_name": "شركة النخبة للتجارة",
  "company_name_en": "Al-Nukhba Trading Co.",
  "cr_number": "1010234567",
  "business_activity": "wholesale_trading",
  "business_activity_ar": "تجارة الجملة",
  "business_age_years": 5,
  "annual_revenue_sar": 3000000,
  "existing_debt_sar": 500000,
  "requested_loan_sar": 750000,
  "absher_verified": true,
  "owner_name": "أحمد بن محمد العتيبي",
  "owner_national_id": "1087654321"
}
```
**Expected Result**: All rules pass. DTR = (500K + 750K) / 3M = 41.7%. Decision: **Approved (موافقة)**.

### Scenario 2: ❌ Rejected — مؤسسة الفجر للمقاولات (Al-Fajr Contracting Est.)

```json
{
  "company_name": "مؤسسة الفجر للمقاولات",
  "company_name_en": "Al-Fajr Contracting Est.",
  "cr_number": "4030567890",
  "business_activity": "contracting",
  "business_activity_ar": "مقاولات",
  "business_age_years": 3,
  "annual_revenue_sar": 1500000,
  "existing_debt_sar": 600000,
  "requested_loan_sar": 500000,
  "absher_verified": true,
  "owner_name": "فهد بن عبدالله الراشدي",
  "owner_national_id": "1098765432"
}
```
**Expected Result**: RULE-001 triggers. DTR = (600K + 500K) / 1.5M = 73.3%. Decision: **Rejected (مرفوض)** — High debt ratio.

### Scenario 3: ❌ Rejected — شركة الدخان العربية (Arabian Tobacco Co.)

```json
{
  "company_name": "شركة الدخان العربية",
  "company_name_en": "Arabian Tobacco Co.",
  "cr_number": "2050345678",
  "business_activity": "tobacco_trading",
  "business_activity_ar": "تجارة التبغ",
  "business_age_years": 10,
  "annual_revenue_sar": 5000000,
  "existing_debt_sar": 1000000,
  "requested_loan_sar": 1500000,
  "absher_verified": true,
  "owner_name": "خالد بن سعود المالكي",
  "owner_national_id": "1076543210"
}
```
**Expected Result**: RULE-002 triggers (tobacco = excluded activity). DTR = 50% (borderline pass). Decision: **Rejected (مرفوض)** — Excluded activity.

---

## 6. Technology Stack

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.11 |
| Web Framework | Streamlit | 1.45.0 |
| PDF Generation | reportlab | 4.2.5 |
| Arabic Text Reshaping | arabic-reshaper | 3.0.0 |
| BiDi Processing | python-bidi | 0.6.4 |
| Containerization | Docker | Latest |
| Orchestration | docker-compose | Latest |
| Data Format | JSON | - |

---

## 7. Project File Structure

```
samaaudit/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app/
│   ├── main.py            # Streamlit app (Arabic UI)
│   ├── agent.py            # Mock agent engine
│   ├── regulatory.py       # Regulatory mapping engine
│   ├── report.py           # Arabic PDF generator
│   ├── scenarios.json      # 3 demo companies
│   ├── rules.json          # Agent rules
│   └── reg_map.json        # Regulatory mapping
└── fonts/
    └── README.md           # Instructions to download Noto Naskh Arabic
```

---

## 8. Out of Scope (MVP)

| Item | Rationale |
|---|---|
| Real LLM / AI Model | MVP uses hardcoded rules to demonstrate audit trail concept. |
| Real Absher/Nafath API | Mock verification only. Real integration requires SAMA sandbox access. |
| Production Security | No auth, encryption, or access control in MVP. |
| Database | In-memory/JSON only. No persistent storage. |
| Multi-tenancy | Single-user demo only. |
| Real-time Monitoring | Batch decision evaluation only. |
| Mobile Responsive | Desktop-first for MVP. |

---

*End of Stage 2 PRD*
