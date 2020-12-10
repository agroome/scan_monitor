import json
import logging
import os
from tenable.sc import TenableSC
from .config import Config

from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = Environment(loader=FileSystemLoader(template_dir))
template = jinja_env.get_template('notification.j2')

logging.basicConfig(filename='notify.log', filemode='w')

cfg = Config(json_config='/Users/agroome/devel/scan_monitor/config.json')

request_fields = [
    'id', 'name', 'description', 'status', 'initiator', 'owner', 'ownerGroup',
    'repository', 'scan', 'job', 'details', 'importStatus', 'importStart', 'importFinish',
    'initiator', 'owner', 'ownerGroup', 'repository', 'scan', 'job', 'details', 'importStatus',
    'importStart', 'importFinish', 'importDuration', 'downloadAvailable', 'resultType', 'resultSource',
    'running', 'errorDetails', 'importErrorDetails', 'totalIPs', 'scannedIPs', 'startTime', 'finishTime',
    'scanDuration, completedIPs', 'completedChecks', 'totalChecks', 'agentScanUUID', 'agentScanContainerUUID',
]

app_dir = '/Users/agroome/devel/project'
notifications_yaml = f'{app_dir}/notifications.yaml'
state_file = f'{app_dir}/state.json'

notification_states = ['Running', 'Paused', 'Completed', 'Partial', 'Error']
end_states = notification_states[2:]


def read_state(filename):
    try:
        with open(filename) as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None
    return state


def write_state(filename, state):
    num = len(state)
    with open(filename, 'w') as f:
        json.dump(state, f)


def update_state(scan_instances, saved_state=None):
    # create a lookup by id
    instances = {instance['id']: instance for instance in scan_instances}
    # initialize new_state with any active instances
    new_state = {index: instance for index, instance in instances.items() if instance['running'] == 'true'}

    if saved_state is not None:
        # review each instance in saved_state for status changes
        for instance_id, saved_instance in saved_state.items():
            instance = new_state.get(instance_id)
            if instance is None:
                # no longer running
                instance = instances.get(instance_id)
                if instance is None:
                    # no longer exists
                    continue

            if instance['status'] != saved_instance['status'] and instance['status'] in notification_states:
                print(f'{saved_instance["status"]} ==> {instance["status"]}')
            if instance['status'] not in end_states:
                # keep the latest info, i.e. notification metadata
                new_state[instance_id] = instance

        # send notifications for any new items that were not in saved_state
        for instance_id in set(new_state) - set(saved_state):
            instance = new_state[instance_id]
            if instance['status'] in notification_states:
                print(f'NEW ==> {instance["status"]}')

    return new_state


def process_instances():
    try:
        tsc = TenableSC(host=cfg.sc_host, port=cfg.sc_port, access_key=cfg.access_key, secret_key=cfg.secret_key)
        scan_instances = tsc.scan_instances.list(fields=request_fields)['usable']
        new_state = update_state(scan_instances, read_state(state_file))
        write_state(state_file, new_state)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    import time
    while True:
        process_instances()
        time.sleep(15)
