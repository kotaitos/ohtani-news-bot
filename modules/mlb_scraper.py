from datetime import (
    datetime,
    timedelta
)
import pytz
import requests
import sys
sys.path.append('./modules')
from mlb_scraper_settings import *


class MLBScraper:
    @classmethod
    def get_schedule(self, datetime: datetime) -> dict:
        get_url = f'{MLB_SCHEDULE_BASE_URL}year_{str(datetime.year).zfill(2)}/month_{str(datetime.month).zfill(2)}/day_{str(datetime.day).zfill(2)}/master_scoreboard.json'
        response = requests.get(get_url)
        scoreboard_data = response.json()['data']
        return scoreboard_data

    @classmethod
    def get_today_schedule(self) -> dict:
        edt = pytz.timezone('US/Eastern')
        jst = pytz.timezone('Japan')
        jst_now = datetime.now(tz=jst)
        edt_now = edt.normalize(jst_now)
        scoreboard_data = self.get_schedule(datetime=edt_now)
        return scoreboard_data
    
    @classmethod
    def get_yesterday_schedule(self) -> dict:
        edt = pytz.timezone('US/Eastern')
        jst = pytz.timezone('Japan')
        now = datetime.now(tz=jst)
        edt_now = edt.normalize(now)
        aday = timedelta(days=-1)
        edt_yesterday = edt_now + aday
        scoreboard_data = self.get_schedule(datetime=edt_yesterday)
        return scoreboard_data
    
    @classmethod
    def get_tomorrow_schedule(self) -> dict:
        edt = pytz.timezone('US/Eastern')
        jst = pytz.timezone('Japan')
        now = datetime.now(tz=jst)
        edt_now = edt.normalize(now)
        aday = timedelta(days=1)
        edt_tomorrow = edt_now + aday
        scoreboard_data = self.get_schedule(datetime=edt_tomorrow)
        return scoreboard_data
    
    @classmethod
    def get_nextday_schedule(self) -> dict:
        scoreboard_data = self.get_today_schedule()
        edt_nextday = datetime.strptime(scoreboard_data['games']['next_day_date'], '%Y-%m-%d')
        nextday_scoreboard_data = self.get_schedule(datetime=edt_nextday)
        return nextday_scoreboard_data
    
    @classmethod
    def get_game_by_team(self, team: str, scoreboard_data: dict) -> list:
        games = []
        for game in scoreboard_data['games']['game']:
            if game['away_team_name'] == team or game['home_team_name'] == team:
                games.append(game)
        return games


if __name__ == '__main__':
    import json
    r = MLBScraper.get_today_schedule()
    # print(json.dumps(r, indent=2))
