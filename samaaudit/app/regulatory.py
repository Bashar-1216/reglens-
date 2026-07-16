"""
SamaAudit — Regulatory Mapping Engine
The core "Regulatory Translation Engine" that maps agent rule evaluations
to SAMA regulatory principles and generates Arabic compliance statements.
This is the unique value proposition of SamaAudit.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


def load_reg_map() -> dict:
    """Load the regulatory mapping table from reg_map.json."""
    with open(BASE_DIR / "reg_map.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_regulatory_mapping(rule_id: str) -> dict:
    """Get the full SAMA regulatory mapping for a specific rule ID."""
    reg_map = load_reg_map()
    return reg_map.get(rule_id, {})


def get_fairness_statement() -> str:
    """Return the standardized Arabic fairness statement (SAMA Principle #5)."""
    reg_map = load_reg_map()
    return reg_map.get("fairness_statement_ar", "")


def get_fairness_principle() -> dict:
    """Return the fairness principle metadata."""
    reg_map = load_reg_map()
    return reg_map.get("fairness_principle", {})


def generate_compliance_report(agent_output: dict) -> dict:
    """
    Take raw agent output and enrich it with regulatory compliance mappings.

    This is the core Regulatory Translation Engine function:
    Agent Decision → SAMA Principle → Regulatory Article → Arabic Audit Statement

    Args:
        agent_output: The structured output from agent.evaluate_application()

    Returns:
        Compliance-enriched report with regulatory mappings ready for PDF generation.
    """
    reg_map = load_reg_map()

    compliance_entries = []

    for rule_eval in agent_output["rules_evaluated"]:
        rule_id = rule_eval["rule_id"]
        mapping = reg_map.get(rule_id, {})

        if mapping:
            compliance_status = (
                mapping["compliance_status_pass_ar"]
                if rule_eval["passed"]
                else mapping["compliance_status_fail_ar"]
            )

            compliance_entries.append({
                "rule_id": rule_id,
                "rule_name_ar": rule_eval["rule_name_ar"],
                "sama_principle_id": mapping["sama_principle_id"],
                "sama_principle_name_ar": mapping["sama_principle_name_ar"],
                "sama_principle_name_en": mapping["sama_principle_name_en"],
                "regulatory_reference_ar": mapping["regulatory_reference_ar"],
                "regulatory_reference_en": mapping["regulatory_reference_en"],
                "audit_statement_ar": mapping["audit_statement_ar"],
                "compliance_status_ar": compliance_status,
                "passed": rule_eval["passed"],
            })

    return {
        "decision_id": agent_output["decision_id"],
        "timestamp": agent_output["timestamp"],
        "company_name": agent_output["application"]["company_name"],
        "company_name_en": agent_output["application"]["company_name_en"],
        "cr_number": agent_output["application"]["cr_number"],
        "requested_amount": agent_output["application"]["requested_loan_sar"],
        "decision": agent_output["decision"],
        "decision_ar": agent_output["decision_ar"],
        "risk_score_ar": agent_output["risk_score_ar"],
        "compliance_entries": compliance_entries,
        "fairness_statement_ar": get_fairness_statement(),
        "fairness_principle": get_fairness_principle(),
        "rules_evaluated": agent_output["rules_evaluated"],
    }
