import os


CHANNEL_ACCESS_TOKEN = os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('YOUR_CHANNEL_SECRET')

LOCAL_DB_ROOT = 'local_db/'
USER_GROUPS_JSON_PATH = LOCAL_DB_ROOT + 'user_groups.json'
