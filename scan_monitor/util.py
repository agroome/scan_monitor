import logging
import re
from configparser import ConfigParser, MissingSectionHeaderError
from scan_monitor import config
from jinja2 import Template

template = config.jinja_env.get_template('notification.j2')

email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')
EMAIL_SECTION = 'email notification'


def extract_cfg(record, field, delimiter_regex, repair_record=True):
    # regex that separates the body of the field from the appended 'config'
    regex_str = f'(?P<{field}>.*){delimiter_regex}(?P<config>.*)'

    logging.info('extracting cfg')
    partitions = re.search(regex_str, record.get(field, ''), re.DOTALL)
    if partitions and repair_record:
        record[field] = partitions.groupdict(field)
        logging.warning(f'record[field] = {record[field]}')

    config_str = partitions and partitions['config'].strip()
    logging.warning(f'CONFIG string= {config_str}')
    config_parser = ConfigParser(allow_no_value=True)
    try:
        logging.warning(f'config_parser read string')
        config_parser.read_string(config_str)
        cfg = config_parser
    except Exception as e:
        logging.warning(e)
        cfg = None

    return cfg


def parse_scan_instance(scan):
    """ Parse a scan instance. Inject smtp_notification if found in the scan description. """

    logging.info('parsing instance')
    cfg = extract_cfg(scan, field='description', delimiter_regex=config.field_delimiter_regex)
    logging.warning(f'cfg: {cfg}')
    if cfg and EMAIL_SECTION in cfg:
        to_value = cfg[EMAIL_SECTION].get('to')
        addresses = to_value and re.findall(email_pattern, to_value)
        logging.info(f'to: {addresses}')
        if addresses:
            scan['smtp_notification'] = dict(to_address=','.join(addresses))
            subject_template = cfg[EMAIL_SECTION].get('subject')
            if subject_template:
                scan['smtp_notification']['subject'] = Template(subject_template).render(**scan)
                logging.info(f'subject: {subject_template}')
        else:
            logging.warning('%s: not able to parse [%s] field="to".', scan["name"], EMAIL_SECTION)
    else:
        logging.error('%s: missing [%s] section in scan definition suffix. %s', EMAIL_SECTION, scan["name"])

    return scan

