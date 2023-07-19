import schedule
import time as t
import json
from datetime import datetime

import sys
sys.path.append('./modules')
from push_message_manager_settings import *

from linebot import (
    LineBotApi,
    WebhookHandler
)


line_bot_api = LineBotApi(channel_access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=CHANNEL_SECRET)


class PushMessageManager:
    @classmethod
    async def push_once(messages: list, time: datetime, group: str):
        def push_once_job(messages: list, group: str):
            with open(USER_GROUPS_JSON_PATH, 'r') as f:
                user_groups = json.load(f)
            user_ids = user_groups[group]
            line_bot_api.multicast(to=user_ids, messages=messages)
            return schedule.CancelJob
        schedule.every().day.at(f'{time: %H:%M}').do(push_once_job, messages=messages, group=group)
        while True:
            schedule.run_pending()
            t.sleep(60)
    
    @classmethod
    def push(messages: list, group: str):
        with open(USER_GROUPS_JSON_PATH, 'r') as f:
            user_groups = json.load(f)
        user_ids = user_groups[group]
        line_bot_api.multicast(to=user_ids, messages=messages)
