import logging
import re
from configparser import ConfigParser, MissingSectionHeaderError
from scan_monitor import config
from jinja2 import Template

template = config.jinja_env.get_template('notification.j2')

# delimiter that separates the description from the meta data
delimiter_pattern = re.compile(config.meta_delimiter)
email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')


def parse_scan_instance(scan):
    """ Parse an item from the list of scan instances. Return meta-data if found in the scan description. """

    logging.info('parse scan instance')

    # check for meta data in the description
    lines = scan['description'].split('\n')
    for line_number, line in enumerate(lines):
        if re.match(delimiter_pattern, line):
            break

    # any lines after 'line_number' are expected to be configParser data
    config_lines = lines[line_number + 1:]
    if config_lines:
        try:
            logging.info(f'parsing config for {scan["name"]}')
            # overwrite (description + config_lines) with just the description
            # we're likely to use that in the formatted message
            # scan['description'] = '\n'.join(lines[:line_number])
            logging.info('\n'.join(config_lines))

            config_parser = ConfigParser(allow_no_value=True)
            config_parser.read_string('\n'.join(config_lines))

            logging.info('READING to: value')
            to_value = config_parser['email notification'].get('to')
            logging.info(f'to: {to_value}')

            matching_addresses = to_value and re.findall(email_pattern, to_value)
            logging.info(f'matching addresses: {matching_addresses}')
            if matching_addresses:
                logging.info(f'matching addresses: {matching_addresses}')
                scan['smtp_notification'] = dict(to=','.join(matching_addresses))
                subject_template = config_parser['email notification'].get('subject')
                if subject_template:
                    scan['smtp_notification']['subject'] = Template(subject_template).render(**scan)
            else:
                logging.warning('%s: expecting "to" field in [email notification] section. %s', scan["name"])

        except MissingSectionHeaderError:
            logging.warning('%s: missing [email notification] section in scan definition suffix. %s', scan["name"])

    return scan


