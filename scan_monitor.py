import re
import smtplib
import time
from config import Config
from configparser import ConfigParser, MissingSectionHeaderError
from tenable.sc import TenableSC

meta_pattern = re.compile(Config.meta_delimiter)
email_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+')

end_states = ['Completed', 'Partial']
intermediate_states = ['Initializing Scanners', 'Pausing', 'Stopping']


def process_scan_meta(scan):
    config_parser = ConfigParser(allow_no_value=True)
    notification_meta = dict()

    expected_format_msg = "Expecting:\n[notifications]\nemail: name@example.com, user@xample.com\n"

    # check for meta data in the description
    lines = scan['description'].split('\n')
    for line_number, line in enumerate(lines):
        if re.match(meta_pattern, line):
            break

    # parse lines following the meta_delimiter and add to dict
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
    print('DEBUG: send notification')
    print(f'DEBUG: {state_info}')

    smtp_server = '127.0.0.1'
    from_addr = 'from@Address.com'
    to_addr = 'to@Address.com'
    text = f'Subject: {state_info["name"]} :: {state_info["status"]}\n\n{state_info["description"]}'
    with smtplib.SMTP(smtp_server, 1025) as server:
        server.ehlo()
        server.sendmail(from_addr, to_addr, text)
        server.quit()


def status_loop():

    tsc = TenableSC(
        host=Config.sc_host,
        port=Config.sc_port,
        access_key=Config.access_key,
        secret_key=Config.secret_key)

    fields = ['id', 'name', 'description', 'status', 'scan']

    def running_or_paused(scan_instance):
        return int(scan_instance['scan']['id']) > 0

    # prime state with running or paused instances
    scan_instances = tsc.scan_instances.list(fields=fields)['usable']
    scan_meta = (process_scan_meta(scan) for scan in scan_instances if running_or_paused(scan))
    scan_instances = filter(lambda meta: 'email' in meta, scan_meta)
    state = {scan['id']: scan for scan in scan_instances}

    while True:
        # refresh state
        scan_instances = tsc.scan_instances.list(fields=fields)['usable']
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
            if new_state['status'] in intermediate_states or 'email' not in new_state:
                continue

            # report state change with email address in meta data
            if new_state['status'] != last_state['status']:
                send_notification(new_state)
                if new_state['status'] not in end_states:
                    state[instance_id] = new_state
                else:
                    del state[instance_id]

        time.sleep(Config.poll_interval)


if __name__ == '__main__':
    status_loop()


