import requests
from bs4 import BeautifulSoup as bs
import operator
import pandas as pd


url = "http://www.covers.com/odds/football/nfl-moneyline-odds.aspx"

content = requests.get(url).content

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
    top_lines = list(map(int, [cell for cell in top_lines if cell != OFF_TEXT]))
    bottom_lines = list(map(int, [cell for cell in bottom_lines if cell != OFF_TEXT]))
    top_line = round(sum(top_lines) / len(top_lines))
    bottom_line = round(sum(bottom_lines) / len(bottom_lines))
    if top_line < 0:
        summary[away_team] = top_line
    else:
        summary[home_team] = bottom_line

picks = sorted(
    [[name, odds] for name, odds in summary.items()],
    key=lambda x: abs(x[1]), reverse=True)
