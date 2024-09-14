import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import copy


class Mailer:
    def __init__(self, sender: str, password: str):
        self.sender = sender
        self.password = password
        self.context = ssl.create_default_context()
    
    def make_attachment(self, file_name):

        with open(file_name, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}"
        )

        return part

    def create_mail(self, subject: str, body: str, attachments: list[str]):
        message = MIMEMultipart()
        message["From"] = self.sender
        message["Subject"] = subject
        body = MIMEText(body,"plain")
        message.attach(body)

        for attachment in attachments:
            message.attach(self.make_attachment(attachment))

        return message

    def send_mails(self, message_base: MIMEMultipart, recipients: list[str], verbose = False): 
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=self.context) as server:
            server.login(self.sender, self.password)

            for recipient in recipients:
                message = copy.deepcopy(message_base)
                message["To"] = recipient
                server.sendmail(self.sender, recipient, message.as_string())
                if verbose:
                    print(f"Mail sent to {recipient}")


# mailer = Mailer("vignesh1234can@gmail.com","wrjm cscm rlxa dvdn")
# message = mailer.create_mail("This is a test mail","Hi,\nYou can find your document attached below.",["Vignesh E.pdf","template.pdf"])
# mailer.send_mails(message, ["vignesh1234can@gmail.com", "seenlordvins@gmail.com"],verbose=True)
    