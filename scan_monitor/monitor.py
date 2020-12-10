import logging
import re
import smtplib
import time
from .config import Config
from configparser import ConfigParser, MissingSectionHeaderError
from tenable.sc import TenableSC

# delimiter that separates the description from the meta data
delimiter_pattern = re.compile(Config.meta_delimiter)
email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')

end_states = ['Completed', 'Partial', 'Error']
notification_states = ['Running', 'Paused'] + end_states

cfg = Config()

verbose = True

logger = logging.getLogger('scan_monitor')
logger.propagate = False

try:
    from systemd.journal import JournalHandler
    handler = JournalHandler()
except:
    handler = logging.StreamHandler()
    pass

handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

logger.addHandler(handler)
logger.setLevel(logging.INFO)


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


def running_or_paused(scan_instance):
    return int(scan_instance['scan']['id']) > 0


def prime_initial_state(tsc, fields):
    logger.info(f'prime initial state')
    # extract meta data from running or paused scan instances
    scan_instances = tsc.scan_instances.list(fields=fields)['usable']
    scan_meta = (extract_scan_meta(scan) for scan in scan_instances if running_or_paused(scan))

    notification_instances = filter(lambda meta: 'email' in meta, scan_meta)
    initial_state = {scan['id']: scan for scan in notification_instances}
    logger.info(f'initial state: {initial_state}')
    return initial_state


def start_monitor():
    logger.info(f'Scan monitor started for {cfg.sc_host}')
    fields = ['id', 'name', 'description', 'status', 'scan']
    try:
        tsc = TenableSC(host=cfg.sc_host, port=cfg.sc_port, access_key=cfg.access_key, secret_key=cfg.secret_key)
        state = prime_initial_state(tsc, fields)
    except Exception as e:
        logger.error(f'Tenable.sc API must be reachable during startup: {e}')
        exit(1)

    while True:
        # get a list of all scan instances, index by 'id' for processing
        try:
            tsc = TenableSC(host=cfg.sc_host, port=cfg.sc_port, access_key=cfg.access_key, secret_key=cfg.secret_key)
            scan_instances = tsc.scan_instances.list(fields=fields)['usable']
            instances = {s['id']: s for s in scan_instances}
        except Exception as e:
            logger.warning(f'Tenable.sc is not reachable: {e}')
            continue

        # remove saved state for any deleted scans
        assumed_deleted = set(state) - set(instances)
        for instance_id in assumed_deleted:
            del state[instance_id]

        # process any new instances
        no_saved_state = set(instances) - set(state)
        for instance_id in no_saved_state:
            instance = instances[instance_id]
            if running_or_paused(instance):
                state[instance_id] = extract_scan_meta(instance)
                state[instance_id]['status'] = 'STARTING'

        # update saved state for each instance
        for instance_id, last_state in state.copy().items():

            instance_meta = extract_scan_meta(instances.get(instance_id))
            if instance_meta['status'] not in notification_states or 'email' not in instance_meta:
                continue

            # report state change and update or delete saved state
            if instance_meta['status'] != last_state['status']:
                send_notification(instance_meta)
                if instance_meta['status'] not in end_states:
                    state[instance_id] = instance_meta
                else:
                    del state[instance_id]

        time.sleep(cfg.poll_interval)

# if __name__ == '__main__':
#     start_monitor()
