import os
from pathlib import Path  
from dotenv import load_dotenv

env_path = Path('.') / '.pyenv'
load_dotenv(dotenv_path=env_path)


class Config:
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    sc_host = os.getenv('SC_HOST')
    sc_port = os.getenv('SC_PORT') and int(os.getenv('SC_PORT')) or 443
    poll_interval = os.getenv('POLL_INTERVAL') and int(os.getenv('POLL_INTERVAL')) or 5
    meta_delimiter = os.getenv('META_DELIMITER') or '---+ do not delete this line .*'
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_server = int(os.getenv('SMTP_PORT')) or os.getenv('SMTP_PORT') or 25
