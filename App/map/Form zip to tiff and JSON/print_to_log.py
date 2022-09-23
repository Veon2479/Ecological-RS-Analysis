### logging ### logging ### logging ### logging 
import config
import logging
from pathlib import Path

# import coloredlogs
# coloredlogs.install()

""" 
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(message)s"
    #file_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


    FORMATS = {
        logging.DEBUG: grey + format + reset,
        #logging.INFO: yellow + format + reset,
        logging.INFO: yellow + "%(asctime)s " + bold_red + "%(name)s " + reset + grey + "\n%(message)s" + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
"""
def get_logger(name):
    
    # Make Dir If Not Exists
    Path(config.resultTiff).mkdir(parents=True, exist_ok=True)
    _log_file   = config.resultTiff + "/logfile.log"

    file_handler = logging.FileHandler(_log_file)
    file_handler.setLevel(logging.INFO)

    file_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(threadName)s - %(message)s"
    file_handler.setFormatter(logging.Formatter(file_log_format))

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    str_log_format = "\x1b[0;32m%(asctime)s \x1b[1;31m %(name)s \x1b[0;33m(%(filename)s).%(funcName)s(%(lineno)d) \x1b[0;34m%(threadName)s\n" + "\x1b[0;37m%(message)s\x1b[0;37m" # powershell coloring
    #str_log_format = "%(message)s" #simple
    stream_handler.setFormatter(logging.Formatter(str_log_format))
    #stream_handler.setFormatter(CustomFormatter())
    logger.addHandler(stream_handler)

    return logger
