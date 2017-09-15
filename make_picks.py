import requests
import re
import sys
import json
import os
import getpass
import logging

from bs4 import BeautifulSoup as bs
from odds_getter import get_picks
from mnf_getter import fetch_avg_ou
from team_map import covers_to_cbs

format = '{asctime}: {message}'
formatter = logging.Formatter(fmt=format, style='{')

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler('nflog.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

email = os.environ.get('CBS_EMAIL', None)
password = os.environ.get('CBS_PASSWORD', None)

if not email or not password:
    email = input('Email: ')
    password = getpass.getpass()

url = f"https://www.cbssports.com/login?dummy%3A%3Alogin_form=1&form%3A%3Alogin_form=login_form&xurl=https%3A%2F%2Fwww.cbssports.com%2F%3F&master_product=150&vendor=cbssports&form_location=log_in_page&userid={email}&password={password}&_submit=Log+In"

picks_url = "http://fhpool2015.football.cbssports.com/office-pool/make-picks"
make_picks_url = "http://fhpool2015.football.cbssports.com/api/league/opm/pick-list"
TEAM_ID = 56
APPSRC = 'd'

with requests.Session() as s:
    r = s.post(url)
    if r.status_code != 200:
        logger.error("Error logging in to cbs sports: {r.content}")
        sys.exit(1)

    r = s.get(picks_url)
    if r.status_code != 200:
        logger.error("Error getting picks url for cbs sports: {r.content}")
        sys.exit(1)

    html = r.content
    soup = bs(html, 'html.parser')
    away_selections = soup.find_all(class_='awayTeamSelection')
    if len(away_selections) < 16:
        logger.error("Unable to find 16 away teams: {soup}")
        sys.exit(1)

    cbs_picks = []
    picks = get_picks()
    for i, pick in enumerate(picks):
        cbs_pick = covers_to_cbs[pick[0]]
        games = soup.find_all(
            'li', class_='pickContainer'
        )
        for _game in games:
            game = _game.find('input', {'data': re.compile(cbs_pick)})
            if game:
                game_id = game.attrs['data']

        _pick = {
            'game_id': game_id,
            'pick': cbs_pick,
            'weight': f'{16 - i}'
        }
        cbs_picks.append(_pick)
    logger.info(f"Picking: {cbs_picks}")

    week = soup.find('input', id='week').attrs['value']
    team_id = soup.find('input', id='team_id').attrs['value']
    token = re.search('CBSi.token = "(.*)"', soup.text).group(1)

    if not week or not team_id or not token:
        logger.error(
            "Error - week: {week}, team_id: {team_id}, token: {token}"
        )

    payload = {
        "picks": cbs_picks,
        "period": week,
        "team_id": team_id,
        "appsrc": APPSRC,  # Don't know what this is for
        "mnf": fetch_avg_ou(),
    }

    data = {
        "payload": json.dumps(payload).replace(' ', ''),
        "access_token": token,
        "resultFormat": "json",
        "responseFormat": "json",
    }
    logger.info(f'Posting with: {data}')

    response = s.post(make_picks_url, data=data)
    if response.status_code != 200:
        msg = f"Error posting picks: \n{response.content}\n{str(data)}"
        logger.critical(msg)
        sys.exit(1)
