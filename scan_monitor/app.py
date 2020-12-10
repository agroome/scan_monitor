import json
import logging
import time
from tenable.sc import TenableSC
from scan_monitor import config
from scan_monitor.util import extract_scan_meta

template = config.jinja_env.get_template('notification.j2')

request_fields = [
    'id', 'name', 'description', 'status', 'initiator', 'owner', 'ownerGroup',
    'repository', 'scan', 'job', 'details', 'importStatus', 'importStart', 'importFinish',
    'initiator', 'owner', 'ownerGroup', 'repository', 'scan', 'job', 'details', 'importStatus',
    'importStart', 'importFinish', 'importDuration', 'downloadAvailable', 'resultType', 'resultSource',
    'running', 'errorDetails', 'importErrorDetails', 'totalIPs', 'scannedIPs', 'startTime', 'finishTime',
    'scanDuration, completedIPs', 'completedChecks', 'totalChecks', 'agentScanUUID', 'agentScanContainerUUID',
]

notification_states = ['Running', 'Paused', 'Completed', 'Partial', 'Error']
end_states = notification_states[2:]


def read_state_table(filename):
    try:
        with open(filename) as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None
    return state


def write_state_table(filename, state):
    with open(filename, 'w') as f:
        json.dump(state, f)


def process_instances(scan_instances, saved_state=None):
    # create a lookup by id, we will refer to this later for instances that are no longer running
    instances = {instance['id']: instance for instance in scan_instances}

    # initialize new_state with any active instances
    new_state = {index: instance for index, instance in instances.items() if instance['running'] == 'true'}

    # as long as we haven't just started, send notifications for running instances not yet in saved_state
    if saved_state is not None:
        for instance_id in set(new_state) - set(saved_state):
            instance = new_state[instance_id]
            if instance['status'] in notification_states:
                notification_meta = extract_scan_meta(instance)
                logging.info('email = %s', notification_meta.get('email', 'UNKNOWN'))
                transition = f'NEW ==> {instance["status"]}'
                logging.info(transition)

        # review instances in saved_state for status changes
        for instance_id, saved_instance in saved_state.items():
            # reference new information
            instance = instances.get(instance_id)
            if instance is None:  # no longer listed or outside of filtered range
                continue

            if instance['status'] != saved_instance['status'] and instance['status'] in notification_states:
                transition = f'{saved_instance["status"]} ==> {instance["status"]}'
                logging.info(transition)
                notification_meta = extract_scan_meta(instance)
                logging.info('email = %s', notification_meta.get('email', 'UNKNOWN'))

            # maintain state with the latest meta data
            if instance['status'] not in end_states:
                new_state[instance_id] = instance

    return new_state


def poll_scan_instances():
    try:
        tsc = TenableSC(
            host=config.sc_host,
            port=config.sc_port,
            access_key=config.access_key,
            secret_key=config.secret_key
        )
        scan_instances = tsc.scan_instances.list(fields=request_fields)['usable']

        saved_state = read_state_table(config.state_file)
        new_state = process_instances(scan_instances, saved_state)
        write_state_table(config.state_file, new_state)

    except Exception as e:
        logging.error(e)


def start_monitor():
    while True:
        poll_scan_instances()
        time.sleep(15)
