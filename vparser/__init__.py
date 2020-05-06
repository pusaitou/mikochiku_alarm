'''
module : vparser

Query API経由でJSONを得て、ライブ動画IDを取り出す。
'''

import json
import requests
import logger
from httpreq import HttpRequest

log = logger.get_logger(__name__)

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
    指定したチャンネルIDのページが不存在の場合に投げる例外
    '''
    pass


def get_source_json(req:HttpRequest, channel_id):
    '''
    Query APIを叩いてライブ動画IDのリストを含むJSONデータを取り出す.

    戻り値:(str):動画IDのリストを含むJSON文字列。
        リクエスト時にネットワークエラー等のエラーが発生した場合は
        空の文字列 （''）を返す。
    '''
    url = f'https://m.youtube.com/channel/{channel_id}/videos'
    params = {'view':2, 'flow':'list', 'pbj':1}
    response = req.get(url=url, params=params)
    return response.text

def extract_video_ids(source_json:str):
    '''
    JSONからライブ動画のIDのリストを抽出する。
    
    戻り値:(List[str]):ライブ動画のIDのリスト。
        ライブ動画なし,またはJSONが不正なフォーマット/JSON取得時にエラー発生の場合
        空のリスト([])を返す。
    '''
    try:
        source_dic = json.loads(source_json)
    except json.JSONDecodeError:
        log.error('JSONのパースに失敗しました')
        return {}
    # チャンネルページが存在しないエラーを示すJSONを
    # 受け取った場合は、例外を呼び出し側(GUI)に伝播させる。
    if _getitem(source_dic, x_404_error) == (
        'This channel does not exist.'
    ):
        raise InvalidChannelIDException()
    return _get_live_vids(source_dic)

def _get_live_vids(dic):
    contents = _getitem(dic, p_contents) or _find_videos_tab(dic) or {}

    return {_getitem(c, px_vid):_getitem(c, px_title) 
        for c in contents if _getitem(c, px_status) == 'LIVE'}

def _find_videos_tab(dic):
    """
    通常p_contentsの位置に動画リストは存在するが、
    位置が異なる場合は、最初からVideosタブを探す。
    """
    tabroot = _getitem(dic, p_tabroot)
    if tabroot is None:
        return 
    for tab in tabroot:
        tabtitle = _getitem(tab, sx_tabtitle)
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
