import os
from pathlib import Path  
from dotenv import load_dotenv

env_path = Path('.') / '.app_env'
load_dotenv(dotenv_path=env_path)

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

