import re
from configparser import ConfigParser, MissingSectionHeaderError
from .config import Config

# delimiter that separates the description from the meta data
delimiter_pattern = re.compile(Config.meta_delimiter)
email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')


def send_notification(state_info):
    """ Send email notification. """
    smtp_server = cfg.smtp_server
    smtp_port = cfg.smtp_port
    from_addr = cfg.from_address
    to_addr = ', '.join(state_info['email'])
    text = f'Subject: {state_info["name"]} :: {state_info["status"]}\n\n{state_info["description"]}'
    logger.info(f'NOTIFY: {state_info["name"]} :: {state_info["status"]}')
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.sendmail(from_addr, to_addr, text)
            server.quit()
    except Exception as e:
        logger.warning(f'SMTP Server [{smtp_server}:{smtp_port}]: {e}.')
        pass


def extract_scan_meta(scan):
    """ Parse an item from the list of scan instances. Return meta-data if found in the scan description. """
    config_parser = ConfigParser(allow_no_value=True)
    notification_meta = dict()

    meta_format_msg = "Expecting:\n[notifications]\nemail: name@example.com, user@xample.com\n"

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
                logger.warning(f'{scan["name"]}: missing email label in scan definition meta data . {meta_format_msg}')

        except MissingSectionHeaderError:
            print(f'{scan["name"]}: missing meta data header in scan definition. {meta_format_msg}')

    return notification_meta


