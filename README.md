# SamaAudit — SME Lending Agent Audit Trail MVP

SamaAudit is a specialized AI Governance & Audit Trail MVP built for Saudi banks. It bridges the gap between technical AI agent logs and SAMA regulatory compliance by mapping decision logic directly to regulatory principles and generating automated, SAMA-compliant Arabic audit reports.

---

## 🌟 Key Features

1. **Regulatory Translation Engine:** Translates raw AI decision triggers into precise SAMA AI and Responsible Lending compliance statements in Arabic.
2. **SAMA AI Principles Alignment:**
   - **Principle #4 (Transparency):** Detailed rule rationale and structured audit trails.
   - **Principle #5 (Fairness):** Built-in fairness validation and non-discrimination check.
3. **Arabic PDF Generator:** Generates professional, SAMA-ready RTL PDF audit reports with embedded Noto Naskh Arabic fonts.
4. **SME Lending Ruleset (Beachhead Market):**
   - Debt-to-Revenue Ratio limits (Article 12, SAMA Guidelines)
   - SAMA Excluded Activities check (AML/CFT Guidelines)
   - Business Age validation
   - Identity verification via Absher/Nafath mock integration
   - Loan size thresholds
5. **Interactive UI:** Built with Streamlit in a premium high-contrast dark theme optimized for both compliance officers and ML engineers.

---

## 📂 Project Structure

```
samaaudit/
├── Dockerfile                  # Docker container setup with fonts
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
├── app/
│   ├── main.py                 # Streamlit dashboard (Arabic UI)
│   ├── agent.py                # Mock agent rule evaluation
│   ├── regulatory.py           # Regulatory Mapping Engine
│   ├── report.py               # Arabic PDF Report Generator
│   ├── scenarios.json          # 3 Saudi SME evaluation scenarios
│   ├── rules.json              # Agent rule parameters
│   └── reg_map.json            # Rule -> SAMA compliance mapping
└── fonts/
    └── NotoNaskhArabic-*.ttf   # Embedded Arabic fonts
```

---

## 🚀 How to Run

### Option 1: Using Docker (Recommended)
Launch the application in a completely containerized environment:
```bash
docker-compose up --build
```
Once initialized, open [http://localhost:8501](http://localhost:8501) in your browser.

### Option 2: Running Locally
Install dependencies and run the dashboard directly:
```bash
pip install -r samaaudit/requirements.txt
streamlit run samaaudit/app/main.py
```

---

## 🛠️ Verification Scenarios

| Scenario | Company | Status | Triggered Rule |
|---|---|---|---|
| **Scenario 1** | Al-Nukhba Trading Co. | ✅ Approved | None (All SAMA rules met) |
| **Scenario 2** | Al-Fajr Contracting Est. | ❌ Rejected | `RULE-001` (DTR 73.3% > 50% limit) |
| **Scenario 3** | Arabian Tobacco Co. | ❌ Rejected | `RULE-002` (Excluded business activity) |
