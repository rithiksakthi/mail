from PyPDF2 import PdfWriter, PdfReader, Transformation
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from mail import Mailer as Mail
import pandas as pd
import io, csv, os
from dotenv import load_dotenv

load_dotenv()


# Global Constants
FONT_FILE = "amazon-ember-cufonfonts/Amazon Ember V2 Bold.ttf"
CERT_DIR = "certs"
DEFAULT_FONT = "AmazonAmber"
PDF_PAGE_SIZE = letter

MAIL_SENDER = ""
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

CSV_FILE_PATH=""
CERTIFICATE_TEMPLATE = ""
CENTER_POINT = (417, 326)

MAIL_SUBJECT = "Claim your certificate and Watch the recorded sessions of AWS Cloud Club Student Community Day'24"
MAIL_CONTENT = """
Dear Sir/Madam,

We hope this email finds you well. We are thrilled to extend our warmest congratulations to you for your participation in the recent AWS Cloud Club Student Community Day (AWS Academia Industry Tech Conference) hosted at St Joseph's Group of Institutions...

Best regards,
AWS Cloud Club - St. Joseph's Group of Institutions
"""


pdfmetrics.registerFont(TTFont(DEFAULT_FONT, FONT_FILE))


class PDFGenerator:
    """Class to handle generation and merging of text into PDF template."""

    def __init__(self, template_file):
        self.template_pdf = PdfReader(open(template_file, "rb"))
        self.template_page = self.template_pdf.pages[0]
        self.packet = io.BytesIO()
        self.canvas = Canvas(self.packet, pagesize=PDF_PAGE_SIZE)

    def add_text(self, text, position, font_size=12, font_style="Helvetica", font_color=(0.62, 0.54, 0.40)):
        """Adds text to the PDF."""
        self.canvas.setFont(font_style, font_size)
        self.canvas.setFillColorRGB(*font_color)
        self.canvas.drawCentredString(position[0], position[1], text)

    def merge(self):
        """Merges the generated content onto the PDF template."""
        self.canvas.save()
        self.packet.seek(0)
        overlay_pdf = PdfReader(self.packet)
        overlay_page = overlay_pdf.pages[0]


        transformation = Transformation().rotate(0).translate(tx=0, ty=0)
        overlay_page.add_transformation(transformation)
        self.template_page.merge_page(overlay_page)


        self.output = PdfWriter()
        self.output.add_page(self.template_page)

    def save(self, output_file):
        """Saves the generated PDF to a file."""
        with open(output_file, "wb") as file:
            self.output.write(file)
        return output_file


def convert_text_to_pdf(input_pdf, output_pdf, font=DEFAULT_FONT, font_size=12):
    """Convert text in an existing PDF to a new PDF using a custom font."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()

     
        packet = io.BytesIO()
        canvas = Canvas(packet, pagesize=PDF_PAGE_SIZE)
        canvas.setFont(font, font_size)
        text_object = canvas.beginText()
        text_object.setTextOrigin(inch, 10.5 * inch)

        for line in text.split('\n'):
            text_object.textLine(line)

        canvas.drawText(text_object)
        canvas.showPage()
        canvas.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]

        writer.add_page(new_page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)


def ensure_cert_directory_exists():
    """Ensure that the certificate directory exists."""
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)


def send_certificates(cert_template, names, emails, center_point):
    """Generates and sends certificates to a list of people."""
    ensure_cert_directory_exists()
    mailer = Mail(sender=MAIL_SENDER, password=MAIL_PASSWORD)

    for name, email in zip(names, emails):
        if name:
            name = name.title()
            print(f"Generating certificate for {name} ({email})")

            generator = PDFGenerator(cert_template)
            generator.add_text(name, center_point, font_size=31, font_style=DEFAULT_FONT)
            generator.merge()

            cert_path = generator.save(f"{CERT_DIR}/{name}-{cert_template}")

            if email:
                message = mailer.create_mail(MAIL_SUBJECT, MAIL_CONTENT, [cert_path])
                mailer.send_mails(message, [email], verbose=True)
        else:
            print(f"Invalid name found: {name}")


def read_csv_data(csv_file):
    """Reads names and emails from a CSV file."""
    df = pd.read_csv(csv_file)
    names = df['name'].tolist()
    emails = df['email'].tolist()
    return names, emails



if __name__ == "__main__":
    # input_pdf = "/home/saru/Downloads/Organizer2.pdf"
    # output_pdf = "output_amazon_ember.pdf"
    # convert_text_to_pdf(input_pdf, output_pdf)


    names, emails = read_csv_data(CSV_FILE_PATH)
    
    send_certificates(CERTIFICATE_TEMPLATE, names, emails, CENTER_POINT)
