import argparse
import logging
import os
import sys

import django
from django.core import management

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'apps')

os.chdir(BASE_DIR)
sys.path.insert(0, APP_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartdoc.settings")
django.setup()


def collect_static():
    """
     Collect static files to the specified directory
     This project is mainly the front.vue/distThe front-end project is placed in the static directory below.
    :return:
    """
    logging.info("Collect static files")
    try:
        management.call_command('collectstatic', '--no-input', '-c', verbosity=0, interactive=False)
        logging.info("Collect static files done")
    except:
        pass


def perform_db_migrate():
    """
    Initial Database Table
    """
    logging.info("Check database structure change ...")
    logging.info("Migrate model change to database ...")
    try:
        management.call_command('migrate')
    except Exception as e:
        logging.error('Perform migrate failed, exit', exc_info=True)
        sys.exit(11)


def start_services():
    management.call_command('migrate')
    management.call_command('runserver', "0.0.0.0:8080")


if __name__ == '__main__':
    os.environ['HF_HOME'] = './'
    parser = argparse.ArgumentParser(
        description="""
           qabot service control tools;

           Example: \r\n

           %(prog)s start all -d;
           """
    )
    parser.add_argument(
        'action', type=str,
        choices=("start", "upgrade_db", "collect_static"),
        help="Action to run"
    )
    args = parser.parse_args()

    action = args.action
    if action == "upgrade_db":
        perform_db_migrate()
    elif action == "collect_static":
        collect_static()
    else:
        collect_static()
        start_services()
