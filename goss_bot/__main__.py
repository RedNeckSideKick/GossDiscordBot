# goss_bot __main__.py

import os
import logging
from datetime import datetime

from .config import config, secret

from .src.goss_bot import GossBot

# Logging information
LOGGING_DIR = "logs"

def main():
    # Get directory for locating needed files and folders
    _dir = os.path.dirname(os.path.abspath(__file__))
    _log_fname = os.path.join(_dir, LOGGING_DIR, f"log {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt")

    # Configure logging
    # TODO - Make logging levels for stdout and logfiles command line params
    # logging.basicConfig(format='%(name)-16s %(levelname)-8s %(message)s', level=logging.DEBUG)
    # Define logging handlers for steam output and file output
    logstream = logging.StreamHandler()
    logstream.setLevel(logging.WARN)
    # Create a basic format for stream logging and apply it
    stream_formatter = logging.Formatter('%(name)-16s %(levelname)-8s %(message)s')
    logstream.setFormatter(stream_formatter)

    os.makedirs(os.path.dirname(_log_fname), exist_ok=True) # Create logging directory if it doesn't exist
    logfile = logging.FileHandler(filename=_log_fname)
    logfile.setLevel(logging.INFO)
    # Create a format with the time for the file logging and apply it
    file_formatter = logging.Formatter('[%(asctime)s] %(name)-16s %(levelname)-8s %(message)s')
    logfile.setFormatter(file_formatter)
    
    # Add the handlers to the root logger
    logging.getLogger('').addHandler(logstream)
    logging.getLogger('').addHandler(logfile)
    logging.debug("Logging configured")

    # Create bot and run
    bot = GossBot(path=_dir)
    # TODO - Add means to specify timed bot shutdown or  recieve signal from outside
    exit_code = bot.run()
    logging.info(f"Bot exited with result {exit_code}")

# Main script execution
if __name__ == "__main__":
    main()