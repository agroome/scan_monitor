import json
import logging
import time
from tenable.sc import TenableSC
from scan_monitor import config
from scan_monitor.util import parse_scan_instance
from scan_monitor.notify import SMTP

template = config.jinja_env.get_template('notification.j2')

try:
    tsc = TenableSC(
        host=config.sc_host, port=config.sc_port, access_key=config.access_key, secret_key=config.secret_key
    )
except Exception as e:
    logging.error(e)
    exit(1)

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


class StateTable:
    filename = config.state_file

    def __init__(self, filename=None):
        if filename is not None:
            self.filename = filename

    def read(self):
        try:
            with open(self.filename) as f:
                state = json.load(f)
        except FileNotFoundError:
            state = None
        except Exception as e:
            logging.error(e)
        return state

    def write(self, state):
        try:
            with open(self.filename, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logging.error(e)


def process_instances(scan_instances, saved_state=None):
    # create a lookup by id, we will refer to this later for instances that are no longer running
    instance_lookup = {instance['id']: instance for instance in scan_instances}

    # initialize state with any active instances (running or paused)
    running_instances = {i: instance for i, instance in instance_lookup.items() if instance['running'] == 'true'}

    if saved_state is not None:
        # review instances in saved_state for status changes
        for instance_id, saved_instance in saved_state.items():
            instance = running_instances.get(instance_id)
            if instance is None:  # no longer listed or outside of filtered range
                # check completion status in all instances
                instance = instance_lookup.get(instance_id)
                if instance is None:  # likely deleted
                    logging.debug(f'item {instance_id} not listed: CONTINUE to next')
                    continue
                # no longer running
                logging.debug('instance no longer running')

            if instance['status'] != saved_instance['status'] and instance['status'] in notification_states:
                logging.debug(f'{instance_id} IS ELIGIBLE {saved_instance["status"]} ==> {instance["status"]}')
                instance = parse_scan_instance(instance)
                if 'smtp_notification' in instance:
                    logging.debug('INSTANCE HAS SMTP_NOTIFICATION')
                    smtp = SMTP(instance)
                    smtp.send()
                else:
                    logging.error(f'{instance["name"]} NO to_address in notification data')
            else:
                logging.debug(f'{instance_id} NOT ELIGIBLE {saved_instance["status"]} ==> {instance["status"]}')

        # next send notifications for new instances that are not yet in saved_state
        for instance_id in set(running_instances) - set(saved_state):
            instance = running_instances[instance_id]
            logging.debug(f'processing new instance status: {instance["status"]}')
            if instance['status'] in notification_states:
                instance = parse_scan_instance(instance)
                if 'smtp_notification' in instance:
                    logging.debug('INSTANCE HAS SMTP_NOTIFICATION')
                    # first time we have seen this one, save the state and notify
                    smtp = SMTP(instance)
                    smtp.send()

    return running_instances


def poll_active_scans(state=StateTable()):
    try:
        scan_instances = tsc.scan_instances.list(fields=request_fields)['usable']
        state.write(process_instances(scan_instances, state.read()))
    except Exception as e:
        logging.error(e)


def start_monitor(poll_interval=config.poll_interval):
    """ start_monitor will run a continuous loop that polls the server every 'poll_interval'. """

    state = StateTable()
    while True:
        poll_active_scans(state)
        time.sleep(poll_interval)
