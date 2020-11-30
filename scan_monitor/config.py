"""
config precedence:
    highest to lowest: config.json, environment variables, .env file values
"""
import json
import logging
import os
from dotenv import load_dotenv

APP_DIR = '/opt/scan_monitor'

# app_dir = os.path.dirname(__file__)
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

    def __init__(self, json_config=json_file):
        logging.debug(f'opening {json_config}')
        with open(json_config) as f:
            config = json.load(f)
            logging.debug(str(config))
            self.access_key = config.get('access_key', self.access_key)
            self.secret_key = config.get('secret_key', self.secret_key)
            self.sc_host = config.get('sc_host', self.sc_host)
            self.sc_port = int(config.get('sc_port', self.sc_port))
            self.poll_interval = int(config.get('poll_interval', self.poll_interval))
            self.meta_delimiter = config.get('meta_delimiter', self.meta_delimiter)
            self.smtp_server = config.get('smtp_server', self.smtp_server)
            self.smtp_port = int(config.get('smtp_port', self.smtp_port))
            self.from_address = config.get('from_address', self.smtp_server)


