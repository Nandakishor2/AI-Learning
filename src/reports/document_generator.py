import os
from pathlib import Path
from typing import Dict, List, Any
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def set_cell_background(cell, fill_hex):
    """Set background shading for a docx table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def generate_docx_report(data: Dict[str, Any], output_path: Path) -> str:
    """Generates a professional DOCX document from structured data."""
    doc = docx.Document()

    # Page Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title
    title = data.get("title", "AI Engineering League Report")
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run(title)
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(26, 54, 93)

    # Subtitle
    subtitle = data.get("subtitle", "")
    if subtitle:
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sub = p_sub.add_run(subtitle)
        run_sub.font.name = "Calibri"
        run_sub.font.size = Pt(13)
        run_sub.font.italic = True
        run_sub.font.color.rgb = RGBColor(74, 85, 104)

    doc.add_paragraph() # Spacer

    # Process Sections
    for sec in data.get("sections", []):
        heading = sec.get("heading", "")
        level = sec.get("level", 1)
        paragraphs = sec.get("paragraphs", [])
        table_data = sec.get("table", [])
        code_block = sec.get("code", "")

        if heading:
            p_h = doc.add_paragraph()
            run_h = p_h.add_run(heading)
            run_h.font.name = "Calibri"
            run_h.font.bold = True
            if level == 1:
                run_h.font.size = Pt(16)
                run_h.font.color.rgb = RGBColor(43, 108, 176)
                p_h.paragraph_format.space_before = Pt(12)
                p_h.paragraph_format.space_after = Pt(4)
            elif level == 2:
                run_h.font.size = Pt(13)
                run_h.font.color.rgb = RGBColor(45, 55, 72)
                p_h.paragraph_format.space_before = Pt(8)
                p_h.paragraph_format.space_after = Pt(3)
            else:
                run_h.font.size = Pt(11)
                run_h.font.bold = True
                p_h.paragraph_format.space_before = Pt(6)
                p_h.paragraph_format.space_after = Pt(2)

        for p_text in paragraphs:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(p_text)
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)

        if table_data and len(table_data) > 0:
            nrows = len(table_data)
            ncols = len(table_data[0])
            table = doc.add_table(rows=nrows, cols=ncols)
            table.style = 'Table Grid'
            table.alignment = WD_ALIGN_PARAGRAPH.CENTER

            for r_idx, row in enumerate(table_data):
                for c_idx, val in enumerate(row):
                    cell = table.cell(r_idx, c_idx)
                    cell.text = str(val)
                    p_cell = cell.paragraphs[0]
                    p_cell.paragraph_format.space_before = Pt(2)
                    p_cell.paragraph_format.space_after = Pt(2)
                    for r in p_cell.runs:
                        r.font.name = "Calibri"
                        r.font.size = Pt(9.5)
                    if r_idx == 0:
                        set_cell_background(cell, "2B6CB0") # Blue header
                        for r in p_cell.runs:
                            r.font.bold = True
                            r.font.color.rgb = RGBColor(255, 255, 255)
                    elif r_idx % 2 == 1:
                        set_cell_background(cell, "F7FAFC") # Zebra row
            doc.add_paragraph() # Spacer

        if code_block:
            p_code = doc.add_paragraph()
            p_code.paragraph_format.space_before = Pt(4)
            p_code.paragraph_format.space_after = Pt(6)
            run_code = p_code.add_run(code_block)
            run_code.font.name = "Consolas"
            run_code.font.size = Pt(9)
            run_code.font.color.rgb = RGBColor(45, 55, 72)

    output_path = Path(output_path)
    os.makedirs(output_path.parent, exist_ok=True)
    doc.save(str(output_path))
    return str(output_path)

def generate_pdf_report(data: Dict[str, Any], output_path: Path) -> str:
    """Generates a professional PDF document from structured data."""
    output_path = Path(output_path)
    os.makedirs(output_path.parent, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Center
        spaceAfter=6
    )
    
    style_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4A5568'),
        alignment=1, # Center
        spaceAfter=14
    )

    style_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1A202C'),
        spaceAfter=4
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1A202C')
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    style_code = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#2D3748')
    )

    story = []
    story.append(Paragraph(data.get("title", "AI Engineering League Report"), style_title))
    if data.get("subtitle"):
        story.append(Paragraph(data.get("subtitle"), style_subtitle))
    story.append(Spacer(1, 8))

    for sec in data.get("sections", []):
        heading = sec.get("heading", "")
        level = sec.get("level", 1)
        paragraphs = sec.get("paragraphs", [])
        table_data = sec.get("table", [])
        code_block = sec.get("code", "")

        if heading:
            st = style_h1 if level == 1 else style_h2
            story.append(Paragraph(heading, st))

        for p_text in paragraphs:
            story.append(Paragraph(p_text.replace("\n", "<br/>"), style_body))

        if table_data and len(table_data) > 0:
            formatted_table_data = []
            for r_idx, row in enumerate(table_data):
                formatted_row = []
                for val in row:
                    st = style_table_header if r_idx == 0 else style_table_cell
                    formatted_row.append(Paragraph(str(val).replace("\n", "<br/>"), st))
                formatted_table_data.append(formatted_row)

            col_count = len(table_data[0])
            col_width = 530.0 / col_count
            t = Table(formatted_table_data, colWidths=[col_width]*col_count)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))

        if code_block:
            story.append(Spacer(1, 3))
            story.append(Preformatted(code_block, style_code))
            story.append(Spacer(1, 5))

    doc.build(story)
    return str(output_path)

def create_dual_format_report(data: Dict[str, Any], base_path_no_ext: str) -> Dict[str, str]:
    """Generates both .docx and .pdf versions simultaneously."""
    docx_file = f"{base_path_no_ext}.docx"
    pdf_file = f"{base_path_no_ext}.pdf"
    p_docx = generate_docx_report(data, Path(docx_file))
    p_pdf = generate_pdf_report(data, Path(pdf_file))
    return {"docx": p_docx, "pdf": p_pdf}
