"""
SamaAudit — Mock Agent Engine
Simulates an AI lending agent with 5 hardcoded SAMA-compliant rules.
Each rule evaluates one aspect of an SME loan application and produces
a structured decision with Arabic rationale.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent


def load_rules() -> dict:
    """Load rule definitions from rules.json."""
    with open(BASE_DIR / "rules.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_scenarios() -> list:
    """Load demo scenarios from scenarios.json."""
    with open(BASE_DIR / "scenarios.json", "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_application(application: dict) -> dict:
    """
    Evaluate an SME loan application against all SAMA lending rules.

    Args:
        application: dict with company data (name, CR, revenue, debt, etc.)

    Returns:
        Structured decision output with all rule evaluations.
    """
    rules_data = load_rules()
    rules = rules_data["rules"]
    excluded_activities = list(rules_data["excluded_activities"].keys())

    results = []
    triggered_rules = []

    for rule in rules:
        rule_id = rule["rule_id"]
        passed = True
        details_en = ""
        details_ar = ""

        if rule_id == "RULE-001":
            # Debt-to-Revenue Ratio check
            total_debt = application["existing_debt_sar"] + application["requested_loan_sar"]
            revenue = application["annual_revenue_sar"]
            dtr = total_debt / revenue if revenue > 0 else 999.0
            dtr_pct = round(dtr * 100, 1)
            threshold_pct = int(rule["threshold"] * 100)
            passed = dtr <= rule["threshold"]
            details_en = f"Computed DTR: {dtr_pct}% (threshold: {threshold_pct}%)"
            details_ar = f"نسبة الدين المحسوبة: {dtr_pct}% (الحد المسموح: {threshold_pct}%)"

        elif rule_id == "RULE-002":
            # Excluded Activity check
            activity = application["business_activity"]
            is_excluded = activity in excluded_activities
            passed = not is_excluded
            if is_excluded:
                activity_ar = rules_data["excluded_activities"].get(activity, activity)
                details_en = f"Activity '{activity}' is in excluded list"
                details_ar = f"النشاط '{activity_ar}' مدرج في قائمة المحظورات"
            else:
                details_en = f"Activity '{activity}' is permitted"
                details_ar = "النشاط التجاري مسموح به"

        elif rule_id == "RULE-003":
            # Business Age check
            age = application["business_age_years"]
            min_years = rule["min_years"]
            passed = age >= min_years
            details_en = f"Business age: {age} year(s) (minimum: {min_years})"
            details_ar = f"عمر المنشأة: {age} سنة (الحد الأدنى: {min_years})"

        elif rule_id == "RULE-004":
            # Absher Identity Verification check
            passed = application.get("absher_verified", False)
            status_en = "Passed" if passed else "Failed"
            status_ar = "ناجح" if passed else "فاشل"
            details_en = f"Absher verification: {status_en}"
            details_ar = f"التحقق عبر أبشر: {status_ar}"

        elif rule_id == "RULE-005":
            # Loan Amount Limit check
            amount = application["requested_loan_sar"]
            max_amount = rule["max_amount"]
            passed = amount <= max_amount
            details_en = f"Requested: SAR {amount:,.0f} (limit: SAR {max_amount:,.0f})"
            details_ar = f"المبلغ المطلوب: {amount:,.0f} ريال (الحد: {max_amount:,.0f} ريال)"

        # Select appropriate rationale based on pass/fail
        rationale_ar = rule["rationale_pass_ar"] if passed else rule["rationale_fail_ar"]

        if not passed:
            triggered_rules.append(rule_id)

        results.append({
            "rule_id": rule_id,
            "rule_name_en": rule["rule_name_en"],
            "rule_name_ar": rule["rule_name_ar"],
            "severity": rule["severity"],
            "passed": passed,
            "details_en": details_en,
            "details_ar": details_ar,
            "rationale_ar": rationale_ar,
        })

    # Final decision: rejected if ANY critical rule fails
    critical_failures = [r for r in results if not r["passed"] and r["severity"] == "critical"]
    decision = "approved" if len(critical_failures) == 0 else "rejected"
    decision_ar = "موافقة" if decision == "approved" else "مرفوض"

    # Simple risk score based on failure count
    failed_count = len([r for r in results if not r["passed"]])
    if failed_count == 0:
        risk_score = "low"
        risk_score_ar = "منخفض"
    elif failed_count == 1:
        risk_score = "medium"
        risk_score_ar = "متوسط"
    else:
        risk_score = "high"
        risk_score_ar = "مرتفع"

    decision_id = f"AUD-2026-{uuid.uuid4().hex[:5].upper()}"

    return {
        "decision_id": decision_id,
        "timestamp": datetime.now().isoformat(),
        "application": application,
        "decision": decision,
        "decision_ar": decision_ar,
        "risk_score": risk_score,
        "risk_score_ar": risk_score_ar,
        "rules_evaluated": results,
        "triggered_rules": triggered_rules,
        "total_rules": len(results),
        "passed_rules": len([r for r in results if r["passed"]]),
        "failed_rules": len([r for r in results if not r["passed"]]),
    }
