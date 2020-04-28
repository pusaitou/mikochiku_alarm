import requests
import logger

HEADERS = {
    'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) '
                 'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                 'CriOS/69.0.3497.91 Mobile/15E148 Safari/605.1',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.5',
    'accept-encoding' : 'gzip, br',
    'x-youtube-client-name': '2',
    'x-youtube-client-version': '2.20200410'}

# エラー発生時に返す空のレスポンス。
# 返した先でもtext属性が使えるようにするため。
# text:'', status_code:None
EMPTY_RESPONSE = requests.Response()

log = logger.get_logger(__name__)

class HttpRequest:

    def __init__(self):
        self._init_session()

    def _init_session(self):
        self.session = requests.Session()

    def get_session(self):
        return self.session

    def get(self, url, params=None):
        try:
            response = self.session.get(
                url=url, params=params, headers=HEADERS, 
                timeout=(10,10), stream=True)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            # 接続切断によるsocket.gaierror等
            log.error('ネットワークに問題が発生しました。')
        except (requests.exceptions.ConnectTimeout, 
                requests.exceptions.ReadTimeout):
            # リトライが規定回数を超えた場合
            log.error('接続がタイムアウトしました。')
        except requests.exceptions.HTTPError:
            log.error('不正なHTTPレスポンスを検出しました。')
        except requests.exceptions.RequestException as e:
            # その他のエラー
            log.error(f'Error:RequestException{type(e)} {str(e)}')
        # エラー発生時はセッションを初期化する。            
        self._init_session()
        # 空のレスポンスを返す。
        return EMPTY_RESPONSE
