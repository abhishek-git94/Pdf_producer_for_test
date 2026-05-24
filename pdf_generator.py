from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable
from io import BytesIO

PRIMARY = HexColor("#667eea")
SECONDARY = HexColor("#764ba2")
DARK = HexColor("#1a1a2e")
LIGHT = HexColor("#f8f9fa")
ACCENT = HexColor("#f093fb")

def create_assessment_pdf(subject, topic, difficulty, questions):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=20*mm,
        leftMargin=18*mm,
        rightMargin=18*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCustom",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=4,
        spaceBefore=0
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCustom",
        fontName="Helvetica",
        fontSize=11,
        textColor=HexColor("#666666"),
        alignment=TA_CENTER,
        spaceAfter=16
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=DARK,
        spaceBefore=14,
        spaceAfter=6,
        borderWidth=0,
        borderColor=PRIMARY,
        borderPadding=4
    ))
    styles.add(ParagraphStyle(
        name="QuestionText",
        fontName="Helvetica",
        fontSize=10.5,
        textColor=DARK,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
        leading=15
    ))
    styles.add(ParagraphStyle(
        name="OptionText",
        fontName="Helvetica",
        fontSize=10,
        textColor=HexColor("#333333"),
        alignment=TA_LEFT,
        leftIndent=12,
        spaceBefore=1,
        spaceAfter=1,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name="AnswerBox",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=HexColor("#155724"),
        alignment=TA_LEFT,
        leftIndent=12,
        spaceBefore=4,
        spaceAfter=2,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name="ExplanationText",
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        textColor=HexColor("#555555"),
        alignment=TA_JUSTIFY,
        leftIndent=12,
        spaceBefore=2,
        spaceAfter=8,
        leading=13
    ))
    styles.add(ParagraphStyle(
        name="FooterStyle",
        fontName="Helvetica",
        fontSize=8,
        textColor=HexColor("#999999"),
        alignment=TA_CENTER
    ))

    elements = []

    elements.append(Paragraph("Abhi Gen_AI", styles["TitleCustom"]))
    elements.append(Paragraph("AI-Generated Assessment", styles["SubtitleCustom"]))

    header_data = [
        ["Subject", subject],
        ["Topic", topic],
        ["Difficulty", difficulty],
        ["Total Questions", str(len(questions))]
    ]
    header_table = Table(header_data, colWidths=[120, 340])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PRIMARY),
        ("TEXTCOLOR", (0, 0), (0, -1), white),
        ("BACKGROUND", (1, 0), (1, -1), HexColor("#f0f0ff")),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 14))

    elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    elements.append(Paragraph("<b>SECTION A - MULTIPLE CHOICE QUESTIONS</b>", styles["SectionHeader"]))
    elements.append(Spacer(1, 4))

    for i, q in enumerate(questions, 1):
        q_bg_color = HexColor("#f9f9ff") if i % 2 == 0 else white

        question_text = f'<b>Q{i}.</b>  {q["question"]}'
        elements.append(Paragraph(question_text, styles["QuestionText"]))

        opt_labels = ["A", "B", "C", "D"]
        for label in opt_labels:
            opt_text = q["options"].get(label, "")
            elements.append(Paragraph(f'<b>({label})</b>  {opt_text}', styles["OptionText"]))

        elements.append(Spacer(1, 2))
        hr = HRFlowable(width="60%", thickness=0.5, color=HexColor("#eeeeee"), spaceAfter=6, spaceBefore=2)
        elements.append(hr)

    elements.append(PageBreak())
    elements.append(Paragraph("<b>ANSWER KEY & EXPLANATIONS</b>", styles["SectionHeader"]))
    elements.append(Spacer(1, 6))

    for i, q in enumerate(questions, 1):
        ans = q["correct_answer"]
        ans_text = q["options"].get(ans, "")
        explanation = q.get("explanation", "No explanation provided.")

        answer_block = [
            [Paragraph(f'<b>Q{i}.</b>', styles["AnswerBox"]),
             Paragraph(f'<b>Answer: {ans}) {ans_text}</b>', styles["AnswerBox"])]
        ]
        ans_table = Table(answer_block, colWidths=[30, 430])
        ans_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#d4edda") if i % 2 == 1 else HexColor("#e8f5e9")),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#c3e6cb")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(ans_table)

        elements.append(Paragraph(f'<i>Explanation:</i> {explanation}', styles["ExplanationText"]))

        if i < len(questions):
            elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc"), spaceAfter=6))

    footer_text = "Generated by Abhi Gen_AI — Powered by Groq API & Llama 3.1"
    elements.append(Paragraph(footer_text, styles["FooterStyle"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
