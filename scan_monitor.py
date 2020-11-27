import logging
import re
import smtplib
import time
from config import Config
from configparser import ConfigParser, MissingSectionHeaderError
from tenable.sc import TenableSC

# delimiter that separates the description from the meta data
delimiter_pattern = re.compile(Config.meta_delimiter)
email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')

end_states = ['Completed', 'Partial', 'Error']
notification_states = ['Running', 'Paused'] + end_states

cfg = Config()

logging.basicConfig(filename='scan_monitor.log', level=logging.INFO)


def process_scan_meta(scan):
    """ Parse an item from the list of scan instances. Return meta-data if found in the scan description. """
    config_parser = ConfigParser(allow_no_value=True)
    notification_meta = dict()

    expected_format_msg = "Expecting:\n[notifications]\nemail: name@example.com, user@xample.com\n"

    # check for meta data in the description
    lines = scan['description'].split('\n')
    for line_number, line in enumerate(lines):
        if re.match(delimiter_pattern, line):
            break

    # parse lines following the meta_delimiter. if found, create dictionary of config values
    description_lines = lines[:line_number]
    config_lines = lines[line_number+1:]
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
                print(f'{scan["name"]}: missing email label in scan definition meta data . {expected_format_msg}')

        except MissingSectionHeaderError:
            print(f'{scan["name"]}: missing meta data header in scan definition. {expected_format_msg}')

    return notification_meta


def send_notification(state_info):
    """ Send email notification. """
    smtp_server = cfg.smtp_server
    smtp_port = cfg.smtp_port
    from_addr = 'from@Address.com'
    to_addr = ', '.join(state_info['email'])
    text = f'Subject: {state_info["name"]} :: {state_info["status"]}\n\n{state_info["description"]}'
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.sendmail(from_addr, to_addr, text)
            server.quit()
    except ConnectionError as e:
        logging.warning(f'Connection error: {e}.')


def polling_loop():
    logging.info('Scan monitor started')

    tsc = TenableSC(
        host=cfg.sc_host,
        port=cfg.sc_port,
        access_key=cfg.access_key,
        secret_key=cfg.secret_key)

    fields = ['id', 'name', 'description', 'status', 'scan']

    def running_or_paused(scan_instance):
        return int(scan_instance['scan']['id']) > 0

    try:
        # prime state with running or paused instances
        scan_instances = tsc.scan_instances.list(fields=fields)['usable']
    except Exception as e:
        logging.warning(f'ERROR: {e}. Tenable.sc is not reachable.')

    scan_meta = (process_scan_meta(scan) for scan in scan_instances if running_or_paused(scan))
    scan_instances = filter(lambda meta: 'email' in meta, scan_meta)
    state = {scan['id']: scan for scan in scan_instances}

    while True:
        # get a list of all scan instances, index by 'id' for processing
        try:
            scan_instances = tsc.scan_instances.list(fields=fields)['usable']
        except Exception as e:
            logging.warning(f'ERROR: {e}. Tenable.sc is not reachable.')
            continue

        instances = {s['id']: s for s in scan_instances}

        # remove saved state for any deleted scans
        assumed_deleted = set(state) - set(instances)
        for instance_id in assumed_deleted:
            del state[instance_id]

        # process any new instances
        no_saved_state = set(instances) - set(state)
        for instance_id in no_saved_state:
            instance = instances[instance_id]
            if running_or_paused(instance):
                state[instance_id] = process_scan_meta(instance)
                state[instance_id]['status'] = 'STARTING'

        # update saved state for each instance
        for instance_id, last_state in state.copy().items():

            new_state = process_scan_meta(instances.get(instance_id))
            if new_state['status'] not in notification_states or 'email' not in new_state:
                continue

            # report state change and update or delete saved state
            if new_state['status'] != last_state['status']:
                send_notification(new_state)
                if new_state['status'] not in end_states:
                    state[instance_id] = new_state
                else:
                    del state[instance_id]

        time.sleep(cfg.poll_interval)


if __name__ == '__main__':
    polling_loop()


