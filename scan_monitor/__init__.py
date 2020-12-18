import json
import logging
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# application defaults
DEFAULT_APP_DIR = '/opt/scan_monitor'
DEFAULT_DELIMITER = '--- do not delete below this line ---'
DEFAULT_DELIMITER_REGEX = '---+ do not delete .*---'
DEFAULT_TEMPLATE = 'notification.j2'
DEFAULT_INTERVAL = 15
DEFAULT_SMTP_PORT = 25
DEFAULT_SC_PORT = 443

# application files
app_dir = Path(os.environ.get('APP_DIR', DEFAULT_APP_DIR))
logfile = app_dir / 'var' / 'log' / 'notify.log'
env_file = app_dir / '.monitor_env'
json_file = app_dir / 'etc' / 'config.json'
state_file = app_dir / 'state.json'
template_dir = app_dir / 'templates'

load_dotenv(dotenv_path=env_file)


class MissingConfig(Exception):
    pass


class Config:
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    sc_host = os.getenv('TSC_SERVER')
    sc_port = int(os.getenv('TSC_PORT', DEFAULT_SC_PORT))
    poll_interval = int(os.getenv('POLL_INTERVAL', DEFAULT_INTERVAL))
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', DEFAULT_SMTP_PORT))
    smtp_from = os.getenv('SMTP_FROM')
    smtp_secret = os.getenv('SMTP_PASSWORD')
    log_level = int(os.getenv('LOG_LEVEL', logging.WARNING))
    field_delimiter_regex = DEFAULT_DELIMITER_REGEX

    def __init__(self, json_config=None):
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.state_file = state_file
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
            self.field_delimiter = self.field_delimiter or cfg.get('field_delimiter', DEFAULT_DELIMITER_REGEX)
            self.smtp_server = self.smtp_server or cfg.get('smtp_server')
            self.smtp_port = int(self.smtp_port or cfg.get('smtp_port', DEFAULT_SMTP_PORT))
            self.smtp_from = self.smtp_from or cfg.get('smtp_from')
            self.smtp_secret = self.smtp_secret or cfg.get('smtp_secret')


config = Config()

logging.basicConfig(
    filename=logfile,
    filemode='a',
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=config.log_level)

logging.info(f'log level: {config.log_level}')

