import pandas as pd
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


def export_to_excel(df, filename):
    """
    Export the given DataFrame to an Excel file.
    """
    try:
        df.to_excel(filename, index=False)
        logger.info(f"Data exported to Excel file: {filename}")
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")

def export_to_pdf(df, filename):
    """
    Export the given DataFrame to a PDF file using reportlab.
    This is a basic implementation that writes the DataFrame text to a PDF.
    """
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        text = c.beginText(40, height - 40)
        text.setFont("Helvetica", 10)
        # Convert DataFrame to string lines
        lines = df.to_string(index=False).split('\n')
        for line in lines:
            text.textLine(line)
        c.drawText(text)
        c.save()
        logger.info(f"Data exported to PDF file: {filename}")
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")