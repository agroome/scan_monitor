from jinja2 import Template
import logging
import ssl
import smtplib
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
        message = '\n\n'.join([self.subject, self.body])
        logging.info(f'sending: {message}')
        try:
            if self.port == 25:
                with smtplib.SMTP(self.server, self.port) as server:
                    server.sendmail(self.from_address, self.to_address, message)
            else:
                # Create a secure SSL context
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
                    if getattr(self, 'smtp_secret'):
                        server.login(self.from_address, self.smtp_secret)
                    server.sendmail(self.from_address, self.to_address, message)
        except Exception as e:
            logging.error(e)



