from jinja2 import Template
import logging
import ssl
import smtplib
from scan_monitor import config


class Notification:
    template_file = 'notification.j2'


class SMTP(Notification):

    def __init__(self, instance_meta, template_file=None):
        logging.info(f'instance_data: {instance_meta}')
        self.server = config.smtp_server
        self.port = config.smtp_port
        self.from_address = config.smtp_from
        self.smtp_secret = config.smtp_secret

        self.to_address = instance_meta['smtp_notification']['to']
        self.subject_template = instance_meta['smtp_notification'].get('subject')
        self.template = config.jinja_env.get_template(template_file or self.template_file)
        self.instance_meta = instance_meta

    @property
    def message_subject(self):
        logging.info('getting subject')
        if self.subject_template:
            subject = Template(self.subject_template).render(**self.instance_meta)
        else:
            subject = '{name} :: {status}'.format(**self.instance_meta)
        logging.info(f'Subject: {subject}')
        return f'Subject: {subject}'

    @property
    def message_body(self):
        logging.info('getting body')
        body = self.template.render(**self.instance_meta)
        logging.info(body)
        return body

    def send(self):
        message = '\n\n'.join([self.message_subject, self.message_body])

        logging.info("SENDING")

        if self.port == 25:
            logging.info("SENDING PORT 25")
            with smtplib.SMTP(self.server, self.port) as server:
                server.sendmail(self.from_address, self.to_address, message)
        else:
            logging.info("SENDING SSL")
            # Create a secure SSL context
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
                if getattr(self, 'smtp_secret'):
                    server.login(self.from_address, self.smtp_secret)
                server.sendmail(self.from_address, self.to_address, message)

        logging.info('NOTIFY SMTP: {name} :: {status}'.format(**self.instance_meta))
        logging.info(message)


