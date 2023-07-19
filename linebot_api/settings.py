import os
from os.path import join, dirname
from dotenv import load_dotenv


load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CHANNEL_ACCESS_TOKEN = os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('YOUR_CHANNEL_SECRET')
SHOWHEY_TEAM_NAME = 'Angels'
SHOWHEY_PLAYER_ID = '660271'
MLB_TV_BASE_URL = 'https://www.mlb.com/tv/g'
MLB_GAMEDAY_BASE_URL = 'https://www.mlb.com/gameday/'
MLB_PLAYER_PROFILE_BASE_URL = 'https://www.mlb.com/player/'

