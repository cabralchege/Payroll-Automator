from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_payslip_pdf(employee, payroll):
    """Generate professional PDF payslip with enhanced error handling."""
    try:
        logger.debug(f"Generating payslip for employee {employee.id}, period {payroll.period}")
        
        # Initialize BytesIO buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceBefore=12,
            textColor=colors.grey
        )

        # Content
        story = []

        # Header
        story.append(Paragraph("KENYAN PAYROLL SYSTEM", title_style))
        story.append(Paragraph(f"EMPLOYEE PAYSLIP - {payroll.period}", styles['Heading2']))
        story.append(Spacer(1, 12))

        # Employee Details Table
        emp_data = [
            ['Employee ID:', employee.id or 'N/A'],
            ['KRA PIN:', employee.kra_pin or 'N/A'],
            ['Name:', employee.full_name() or 'Unknown'],
            ['Period:', payroll.period or 'N/A'],
            ['Generated:', datetime.now().strftime('%d/%m/%Y')]
        ]
        emp_table = Table(emp_data, colWidths=[3*cm, 11*cm])
        emp_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 12))

        # Earnings Table
        benefits_total = payroll.gross_salary - employee.basic_salary
        earnings_data = [
            ['DESCRIPTION', 'AMOUNT (KSh)'],
            ['Basic Salary', f"{employee.basic_salary:,.2f}"],
            ['Total Benefits', f"{benefits_total:,.2f}"],
            ['GROSS SALARY', f"{payroll.gross_salary:,.2f}"]
        ]
        earnings_table = Table(earnings_data, colWidths=[8*cm, 6*cm])
        earnings_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige)
        ]))
        story.append(Paragraph("EARNINGS", styles['Heading3']))
        story.append(earnings_table)
        story.append(Spacer(1, 12))

        # Deductions Table
        total_deductions = payroll.nssf + payroll.ahl + payroll.paye + payroll.shif
        deductions_data = [
            ['DEDUCTION', 'AMOUNT (KSh)'],
            ['NSSF', f"{payroll.nssf:,.2f}"],
            ['AHL (Housing Levy)', f"{payroll.ahl:,.2f}"],
            ['PAYE (Income Tax)', f"{payroll.paye:,.2f}"],
            ['SHIF', f"{payroll.shif:,.2f}"],
            ['TOTAL DEDUCTIONS', f"{total_deductions:,.2f}"]
        ]
        deductions_table = Table(deductions_data, colWidths=[8*cm, 6*cm])
        deductions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightcoral)
        ]))
        story.append(Paragraph("DEDUCTIONS", styles['Heading3']))
        story.append(deductions_table)
        story.append(Spacer(1, 12))

        # Net Pay
        net_data = [
            ['NET PAY', f"{payroll.net_pay:,.2f}"]
        ]
        net_table = Table(net_data, colWidths=[8*cm, 6*cm])
        net_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen)
        ]))
        story.append(net_table)
        story.append(Spacer(1, 24))

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