from tier import Tier
from game import Game
from season import Season
from summoner import Summoner
from queue_info import QueueInfo
from league_stats import LeagueStats
from champion_stats import ChampionStats
from datetime import datetime

import json
import requests
from bs4 import BeautifulSoup


__version__ = '1.0.0'
__author__ = 'Doomlad'
__license__ = 'BSD-3-Clause'