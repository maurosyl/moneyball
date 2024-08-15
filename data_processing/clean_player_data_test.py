import os
import pandas as pd

from data_cleaning_utils import TEAMS_1819, TEAMS_1920, TEAMS_2021, TEAMS_2122, TEAMS_2223
from data_cleaning_utils import make_season_history

out_dir = '../data/player_data/season_scores'

teams = [TEAMS_1819, TEAMS_1920, TEAMS_2021, TEAMS_2122, TEAMS_2223]
years = ['1819', '1920', '2021', '2122', '2223']

for i in range(len(years)):
    team = teams[i]
    year = years[i]
    data_dir = f'../data/player_data/day2day/day2day_{year}/'
    out_path = f'{out_dir}/season_history_{year}.xlsx'
    players_df = make_season_history(day2day_dir=data_dir, teams_list=TEAMS_1819)
    players_df.to_excel(out_path)


