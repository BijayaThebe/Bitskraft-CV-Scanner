from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def write_pdf(text, output_file="result.pdf"):
    doc = SimpleDocTemplate(output_file)
    styles = getSampleStyleSheet()
    content = [Paragraph(text, styles["Normal"])]
    doc.build(content)
    return output_file
