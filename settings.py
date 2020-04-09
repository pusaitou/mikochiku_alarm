import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CHID = os.environ.get("CHANNEL_ID")
ICON = os.environ.get("ICON_PATH")
ALARM = os.environ.get("ALARM_PATH")
