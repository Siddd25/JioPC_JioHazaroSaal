import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
from dotenv import load_dotenv

import os

class EmailSender:

    def __init__(self, config,recipent):

        load_dotenv()

        

        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))

        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")

        self.sender = config["sender"]
        self.recipient = recipent

      


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

