import logging
import ssl
import smtplib
from scan_monitor import config


class Notification:
    template_file = 'notification.j2'


class SMTP(Notification):

    def __init__(self, notification_meta, instance_meta, template_file=None):
        logging.info(f'notification: {notification_meta}')
        logging.info(f'instance_data: {instance_meta}')
        self.server = config.smtp_server
        self.port = config.smtp_port
        self.from_address = config.smtp_from
        self.to_address = ', '.join(notification_meta['email'])
        self.template = config.jinja_env.get_template(template_file or self.template_file)
        self.instance_meta = instance_meta
        self.notification_meta = notification_meta
        self.smtp_secret = config.smtp_secret

    @property
    def message_subject(self):
        return 'Subject: {name} :: {status}'.format(**self.notification_meta)

    @property
    def message_body(self):
        return self.template.render(**self.instance_meta)

    def send_smtp(self):
        message = '\n\n'.join([self.message_subject, self.message_body])

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
            server.login(self.from_address, self.smtp_secret)
            server.sendmail(self.from_address, self.to_address, message)

        logging.info(f'NOTIFY SMTP: {self.notification_meta["name"]} :: {self.notification_meta["status"]}')
        logging.info(message)


