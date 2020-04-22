import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


HEADERS = {
    'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) '
                 'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                 'CriOS/69.0.3497.91 Mobile/15E148 Safari/605.1',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.5',
    'accept-encoding' : 'gzip, br',
    'x-youTube-client-name': '2',
    'x-youTube-client-version': '2.20200410'}

class HttpRequest:

    def __init__(self):
        self.session = requests.Session()
        self.retries = Retry(total=5, # リトライ回数
            backoff_factor=3, # リトライが複数回起こったときに伸ばす間隔
            status_forcelist=[400, 403, 429, 500]) # タイムアウト以外の捕捉対象status_code
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    def get_session(self):
        return self.session

    def get(self, url, params=None):
        return self.session.get(
            url=url, params=params, headers=HEADERS, 
            timeout=(20,10), stream=True)
