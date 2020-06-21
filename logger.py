import logging
import logging.handlers
import os
import settings
from datetime import datetime
from glob import glob
from pathlib import Path


# ログファイル名。起動時に、日時をベースとしたファイル名を設定。
log_name = ''.join(['log', datetime.now().strftime("%Y%m%d_%H%M%S"), ".txt"])


def remove_old_log(max_logfile_count=5):
    '''
    起動時にログフォルダ内に残っているログファイルを走査、
    「max_logfile_count」個以下のファイル数になるように、古いログファイルを削除する

    parameter
    ---------
    max_logfile_count : 残すログファイルの個数
    '''
    if max_logfile_count < 1:
        max_logfile_count = 1
    # ログフォルダ内のログファイル名の走査、ログファイルのファイル名は昇順ソートしておく
    baselogdir = os.path.dirname(get_logfile_path())
    logfilelist = sorted(glob(''.join([baselogdir, '/*', '.txt'])))
    current_count = len(logfilelist)
    if current_count < max_logfile_count + 1:
        return
    remove_count = current_count - max_logfile_count  # 削除する回数
    for filename in logfilelist:
        try:
            os.remove(filename)
        except Exception:
            pass
        remove_count -= 1
        if remove_count < 1:
            break


def get_logfile_path() -> str:
    '''
    ログファイルのフルパスを返す
    '''
    parent_dir = os.path.join(".", settings.LOG_DIR)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)
    logfile_path = os.path.join(parent_dir, log_name)
    return logfile_path


def get_logger(modname, loglevel=logging.DEBUG):
    logger = logging.getLogger(modname)
    if loglevel is None:
        logger.addHandler(logging.NullHandler())
        return logger
    logger.setLevel(loglevel)
    # create a handler for showing info
    str_handler = logging.StreamHandler()
    formatter = LogFormatter()
    str_handler.setFormatter(formatter)
    str_handler.setLevel(loglevel) 
    logger.addHandler(str_handler)
    # create a handler for recording log file
    file_handler = logging.FileHandler(filename=get_logfile_path(), encoding='utf-8')
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
