'''
module : vparser

APIから得たJSONから、ライブ動画IDを取り出す。
'''

import json
import requests
from httpreq import HttpRequest

'''
JSONパース用のpath
'''
p_tabroot = [
    'response',
    'contents',
    'singleColumnBrowseResultsRenderer',
    'tabs'
]

sx_tabtitle = [
    'tabRenderer',
    'title'
]

sx_contents_part = [
    'tabRenderer',
    'content',
    'sectionListRenderer',
    'contents',
    0,
    'itemSectionRenderer',
    'contents'
]

p_videotab = [
    'response',
    'contents',
    'singleColumnBrowseResultsRenderer',
    'tabs',
    1,
    'tabRenderer',
    'title'
]

p_contents = [
    'response',
    'contents',
    'singleColumnBrowseResultsRenderer',
    'tabs',
    1,
    'tabRenderer',
    'content',
    'sectionListRenderer',
    'contents',
    0,
    'itemSectionRenderer',
    'contents'
]

px_vid = [
    'compactVideoRenderer',
    'videoId',
]

px_title = [
    'compactVideoRenderer',
    'title',
    'runs',
    0,
    'text'
]

px_status = [
    'compactVideoRenderer',
    'thumbnailOverlays',
    0,
    'thumbnailOverlayTimeStatusRenderer',
    'style'
]

'''
404エラーのJSON path
'''
x_404_error = [
    'response',
    'responseContext',
    'errors',
    0
]


class InvalidChannelIDException(requests.exceptions.RequestException):
    '''
    指定したチャンネルIDのページが不存在（404）の場合に投げる例外
    '''
    pass


def get_source_json(req:HttpRequest, channel_id):
    '''
    Query APIを叩いてライブ動画IDのリストを含むJSONデータを取り出す.

    戻り値:(str):動画IDのリストを含むJSON文字列。
        リクエスト時にネットワークエラー等のエラー発生した場合は
        エラーを表すJSONを返す。現時点ではダミーで{"error":1}

        TODO: エラー種類に応じて値を切り替えて処理できるようにする。
        またはエラー内容ごとに異なる例外を伝播させる。
    '''
    try:
        url = f'https://m.youtube.com/channel/{channel_id}/videos'
        params = {'view':2, 'flow':'list', 'pbj':1}
        response = req.get(url=url, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectTimeout as e:
        print('タイムアウトしました。')
        # sessionを取得しなおす。
        self.request = HttpRequest()
    except requests.exceptions.RequestException as e:
        # NOTE: Query APIでは誤ったChannelIDを指定してもRequestExceptionは発生しない。
        if response.status_code == 404:
            # GUI側に404エラーを伝播させる
            raise InvalidChannelIDException()
        print(f'Error:{response.status_code}')
    except Exception as e:
        print(type(e),str(e))
    # 例外が起きてもエラーjsonを返して継続する。
    return json.dumps({'error':1})


def extract_video_ids(source_json:str):
    '''
    JSONからライブ動画のIDのリストを抽出する。
    
    戻り値:(list):ライブ動画のIDのリスト。
        ライブ動画なし,またはJSONが不正なフォーマット/JSON取得時にエラー発生の場合
        空のリスト([])を返す。
    '''
    try:
        source_dic = json.loads(source_json)
    except json.JSONDecodeError as e:
        print(type(e).str(e))
        return []
    # チャンネルページが存在しない場合、APIはエラーJSONを吐くので例外発生させる。
    if _getitem(source_dic, x_404_error) == (
        'This channel does not exist.'
    ):
        raise InvalidChannelIDException()
    
    if source_dic.get('error'):
        return []

    return _get_live_vids(source_dic)

def _get_live_vids(dic):
    tab = _getitem(dic, p_videotab)
    contents = _getitem(dic, p_contents)
    
    if contents is None:
        # Videosタブが通常位置と異なるため探し直す
        contents = _find_videos_tab(dic)
    if contents is None:
        # Videosタブが見つからなかった
        return []     

    return [ _getitem(c, px_vid) for c in contents
        if _getitem(c, px_status) == 'LIVE' ]       


def _find_videos_tab(dic):
    """
    Videosタブを探す
    """
    tabroot = _getitem(dic, p_tabroot)
    if tabroot is None:
        return 
    for tab in tabroot:
        tabtitle = _getitem(tab, sx_tabtitle)
        if tabtitle is None:
            continue
        if tabtitle == 'Videos':
            return _getitem(tab, sx_contents_part)


def _getitem(dict_body, items: list):
    for item in items:
        if dict_body is None:
            break
        if isinstance(dict_body, dict):
            dict_body = dict_body.get(item)
            continue
        if isinstance(item, int) and \
            isinstance(dict_body, list) and \
            len(dict_body) > item:
            dict_body = dict_body[item]
            continue
        return None
    return dict_body
