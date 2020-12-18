from jinja2 import Template
import logging
import ssl
import smtplib
from email.message import EmailMessage
from scan_monitor import config


class SMTP:
    """Class that will send an SMTP email. """

    def __init__(self, notification, template_file=config.default_template):
        self.server = config.smtp_server
        self.port = config.smtp_port
        self.from_address = config.smtp_from
        self.smtp_secret = config.smtp_secret

        self.to_address = notification['smtp_notification']['to_address']
        self.subject_template = notification['smtp_notification'].get('subject')
        self.template = config.jinja_env.get_template(template_file)
        self.notification = notification

    @property
    def subject(self):
        if self.subject_template:
            subject = Template(self.subject_template).render(**self.notification)
        else:
            subject = '{name} :: {status}'.format(**self.notification)
        return f'Subject: {subject}'

    @property
    def body(self):
        body = self.template.render(**self.notification)
        return body

    def send(self):
        try:
            msg = EmailMessage()
            msg.set_content(self.body)
            msg['Subject'] = self.subject
            msg['From'] = self.from_address
            msg['To'] = self.to_address

            if self.port == 25:
                logging.info(f'sending: {self.body}')
                with smtplib.SMTP(self.server) as s:
                    s.send_message(msg)
            else:
                # Create a secure SSL context
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.server, self.port, context=context) as s:
                    if getattr(self, 'smtp_secret'):
                        s.login(self.from_address, self.smtp_secret)
                    s.send_message(msg)
        except Exception as e:
            logging.error(e)



