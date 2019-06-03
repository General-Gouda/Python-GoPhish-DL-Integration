'''
GoPhish tool
Distribution List synchronization utility

By: Matt Marchese

Version: Beta - 2019.06.03
'''

import os
import sys
import logging
import GoPhish_DL_Integration
from GoPhish_DL_Integration import Configuration
from time import sleep

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

    config = Configuration()
    log_location = config.Log_Location
    log_file_name = "Gophish_DL_Integration.log"

    if not os.path.exists(log_location):
        os.mkdir(log_location)

    if not os.path.isfile(os.path.join(log_location, log_file_name)):
        open(os.path.join(log_location, log_file_name), 'a').close()

    # Logging Setup
        # Log Levels for reference:
        #     CRITICAL = 50
        #     FATAL = CRITICAL
        #     ERROR = 40
        #     WARNING = 30
        #     WARN = WARNING
        #     INFO = 20
        #     DEBUG = 10
        #     NOTSET = 0

    logging.basicConfig(
        format='[ %(asctime)s | %(levelname)s ] %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        filename=os.path.join(
            log_location,
            log_file_name
        ),
        level=config.Log_Level
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Log initialized.")

    while True:
        GoPhish_DL_Integration.main()
        sleep(86400)

