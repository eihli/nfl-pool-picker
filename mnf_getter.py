import requests
import re
from bs4 import BeautifulSoup as bs


def fetch_avg_ou():
    url = "http://www.covers.com/odds/football/nfl_lines.aspx"

    soup = bs(requests.get(url).content, 'html.parser')

    game = soup.find('div', class_='game-box-header', text=re.compile('Monday'))

    rows = game.find_parent('table').find_all('tr', class_=None)

    cells = [row.find_all('td')[-1] for row in rows]

    cells = [cell.find('div', class_='left') for cell in cells]

    cells = [float(cell.text.strip()) for cell in cells if cell]

    return round(sum(cells) / len(cells))
