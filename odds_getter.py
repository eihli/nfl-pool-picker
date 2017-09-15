import logging
import requests
import sys

from bs4 import BeautifulSoup as bs

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler('nflog.log')
file_handler.setLevel(logging.INFO)
format = "{asctime}: {message}"

logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

url = "http://www.covers.com/odds/football/nfl-moneyline-odds.aspx"


def get_picks():
    r = requests.get(url)
    if r.status_code != 200:
        logger.error("Unable to get odds from covers.com")
        sys.exit(1)

    content = r.content

    soup = bs(content, 'html.parser')

    table = soup.find(class_='CustomOddsContainer').table
    rows = table.find_all('tr', class_='bg_row')

    ODDS_CELL_OFFSET = 3
    OFF_TEXT = 'OFF'

    summary = {}

    for row in rows:
        away_team = row.find(class_='team_away').text.replace('@', '').strip()
        home_team = row.find(class_='team_home').text.replace('@', '').strip()
        odds_cells = row.find_all('td')[ODDS_CELL_OFFSET:]
        top_lines = [cell.find(class_='line_top') for cell in odds_cells]
        bottom_lines = [line.nextSibling.nextSibling for line in top_lines]
        top_lines = [cell.text.strip() for cell in top_lines]
        bottom_lines = [cell.text.strip() for cell in bottom_lines]
        top_lines = list(
            map(int, [cell for cell in top_lines if cell != OFF_TEXT])
        )
        bottom_lines = list(
            map(int, [cell for cell in bottom_lines if cell != OFF_TEXT])
        )
        top_line = round(sum(top_lines) / len(top_lines))
        bottom_line = round(sum(bottom_lines) / len(bottom_lines))
        if top_line < 0:
            summary[away_team] = top_line
        else:
            summary[home_team] = bottom_line

    picks = sorted(
        [[name, odds] for name, odds in summary.items()],
        key=lambda x: abs(x[1]), reverse=True)

    if len(picks) != 16:
        logger.error(f"Expected 16 picks but only got {len(picks)}")
        logger.error(str(picks))
        sys.exit(1)

    return picks
