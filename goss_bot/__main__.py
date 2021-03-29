# goss_bot __main__.py

import os
import logging
from datetime import datetime
from configobj import ConfigObj

from .src.goss_bot import GossBot

# Configuration file information
_CONFIG_DIR     = "config"
_CONFIG_FILE    = "config.ini"
_SECRET_FILE    = "secret.ini"

# Logging information
_LOGGING_DIR    = "logs"

# Get directory for locating needed files and folders
_dir = os.path.dirname(os.path.abspath(__file__))
_log_fname = os.path.join(_dir, _LOGGING_DIR, f"log {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt")

def main():
    # Configure logging
    os.makedirs(os.path.dirname(_log_fname), exist_ok=True) # Create logging directory if it doesn't exist
    logging.basicConfig(format='%(name)-16s %(levelname)-8s %(message)s', level=logging.INFO)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    logfile = logging.FileHandler(filename=_log_fname)
    logfile.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-16s %(levelname)-8s %(message)s')
    # tell the handler to use this format
    logfile.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(logfile)
    logging.debug("Logging configured")

    # Load in configuration files
    logging.debug("Loading configs")
    config = ConfigObj(os.path.join(_dir, _CONFIG_DIR, _CONFIG_FILE))
    secret = ConfigObj(os.path.join(_dir, _CONFIG_DIR, _SECRET_FILE))

    # Create bot and run in context manager
    bot = GossBot(config=config, secret=secret, path=_dir)
    with bot:
        logging.debug("In context manager")
        bot.run()
        logging.debug("Exiting context manager")

# Main script execution
if __name__ == "__main__":
    main()