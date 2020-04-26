import logging
import logging.handlers
import os
import settings
from datetime import datetime
from pathlib import Path

def get_logfile_path():
    parent_dir = os.path.join(".", settings.LOG_DIR)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)
    logfile_path = os.path.join(parent_dir, settings.LOG_NAME)
    return logfile_path


def get_logger(modname,loglevel=logging.DEBUG):
    logger = logging.getLogger(modname)
    if loglevel is None:
        logger.addHandler(logging.NullHandler())
        return logger
    logger.setLevel(loglevel)
    # create a handler for showing info
    str_handler = logging.StreamHandler()
    formatter  = LogFormatter()
    str_handler.setFormatter(formatter)
    str_handler.setLevel(loglevel) 
    logger.addHandler(str_handler)
    # create a handler for recording log file
    file_handler = logging.handlers.RotatingFileHandler(
        filename=get_logfile_path(),
        encoding='utf-8', maxBytes=100000, backupCount=2)
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(LogFormatter())
    logger.addHandler(file_handler)
    return logger


class LogFormatter(logging.Formatter):

    def format(self, record):
        timestamp = (
            datetime.fromtimestamp(record.created)).strftime("%Y/%m/%d %H:%M:%S")
        filename = (record.filename).ljust(15)
        module = (record.module).ljust(15)
        lineno = str(record.lineno).rjust(4)
        level = (record.levelname).ljust(6)
        message = record.getMessage()
        
        return '{} - {} - {} :{} - {} -  {}'.format(
            timestamp, filename, module, lineno, level, message)
