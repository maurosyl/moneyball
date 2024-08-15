from typing import List, Callable, Literal

import numpy as np
import pandas as pd
from team_classes import RealTeam, FantaTeam, Player

class FantaSimulator:

    def __init__(self, fanta_team: FantaTeam, fitness_type: Literal['oracle', 'oracle_avg'], defence_bonus = False):
        self.fanta_team = fanta_team
        self.roles = ['P', 'D', 'C', 'A']
        self.legal_rosters = [
            [1, 3, 4, 3],
            [1, 4, 3, 3],
            [1, 3, 5, 2],
            [1, 4, 4, 2],
            [1, 4, 5, 1]
        ]
        if fitness_type == 'oracle':
            self.fitness_func = self.oracle_fitness
        if fitness_type == 'oracle_avg':
            self.fitness_func = self.avg_oracle_fitness
        self.defence_bonus = defence_bonus

    def oracle_fitness(self, player: Player, week:int):
        fitness = player.score_history[week]
        return fitness

    def avg_oracle_fitness(self, player: Player, week:int):
        fitness = np.mean([s for s in player.score_history if s != -1])
        return fitness

    def make_roster(self, week: int):
        fit_dict = {'role' : [], 'name' : [], 'fitness': [], 'vote': []}
        for role in self.fanta_team.team_dict.keys():
            for player in self.fanta_team.team_dict[role]:
                fit_dict['role'].append(role)
                fit_dict['name'].append(player.name)
                fit_dict['vote'].append(player.vote_history[week])
                fit_dict['fitness'].append(self.fitness_func(player, week))
        fitness_df = pd.DataFrame(data=fit_dict)

        legal_confs = []
        legal_confs_fit = []
        for conf in self.legal_rosters:
            conf_df = pd.DataFrame()
            for i, role in enumerate(self.roles):
                n_players = conf[i]
                role_df = fitness_df[fitness_df['role'] == role]
                best_in_role_df = role_df.sort_values(ascending=False, by=['fitness']).iloc[0:n_players]
                conf_df = conf_df._append(best_in_role_df, ignore_index=True)
            conf_fitness = conf_df['fitness'].sum()
            if self.defence_bonus and conf[1] >= 4:
                # TODO: this works only for the oracle, adding the def bonus could be unsafe with other fitness types
                conf_fitness += self.compute_defence_bonus(conf_df)
            legal_confs.append(conf_df)
            legal_confs_fit.append(conf_fitness)

        roster_df = legal_confs[np.argmax(legal_confs_fit)]
        return roster_df

    def simulate_match(self, week: int, defence_bonus:bool = False):
        roster_df = self.make_roster(week=week)
        match_dict = dict(name=[], role=[], vote=[], score=[])
        for role in self.fanta_team.team_dict.keys():
            for player in self.fanta_team.team_dict[role]:
                if player.name in roster_df['name'].values:
                    match_dict['name'].append(player.name)
                    match_dict['role'].append(player.role)
                    match_dict['vote'].append(player.vote_history[week])
                    match_dict['score'].append(player.score_history[week])
                    match_dict['week'] = week
        def_bonus = self.compute_defence_bonus(match_dict) if defence_bonus else 0
        return match_dict, def_bonus

    def simulate_season(self, defence_bonus:bool=False):
        matches = []
        def_bonus_list = []
        for week in range(38):
            match_dict, def_bonus = self.simulate_match(week=week, defence_bonus=defence_bonus)
            matches.append(pd.DataFrame(match_dict))
            def_bonus_list.append(def_bonus)
        season_df = pd.concat(matches)
        weekly_scores = [m['score'].sum() for m in matches]
        weekly_scores += np.array(def_bonus_list)
        return season_df, weekly_scores

    def compute_defence_bonus(self, match_dict):
        df = pd.DataFrame(match_dict)
        df = df[df['role'].isin(['P', 'D'])]
        if len(df) < 5:
            return 0

        df = df.sort_values(by='vote')
        df = df.iloc[:4]

        avg_vote = df['vote'].mean()
        bonus = 0
        if avg_vote >= 6:
            bonus = 1
        if avg_vote >= 6.5:
            bonus = 3
        if avg_vote >= 7:
            bonus = 6
        return bonus

