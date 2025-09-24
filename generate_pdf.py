from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_payslip_pdf(employee, payroll):
    """Generate professional PDF payslip."""
    try:
        logger.debug(f"Generating payslip for employee {employee.id}, period {payroll.period}")
        
        # Initialize BytesIO buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin= 20 * mm,
            leftMargin= 20 * mm,
            topMargin= 15 * mm,
            bottomMargin= 15 * mm,
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName ="Helvetica-Bold",
            fontSize=16,
            leading= 20,
        )
        section_style = ParagraphStyle(
            'section',
            parent=styles['Heading4'],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12
        )
        normal_style = ParagraphStyle(
            'normal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
        )
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            leading=12,
        )

        # Content
        story = []

        # Containerizing the payslip
        container_width = 200
        col1 = int(container_width * 0.45)
        col2 = container_width - col1

        # Header
        story.append(Paragraph(f"Payslip {payroll.period}", title_style))
        # story.append(Paragraph(f"EMPLOYEE PAYSLIP - {payroll.period}", styles['Heading2']))
        story.append(Spacer(1, 6))

        # Employee Details Table
        emp_data = [
            ['Employee ID:', employee.id or 'N/A'],
            ['KRA PIN:', employee.kra_pin or 'N/A'],
            ['Name:', employee.full_name() or 'Unknown'],
            ['Period:', payroll.period or 'N/A'],
            ['Generated:', datetime.now().strftime('%d/%m/%Y')]
        ]
        emp_table = Table(emp_data, colWidths=[col1, col2], hAlign="LEFT")
        emp_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (1, 0), (1, -1), 6),
            ('RIGHTPADDING', (1, 0), (1, -1), 4),
            ('FONTSIZE', (0, 0), (-1, -1), 9.5),
            ('VALIGN', (0, 0), (-1, 1), 'MIDDLE')
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 6))

        # Paymeant breakdown
        benefits_total = payroll.gross_salary - employee.basic_salary
        earnings_data = [
            # ['DESCRIPTION', 'AMOUNT (KSh)'],
            ['Basic Salary', f"{employee.basic_salary:,.2f}"],
            ['Total Benefits', f"{benefits_total:,.2f}"],
            ['Gross Salary', f"{payroll.gross_salary:,.2f}"],
            ['(Less) NSSF Deduction', f"{payroll.nssf:,.2f}"],
            ['(Less) Housing Levy Deduction', f"{payroll.ahl:,.2f}"],
            ['(Less) SHIF Deduction', f"{payroll.shif:,.2f}"],
        ]
        earnings_table = Table(earnings_data, colWidths=[col1, col2])
        earnings_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (1, 0), (1, -1), 4),
            ('RIGHTPADDING', (1, 0), (1, -1), 6),
            ('FONTSIZE', (0, 0), (-1, -1), 9.5),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F7F7F8')])
        ]))
        story.append(Paragraph("Payment Breakdown", section_style))
        story.append(earnings_table)
        story.append(Spacer(1, 6))

        # Deductions Table
        total_deductions = payroll.nssf + payroll.ahl + payroll.paye + payroll.shif
        deductions_data = [
            # ['DEDUCTION', 'AMOUNT (KSh)'],
            ['Net Paye ', f"{payroll.paye:,.2f}"],
            ['NSSF Deduction', f"{payroll.nssf:,.2f}"],
            ['Housing Levy Deduction', f"{payroll.ahl:,.2f}"],
            ['SHIF Deduction', f"{payroll.shif:,.2f}"],
            ['Total Deductions', f"{total_deductions:,.2f}"]
        ]
        deductions_table = Table(deductions_data, colWidths=[col1, col2])
        deductions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f7f7f8")]),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#efefef")),
            ("LINEABOVE", (0, -1), (-1, -1), 0.4, colors.grey),
        ]))
        # story.append(Paragraph("DEDUCTIONS", styles['Heading3']))
        story.append(deductions_table)
        story.append(Spacer(1, 6))

        # Net Pay
        net_data = [
            ['Net Pay', f"{payroll.net_pay:,.2f}"]
        ]
        net_table = Table(net_data, colWidths=[col1, col2])
        net_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10.5),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#efefef")),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(net_table)
        story.append(Spacer(1, 6))

        # Footer
        footer = Paragraph(
            "This is a computer-generated payslip. No signature required. | "
            "For queries contact HR Department.",
            footer_style
        )
        story.append(footer)

        # Build PDF
        logger.debug("Building PDF...")
        doc.build(story)
        buffer.seek(0)
        logger.debug("PDF generated successfully")
        return buffer

    except Exception as e:
        logger.error(f"Failed to generate PDF: {str(e)}", exc_info=True)
        raise Exception(f"PDF generation failed: {str(e)}")