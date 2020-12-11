import logging
import re
from configparser import ConfigParser, MissingSectionHeaderError
from scan_monitor import config

template = config.jinja_env.get_template('notification.j2')

# delimiter that separates the description from the meta data
delimiter_pattern = re.compile(config.meta_delimiter)
email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')


def extract_scan_meta(scan):
    """ Parse an item from the list of scan instances. Return meta-data if found in the scan description. """
    config_parser = ConfigParser(allow_no_value=True)
    notification_meta = dict()

    format_msg = "Expecting:\n[notifications]\nemail: name@example.com, user@xample.com\n"

    # check for meta data in the description
    lines = scan['description'].split('\n')
    for line_number, line in enumerate(lines):
        if re.match(delimiter_pattern, line):
            break

    # parse lines following the meta_delimiter. if found, create dictionary of config values
    description_lines = lines[:line_number]
    config_lines = lines[line_number + 1:]
    if config_lines:
        try:
            config_parser.read_string('\n'.join(config_lines))
            email_values_string = config_parser['notifications'].get('email')
            email_addresses = email_values_string and re.findall(email_pattern, email_values_string)
            if email_addresses:
                notification_meta = dict(
                    id=scan['id'],
                    name=scan['name'],
                    description='\n'.join(description_lines),
                    status=scan['status'],
                    email=email_addresses)
            else:
                logging.warning('%s: missing email label in scan definition meta data. %s', scan["name"], format_msg)

        except MissingSectionHeaderError:
            print('%s: missing meta data header in scan definition. %s', scan["name"], format_msg)

    return notification_meta

