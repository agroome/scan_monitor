"""
config precedence:
    highest to lowest: config.json, environment variables, .env file values
"""
import json
import os
from dotenv import load_dotenv

app_dir = os.path.dirname(__file__)
env_file = os.path.join(app_dir, '.env')
json_file = os.path.join(app_dir, 'config.json')

load_dotenv(dotenv_path=env_file)

DEFAULT_META_DELIMITER = '---+ do not delete this line .*'


class Config:
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    sc_host = os.getenv('SC_HOST')
    sc_port = os.getenv('SC_PORT') and int(os.getenv('SC_PORT')) or 443
    poll_interval = os.getenv('POLL_INTERVAL') and int(os.getenv('POLL_INTERVAL')) or 5
    meta_delimiter = os.getenv('META_DELIMITER') or DEFAULT_META_DELIMITER 
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT') and int(os.getenv('SMTP_PORT')) or 25

    def __init__(self, json_config=json_file):
        with open(json_config) as f:
            config = json.load(f)
            self.access_key = config.get('access_key', self.access_key)
            self.secret_key = config.get('secret_key', self.secret_key)
            self.sc_host = config.get('sc_host', self.sc_host)
            self.sc_port = config.get('sc_port', self.sc_port)
            self.poll_interval = config.get('poll_interval', self.poll_interval)
            self.meta_delimiter = config.get('meta_delimiter', self.meta_delimiter)
            self.smtp_server = config.get('smtp_server', self.smtp_server)
            self.smtp_port = config.get('smtp_port', self.smtp_port)


if __name__ == '__main__':
    print(Config().__dict__)

