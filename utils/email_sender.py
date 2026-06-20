import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml


class EmailSender:

    def __init__(self, config):

        self.smtp_server = config["smtp_server"]
        self.smtp_port = config["smtp_port"]

        self.username = config["username"]
        self.password = config["password"]

        self.sender = config["sender"]
        self.recipient = config["recipient"]

    def send(self, subject, body):

        msg = MIMEMultipart()

        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg["Subject"] = subject

        msg.attach(
            MIMEText(body, "plain")
        )

        with smtplib.SMTP(
            self.smtp_server,
            self.smtp_port
        ) as server:

            server.starttls()

            server.login(
                self.username,
                self.password
            )

            server.send_message(msg)

