import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailSender:
    def __init__(self, username, password, smtp_host='smtp.189.cn', smtp_port=465, **kwargs):
        self.username = username
        self.password = password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_mail = kwargs.get('sender_mail', username)
        # Create secure connection with server and send email
        self.context = ssl.create_default_context()

    def send(self, receiver_email, subject, content, **kwargs):
        message = MIMEMultipart("alternative")
        message['Subject'] = subject
        message['From'] = self.username
        message['To'] = receiver_email
        subtype = 'html' if kwargs.get('html', False) else 'plain'
        payload = MIMEText(content, subtype)
        message.attach(payload)

        with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=self.context) as server:
            server.login(self.username, self.password)
            server.sendmail(
                self.username, receiver_email, message.as_string()
            )
