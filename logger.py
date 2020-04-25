import logging
import logging.handlers
import os
from datetime import datetime

def get_logfile_path():
    if   os.name == "posix": log_path = "log/"
    elif os.name == "nt"   : log_path = ".\\log\\"
    log_file = "test.txt"
    filepath = log_path + log_file
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return filepath


def get_logger(modname,loglevel=logging.DEBUG):
    logger = logging.getLogger(modname)
    if loglevel is None:
        logger.addHandler(logging.NullHandler())
        return logger
    logger.setLevel(loglevel)
    # create handler1 for showing info
    str_handler = logging.StreamHandler()
    formatter  = LogFormatter()
    str_handler.setFormatter(formatter)

    str_handler.setLevel(loglevel) 
    logger.addHandler(str_handler)
    # create handler2 for recording log file
    file_handler = logging.handlers.RotatingFileHandler(
        filename=get_logfile_path(), encoding='utf-8', 
        maxBytes=100000, backupCount=0)
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(LogFormatter())
    logger.addHandler(file_handler)
    return logger


class LogFormatter(logging.Formatter):

    def format(self, record):
        timestamp = (
            datetime.fromtimestamp(record.created)).strftime("%Y/%m/%d %H:%M:%S")
        module = (record.module).ljust(15)
        lineno = str(record.lineno).rjust(4)
        message = record.getMessage()
        
        return '[{}]  {}  ({})  {}'.format(
            timestamp, module, lineno, message)
