import click
import os
from scan_monitor import env_file
from dotenv import load_dotenv

load_dotenv(env_file)


@click.command()
@click.option(
    '--tsc-server',
    prompt='Tenable.sc server',
    help='Tenable.sc hostname or IP address',
    default=lambda: os.environ.get('TSC_SERVER'))
@click.option(
    '--tsc-port',
    prompt='Tenable.sc port',
    help='Tenable.sc port',
    default=lambda: int(os.environ.get('TSC_PORT', 443)))
@click.option(
    '--poll-interval',
    prompt='Poll interval',
    help='Interval (in seconds) to poll Tenable.sc for scan status',
    default=lambda: int(os.environ.get('POLL_INTERVAL', 15)))
@click.option(
    '--access-key',
    help='Tenable.sc access key',
    prompt='Access key',
    default=lambda: os.environ.get('ACCESS_KEY'))
@click.option(
    '--secret-key',
    help='Tenable.sc secret key',
    prompt='Secret key',
    default=lambda: os.environ.get('SECRET_KEY'))
@click.option(
    '--smtp-server',
    help='SMTP hostname or IP address for sending email notifications',
    prompt='SMTP server',
    default=lambda: os.environ.get('SMTP_SERVER'))
@click.option(
    '--smtp-port',
    help='SMTP port',
    prompt='SMTP port',
    default=lambda: int(os.environ.get('SMTP_PORT', 25)))
@click.option(
    '--smtp-from',
    help='SMTP from address',
    prompt='From address',
    default=lambda: os.environ.get('SMTP_FROM'))
# @click.option('--smtp-password', is_flag=True, help='This flag generates a prompt for your SMTP password')
def configure(tsc_server, tsc_port, poll_interval, access_key, secret_key, smtp_server, smtp_port, smtp_from):
    """Gather configuration parameters and write them to the APP_DIR/.env file."""

    cfg = dict(
        tsc_server=tsc_server, tsc_port=tsc_port, poll_interval=poll_interval,
        access_key=access_key, secret_key=secret_key,
        smtp_server=smtp_server, smtp_port=smtp_port, smtp_from=smtp_from)

    with open(env_file, 'w') as f:
        f.writelines([f'{k.upper()}={v}\n' for k, v in cfg.items()])


if __name__ == '__main__':
    configure()
