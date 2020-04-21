import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/69.0.3497.100 Safari/537.36'}

class HttpRequest:

    def __init__(self):
        self.session = requests.Session()
        self.retries = Retry(total=5, # リトライ回数
            backoff_factor=3, # リトライが複数回起こったときに伸ばす間隔
            status_forcelist=[400, 403, 429, 500]) # タイムアウト以外の捕捉対象status_code
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    def get_session(self):
        return self.session

    def get(self, url):
            return self.session.get(
                url=url, headers=HEADERS, timeout=(20,10), stream=True)