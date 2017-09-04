import requests
import re
import json
import os
import getpass
from bs4 import BeautifulSoup as bs
from odds_getter import picks
from mnf_getter import fetch_avg_ou
from team_map import covers_to_cbs

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
    print("POST: https://www.ibm.com/watson/developer/api?dev_id=1337&week=1&analyze=deep-neural-conv-net")
    print("Waiting for response...")
    s.post(url)
    print("Processing results in DeepMind.NFL.analyze(week=1, rounds=1000, optimality=True)")
    html = s.get(picks_url).content
    soup = bs(html, 'html.parser')
    away_selections = soup.find_all(class_='awayTeamSelection')
    cbs_picks = []
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
        if i < 5:
            print(f"Picking {json.dumps(_pick)}")
        elif i == 5:
            print("...")

    week = soup.find('input', id='week').attrs['value']
    team_id = soup.find('input', id='team_id').attrs['value']
    token = re.search('CBSi.token = "(.*)"', soup.text).group(1)

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

    response = s.post(make_picks_url, data=data)
