import logging
import re
from configparser import ConfigParser, MissingSectionHeaderError
from scan_monitor import config
from jinja2 import Template

template = config.jinja_env.get_template('notification.j2')

email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')
EMAIL_SECTION = 'email notification'


def extract_cfg(record, field, delimiter_regex, repair_record=True):
    """Extract configParser data after delimeter in field from record."""

    # regex that separates the body of the field from the appended 'config'
    regex_str = f'(?P<{field}>.*){delimiter_regex}(?P<config>.*)'

    partitions = re.search(regex_str, record.get(field, ''), re.DOTALL)
    # replace the field with the field text above the delimiter
    if partitions and repair_record:
        record[field] = partitions[field]

    config_str = partitions and partitions['config'].strip()
    config_parser = ConfigParser(allow_no_value=True)
    try:
        config_parser.read_string(config_str)
        cfg = config_parser
    except Exception as e:
        logging.warning(e)
        cfg = None

    return cfg


def parse_scan_instance(scan):
    """ Parse a scan instance. Inject smtp_notification if found in the scan description. """

    cfg = extract_cfg(scan, field='description', delimiter_regex=config.field_delimiter_regex)
    if cfg and EMAIL_SECTION in cfg:
        to_value = cfg[EMAIL_SECTION].get('to')
        addresses = to_value and re.findall(email_pattern, to_value)
        if addresses:
            logging.debug(f'found to addresses: {addresses}')
            # add to: addresses to notification info
            scan['smtp_notification'] = dict(to_address=','.join(addresses))
            subject_template = cfg[EMAIL_SECTION].get('subject')
            # add subject: addresses to notification info
            if subject_template:
                scan['smtp_notification']['subject'] = Template(subject_template).render(**scan)
        else:
            logging.warning('%s: not able to parse [%s] field="to".', scan["name"], EMAIL_SECTION)
    else:
        logging.error('%s: missing [%s] section in scan definition suffix. %s', EMAIL_SECTION, scan["name"])

    return scan

