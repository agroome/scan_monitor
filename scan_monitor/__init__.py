import json
import logging
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader


APP_DIR = '/opt/scan_monitor'


logfile = os.path.join(APP_DIR, 'var', 'log', 'notify.log')
logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)
logging.info('starting logging')

env_file = os.path.join(APP_DIR, '.env')
json_file = os.path.join(APP_DIR, 'etc', 'config.json')

load_dotenv(dotenv_path=env_file)

META_DELIMITER_REGEX = '---+ do not delete .*'


class Config:
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    sc_host = os.getenv('SC_HOST')
    sc_port = int(os.getenv('SC_PORT', 443))
    poll_interval = int(os.getenv('POLL_INTERVAL', 15))
    meta_delimiter = os.getenv('META_DELIMITER', META_DELIMITER_REGEX)
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 25))
    smtp_from = os.getenv('SMTP_FROM')

    def __init__(self, json_config=None):
        template_dir = os.path.join(APP_DIR, 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.state_file = os.path.join(APP_DIR, 'state.json')

        if json_config is not None:
            logging.debug(f'opening {json_config}')
            with open(json_config) as f:
                cfg = json.load(f)
            self.access_key = cfg.get('access_key', self.access_key)
            self.secret_key = cfg.get('secret_key', self.secret_key)
            self.sc_host = cfg.get('sc_host', self.sc_host)
            self.sc_port = int(cfg.get('sc_port', self.sc_port))
            self.poll_interval = int(cfg.get('poll_interval', self.poll_interval))
            self.meta_delimiter = cfg.get('meta_delimiter', self.meta_delimiter)
            self.smtp_server = cfg.get('smtp_server', self.smtp_server)
            self.smtp_port = int(cfg.get('smtp_port', self.smtp_port))
            self.smtp_from = cfg.get('smtp_from', self.smtp_from)


config = Config(json_config=json_file)



