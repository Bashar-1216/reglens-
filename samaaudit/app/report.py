"""
SamaAudit — Arabic PDF Report Generator
Generates SAMA-style audit reports with proper RTL Arabic text.
Uses reportlab with arabic-reshaper and python-bidi for correct Arabic rendering.
"""

import io
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display

# ──────────────────────────────────────────────
# Colors — SAMA brand palette
# ──────────────────────────────────────────────
SAMA_GREEN = colors.HexColor("#006B3F")
HEADER_BG = colors.HexColor("#0a2647")
APPROVED_GREEN = colors.HexColor("#27ae60")
REJECTED_RED = colors.HexColor("#e74c3c")
LIGHT_GRAY = colors.HexColor("#f5f6fa")
MEDIUM_GRAY = colors.HexColor("#dcdde1")
DARK_TEXT = colors.HexColor("#2c3e50")
WHITE = colors.white

# ──────────────────────────────────────────────
# Font registration
# ──────────────────────────────────────────────
FONTS_DIR = Path(__file__).parent.parent / "fonts"


def _register_fonts():
    """Register Noto Naskh Arabic. Falls back to Helvetica if unavailable."""
    regular = FONTS_DIR / "NotoNaskhArabic-Regular.ttf"
    bold = FONTS_DIR / "NotoNaskhArabic-Bold.ttf"

    if regular.exists():
        pdfmetrics.registerFont(TTFont("ArabicFont", str(regular)))
        bold_path = bold if bold.exists() else regular
        pdfmetrics.registerFont(TTFont("ArabicFontBold", str(bold_path)))
        return "ArabicFont", "ArabicFontBold"

    return "Helvetica", "Helvetica-Bold"


def _ar(text: str) -> str:
    """Reshape and reorder Arabic text for correct RTL rendering in PDF."""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# ──────────────────────────────────────────────
# PDF generation
# ──────────────────────────────────────────────

def generate_pdf(compliance_report: dict) -> bytes:
    """
    Generate a professional SAMA-style Arabic audit report as PDF bytes.

    The report contains 4 sections:
    1. Decision Summary (ملخص القرار)
    2. Rule Rationale Table (جدول مبررات القواعد)
    3. Regulatory Compliance Map (خريطة الالتزام التنظيمي)
    4. Fairness Statement (بيان العدالة)
    """
    font, font_bold = _register_fonts()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )

    # ── Paragraph styles ──
    styles = getSampleStyleSheet()

    s_title = ParagraphStyle(
        "Title_AR", parent=styles["Title"],
        fontName=font_bold, fontSize=18, alignment=TA_CENTER,
        textColor=DARK_TEXT, spaceAfter=2 * mm, leading=28,
    )
    s_subtitle = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontName=font, fontSize=10, alignment=TA_CENTER,
        textColor=colors.gray, spaceAfter=4 * mm, leading=16,
    )
    s_section = ParagraphStyle(
        "Section_AR", parent=styles["Heading2"],
        fontName=font_bold, fontSize=13, alignment=TA_RIGHT,
        textColor=SAMA_GREEN, spaceBefore=6 * mm, spaceAfter=3 * mm, leading=22,
    )
    s_body = ParagraphStyle(
        "Body_AR", parent=styles["Normal"],
        fontName=font, fontSize=9, alignment=TA_RIGHT,
        textColor=DARK_TEXT, leading=16, spaceAfter=2 * mm,
    )
    s_cell = ParagraphStyle(
        "Cell", parent=styles["Normal"],
        fontName=font, fontSize=8, alignment=TA_RIGHT,
        textColor=DARK_TEXT, leading=14,
    )
    s_cell_c = ParagraphStyle(
        "CellC", parent=styles["Normal"],
        fontName=font, fontSize=8, alignment=TA_CENTER,
        textColor=DARK_TEXT, leading=14,
    )
    s_hdr = ParagraphStyle(
        "CellHdr", parent=styles["Normal"],
        fontName=font_bold, fontSize=8, alignment=TA_CENTER,
        textColor=WHITE, leading=14,
    )
    s_footer = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName=font, fontSize=7, alignment=TA_CENTER,
        textColor=colors.gray, leading=12,
    )

    elements = []

    # ════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════
    elements.append(Paragraph(_ar("تقرير تدقيق قرار الإقراض بالذكاء الاصطناعي"), s_title))
    elements.append(Paragraph("AI Lending Decision Audit Report — SamaAudit", s_subtitle))
    elements.append(Paragraph(
        _ar(f"رقم التقرير: {compliance_report['decision_id']}"), s_subtitle
    ))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=SAMA_GREEN, spaceAfter=4 * mm))

    # ════════════════════════════════════════════
    # SECTION 1 — Decision Summary
    # ════════════════════════════════════════════
    elements.append(Paragraph(_ar("أولاً: ملخص القرار"), s_section))

    is_approved = compliance_report["decision"] == "approved"
    badge_color = APPROVED_GREEN if is_approved else REJECTED_RED

    summary_rows = [
        [Paragraph(_ar("القيمة"), s_hdr), Paragraph(_ar("البيان"), s_hdr)],
        [Paragraph(_ar(compliance_report["company_name"]), s_cell),
         Paragraph(_ar("اسم الشركة"), s_cell)],
        [Paragraph(compliance_report["cr_number"], s_cell_c),
         Paragraph(_ar("رقم السجل التجاري"), s_cell)],
        [Paragraph(f"{compliance_report['requested_amount']:,.0f} SAR", s_cell_c),
         Paragraph(_ar("مبلغ التمويل المطلوب"), s_cell)],
        [Paragraph(_ar(compliance_report["decision_ar"]), s_cell_c),
         Paragraph(_ar("القرار"), s_cell)],
        [Paragraph(_ar(compliance_report["risk_score_ar"]), s_cell_c),
         Paragraph(_ar("مستوى المخاطر"), s_cell)],
        [Paragraph(compliance_report["timestamp"][:19], s_cell_c),
         Paragraph(_ar("تاريخ ووقت القرار"), s_cell)],
    ]

    t1 = Table(summary_rows, colWidths=[95 * mm, 75 * mm])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 4), (0, 4), badge_color),
        ("TEXTCOLOR", (0, 4), (0, 4), WHITE),
    ]))
    elements.append(t1)

    # ════════════════════════════════════════════
    # SECTION 2 — Rule Rationale Table
    # ════════════════════════════════════════════
    elements.append(Paragraph(_ar("ثانياً: جدول مبررات القواعد"), s_section))

    rule_rows = [[
        Paragraph(_ar("المبرر"), s_hdr),
        Paragraph(_ar("النتيجة"), s_hdr),
        Paragraph(_ar("اسم القاعدة"), s_hdr),
        Paragraph(_ar("الرقم"), s_hdr),
    ]]

    for rule in compliance_report["rules_evaluated"]:
        mark = "\u2713" if rule["passed"] else "\u2717"
        mark_color = APPROVED_GREEN if rule["passed"] else REJECTED_RED
        s_mark = ParagraphStyle(
            "mark", parent=s_cell_c, textColor=mark_color,
            fontSize=12, fontName="Helvetica-Bold",
        )
        rule_rows.append([
            Paragraph(_ar(rule["rationale_ar"]), s_cell),
            Paragraph(mark, s_mark),
            Paragraph(_ar(rule["rule_name_ar"]), s_cell),
            Paragraph(rule["rule_id"], s_cell_c),
        ])

    t2 = Table(rule_rows, colWidths=[75 * mm, 20 * mm, 50 * mm, 25 * mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t2)

    # ════════════════════════════════════════════
    # SECTION 3 — Regulatory Compliance Map
    # ════════════════════════════════════════════
    elements.append(Paragraph(_ar("ثالثاً: خريطة الالتزام التنظيمي"), s_section))

    reg_rows = [[
        Paragraph(_ar("حالة الالتزام"), s_hdr),
        Paragraph(_ar("المرجع التنظيمي"), s_hdr),
        Paragraph(_ar("مبدأ ساما"), s_hdr),
        Paragraph(_ar("الرقم"), s_hdr),
    ]]

    for entry in compliance_report["compliance_entries"]:
        sc = APPROVED_GREEN if entry["passed"] else REJECTED_RED
        s_status = ParagraphStyle("cs", parent=s_cell, textColor=sc, fontSize=7)
        reg_rows.append([
            Paragraph(_ar(entry["compliance_status_ar"]), s_status),
            Paragraph(_ar(entry["regulatory_reference_ar"]), s_cell),
            Paragraph(_ar(entry["sama_principle_name_ar"]), s_cell),
            Paragraph(entry["rule_id"], s_cell_c),
        ])

    t3 = Table(reg_rows, colWidths=[55 * mm, 45 * mm, 40 * mm, 25 * mm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t3)

    # ════════════════════════════════════════════
    # SECTION 4 — Fairness Statement
    # ════════════════════════════════════════════
    elements.append(Paragraph(_ar("رابعاً: بيان العدالة"), s_section))
    elements.append(Paragraph(_ar(compliance_report["fairness_statement_ar"]), s_body))

    fp = compliance_report.get("fairness_principle", {})
    if fp:
        ref = fp.get("regulatory_reference_ar", "")
        s_ref = ParagraphStyle("ref", parent=s_body, fontSize=8, textColor=colors.gray)
        elements.append(Paragraph(_ar(f"المرجع: {ref}"), s_ref))

    # ════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MEDIUM_GRAY, spaceAfter=3 * mm))
    elements.append(Paragraph(_ar("تم إنشاء هذا التقرير آلياً بواسطة نظام SamaAudit"), s_footer))
    elements.append(Paragraph(
        _ar(f"تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), s_footer
    ))
    elements.append(Paragraph(_ar("هذا التقرير لأغراض التدقيق الداخلي فقط"), s_footer))

    # Build the PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
