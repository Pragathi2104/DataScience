from pathlib import Path
from tempfile import gettempdir


def build_report(analyses):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    path = Path(gettempdir()) / 'meatwise-analysis-report.pdf'
    pdf = canvas.Canvas(str(path), pagesize=letter)
    pdf.setTitle('Meatwise Analysis Report')
    pdf.setFont('Helvetica-Bold', 20)
    pdf.drawString(54, 740, 'Meatwise Analysis Report')
    pdf.setFont('Helvetica', 10)
    pdf.drawString(54, 720, f'Generated report for {len(analyses)} saved sample(s).')
    y = 680
    for item in analyses[:18]:
        pdf.drawString(54, y, f"{item['analysis_id']} | {item['meat_type']} | {item['prediction']} | {item['confidence']}% confidence")
        y -= 20
    pdf.save()
    return path