import json
import logging
import os
import re
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+')
EMAIL_SECTION = 'email notification'

app_dir = Path(os.getenv('APP_DIR', '/opt/scan_monitor'))
logfile = app_dir / 'var/log/notify.log'
env_file = app_dir / '.env'
json_file = app_dir / 'etc/config.json'


def update_cfg(cfg, file=json_file):
    data = dict()
    if os.path.isfile(file):
        with open(file) as f:
            data = json.load(f)

    data.update(cfg)
    with open(file, 'w') as f:
        json.dump(data, f)


logging.basicConfig(
    filename=logfile,
    filemode='a',
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %h:%M:%S',
    level=logging.WARNING)


load_dotenv(dotenv_path=env_file)

DEFAULT_DELIMITER_REGEX = '---+ do not delete .*---'
DEFAULT_TEMPLATE = 'notification.j2'

DEFAULT_INTERVAL = 15
DEFAULT_SMTP_PORT = 25
DEFAULT_SC_PORT = 443


class MissingConfig(Exception):
    pass


class Config:
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    sc_host = os.getenv('SC_HOST')
    sc_port = os.getenv('SC_PORT')
    poll_interval = os.getenv('POLL_INTERVAL')
    meta_delimiter = os.getenv('META_DELIMITER')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_from = os.getenv('SMTP_FROM')
    smtp_secret = os.getenv('SMTP_SECRET')

    def __init__(self, json_config=None):
        template_dir = os.path.join(app_dir, 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.state_file = os.path.join(app_dir, 'state.json')
        self.default_template = DEFAULT_TEMPLATE

        if json_config:
            logging.debug(f'using configuration file {json_config}')
            with open(json_config) as f:
                cfg = json.load(f)
            self.access_key = self.access_key or cfg.get('access_key')
            self.secret_key = self.secret_key or cfg.get('secret_key')
            self.sc_host = self.sc_host or cfg.get('sc_host')
            self.sc_port = int(self.sc_port or cfg.get('sc_port', DEFAULT_SC_PORT))
            self.poll_interval = int(self.poll_interval or cfg.get('poll_interval', DEFAULT_INTERVAL))
            self.meta_delimiter = self.meta_delimiter or cfg.get('meta_delimiter', DEFAULT_DELIMITER_REGEX)
            self.smtp_server = self.smtp_server or cfg.get('smtp_server')
            self.smtp_port = int(self.smtp_port or cfg.get('smtp_port', DEFAULT_SMTP_PORT))
            self.smtp_from = self.smtp_from or cfg.get('smtp_from')
            self.smtp_secret = self.smtp_secret or cfg.get('smtp_secret')


try:
    config = Config(json_config=json_file)
except FileNotFoundError as e:
    config = Config()
    if not config.access_key and config.secret_key and config.sc_host:
        logging.error('Missing Tenable.sc configuration parameters.')
        raise MissingConfig

