import datetime
import json
import pytz
from .settings import *
from django.http import (
    HttpResponseForbidden,
    HttpResponse
)

from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    CarouselColumn,
    CarouselTemplate,
    URITemplateAction,
    TemplateSendMessage
)

from linebot import (
    LineBotApi,
    WebhookHandler
)


line_bot_api = LineBotApi(channel_access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=CHANNEL_SECRET)


def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()
    return HttpResponse('Success', status=200)


from modules.mlb_scraper import MLBScraper
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    try:
        if event.message.text == 'command:直近の試合':
            messages = get_messages_today()
        elif 'かなたん' in event.message.text or 'かなちゃん' in event.message.text or 'ちゃんかな' in event.message.text:
            messages = []
            messages.append(TextSendMessage(text='かなたんかわいい💓'))
        else:
            messages = []
            messages.append(TextSendMessage(text='下のリッチメニューから見たい情報を選択してね☺️'))
        line_bot_api.reply_message(
            event.reply_token,
            messages=messages
        )
    except:
        import traceback
        traceback.print_exc()


def get_messages_today() -> list:
    messages = []
    scoreboard_data = MLBScraper.get_today_schedule()
    games = MLBScraper.get_game_by_team(team=SHOWHEY_TEAM_NAME, scoreboard_data=scoreboard_data)
    if games:
        messages.append(TextSendMessage(text=f'直近のエンジェルスの試合は{len(games)}試合あります。'))
        carousel_items = []
        for game in games:
            try:
                if game['status']['status'] == 'Preview':
                    # 試合前
                    jst = pytz.timezone('Japan')
                    edt_datetime = datetime.datetime.strptime(f'{game["time_date"]}', '%Y/%m/%d %H:%M')
                    if game['ampm'] == 'PM':
                        edt_datetime += datetime.timedelta(hours=+12)
                    jst_datetime = pytz.timezone('US/Eastern').localize(edt_datetime).astimezone(jst)
                    text = f'日時：{jst_datetime:%Y/%m/%d %H:%M}\n場所：{game["venue"]}'
                    subtext = ''
                    if game['home_probable_pitcher']['id'] == SHOWHEY_PLAYER_ID or game['away_probable_pitcher']['id'] == SHOWHEY_PLAYER_ID:
                        subtext += '・大谷翔平選手が先発予定\n'
                    carousel_item = {
                        'thumbnail_image_url': 'https://p4.wallpaperbetter.com/wallpaper/190/581/78/los-angeles-angels-of-anaheim-logo-wallpaper-preview.jpg',
                        'title': f'[試合前] {game["home_team_name"]} vs {game["away_team_name"]}',
                        'text': text,
                        'subtext': subtext[:-1],
                        'actions': {
                            "type": "uri",
                            'label': 'ゲームプレビューを観る',
                            'uri': f'{MLB_GAMEDAY_BASE_URL}{game["game_pk"]}'
                        }
                    }
                    carousel_items.append(carousel_item)
                elif game['status']['status'] == 'Final':
                    # 試合後
                    jst = pytz.timezone('Japan')
                    edt_datetime = datetime.datetime.strptime(game["time_date"], '%Y/%m/%d %H:%M')
                    if game['ampm'] == 'PM':
                        edt_datetime += datetime.timedelta(hours=+12)
                    jst_datetime = pytz.timezone('US/Eastern').localize(edt_datetime).astimezone(jst)
                    text = f'日時：{jst_datetime:%Y/%m/%d %H:%M}\n場所：{game["venue"]}\n結果：{game["home_team_name"]} {game["linescore"]["r"]["home"]} - {game["linescore"]["r"]["away"]} {game["away_team_name"]}'
                    subtext = ''
                    if game['winning_pitcher']['id'] == SHOWHEY_PLAYER_ID:
                        subtext += f'・大谷 {game["winning_pitcher"]["wins"]}勝目\n'
                    elif game['losing_pitcher']['id'] == SHOWHEY_PLAYER_ID:
                        subtext += f'・大谷 {game["losing_pitcher"]["losses"]}敗目\n'
                    if type(game['home_runs']['player']) == list:
                        for player in game['home_runs']['player']:
                            if player['id'] == SHOWHEY_PLAYER_ID:
                                subtext += f'・大谷 第{player["number"]}号HR\n'
                    elif type(game['home_runs']['player']) == dict:
                        if game['home_runs']['player']['id'] == SHOWHEY_PLAYER_ID:
                                subtext += f'・大谷 第{player["number"]}号HR\n'
                    carousel_item = {
                        'thumbnail_image_url': 'https://p4.wallpaperbetter.com/wallpaper/190/581/78/los-angeles-angels-of-anaheim-logo-wallpaper-preview.jpg',
                        'title': f'[試合終了] {game["home_team_name"]} vs {game["away_team_name"]}',
                        'text': text,
                        'subtext': subtext[:-1],
                        'actions': {
                            "type": "uri",
                            'label': '試合映像を見る',
                            'uri': f'{MLB_TV_BASE_URL}{game["game_pk"]}'
                        }
                    }
                    carousel_items.append(carousel_item)
                elif game['status']['status'] == 'In Progress':
                    jst = pytz.timezone('Japan')
                    edt_datetime = datetime.datetime.strptime(game["time_date"], '%Y/%m/%d %H:%M')
                    if game['ampm'] == 'PM':
                        edt_datetime += datetime.timedelta(hours=+12)
                    jst_datetime = pytz.timezone('US/Eastern').localize(edt_datetime).astimezone(jst)
                    text = f'日時：{jst_datetime:%Y/%m/%d %H:%M}\n場所：{game["venue"]}'
                    subtext = f'試合は進行中です。\n{game["status"]["inning"]}回途中\n{game["home_team_name"]} {game["linescore"]["r"]["home"]} - {game["linescore"]["r"]["away"]} {game["away_team_name"]}\n\n'
                    if game['pitcher']['id'] == SHOWHEY_PLAYER_ID:
                        subtext += f'大谷翔平選手が登板中です。\n\n<現在の成績>\n{game["pitcher"]["wins"]}勝{game["pitcher"]["losses"]}敗\n防御率 {game["pitcher"]["era"]}\n'
                    elif game['opposing_pitcher']['id'] == SHOWHEY_PLAYER_ID:
                        subtext += f'大谷翔平選手が登板中です。\n\n<現在の成績>\n{game["opposing_pitcher"]["wins"]}勝{game["opposing_pitcher"]["losses"]}敗\n防御率 {game["opposing_pitcher"]["era"]}\n'
                    if type(game['home_runs']['player']) == list:
                        for player in game['home_runs']['player']:
                            if player['id'] == SHOWHEY_PLAYER_ID:
                                subtext += f'・大谷 第{player["number"]}号HR\n'
                    elif type(game['home_runs']['player']) == dict:
                        if game['home_runs']['player']['id'] == SHOWHEY_PLAYER_ID:
                                subtext += f'・大谷 第{player["number"]}号HR\n'
                    carousel_item = {
                        'thumbnail_image_url': 'https://p4.wallpaperbetter.com/wallpaper/190/581/78/los-angeles-angels-of-anaheim-logo-wallpaper-preview.jpg',
                        'title': f'[試合中] {game["home_team_name"]} vs {game["away_team_name"]}',
                        'text': text,
                        'subtext': subtext[:-1],
                        'actions': {
                            "type": "uri",
                            'label': '試合映像を見る',
                            'uri': f'{MLB_TV_BASE_URL}{game["game_pk"]}'
                        }
                    }
                    carousel_items.append(carousel_item)
            except:
                print(json.dumps(game, indent=2))
                import traceback
                traceback.print_exc()
        columns = [
            CarouselColumn(
                thumbnail_image_url=column["thumbnail_image_url"],
                title=column["title"],
                text=column["text"],
                actions=[
                    URITemplateAction(
                        label=column["actions"]["label"],
                        uri=column["actions"]["uri"],
                    )
                ]
            )
            for column in carousel_items
        ]
        messages.append(TemplateSendMessage(
            alt_text=f'本日エンジェルスの試合は{len(games)}試合です。',
            template=CarouselTemplate(columns=columns)
        ))
        for i, col in enumerate(carousel_items):
            if col["subtext"]:
                messages.append(TextSendMessage(text=f'{i+1}試合目の大谷選手の情報\n{col["subtext"]}'))
            else:
                messages.append(TextSendMessage(text=f'{i+1}試合目の大谷選手に関する情報はありません。'))
    else:
        messages.append(TextSendMessage(text=f'本日エンジェルスの試合予定はありません。'))
    
    return messages
