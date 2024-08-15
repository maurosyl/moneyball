from typing import List, Literal

import numpy as np
import pandas as pd

from team_classes import FantaTeam, Player


# team_strategy = dict(P=0, D=0, C=0, A=0)

class BuyerSimulator:
    team_strategies = [
        [0.1, 0.2, 0.3, 0.4],
        [0.1, 0.1, 0.2, 0.6],
        [0.1, 0.1, 0.4, 0.4],
        [0.05, 0.05, 0.3, 0.6],
        [0.1, 0.25, 0.25, 0.4],
        [0.3, 0.3, 0.3, 0.1],
        [0.05, 0.05, 0.05, 0.85]
    ]
    roles = ['P', 'D', 'C', 'A']
    num_by_role = {'P':3, 'D':8, 'C':8, 'A':6}

    def __init__(self, players_df):
        self.players_df = players_df
        self.roles_dict = {}
        self.budget_dict = {}
        self.roles = BuyerSimulator.roles
        self.num_by_role = BuyerSimulator.num_by_role

    def pick_team(self,
                  team_strategy: List[float],
                  dep_strategy: Literal['ALL1', 'BAL'],
                  budget=500,
                  seed: int = 0) -> FantaTeam:
        # print(f'Picking team with strategy: {team_strategy} and department strategy: {dep_strategy}')
        self.roles_dict = {role: self.players_df[self.players_df["role"] == role].sort_values(by="avg_score", ascending = False) for role in self.roles}
        self.budget_dict = {role: budget*team_strategy[i] for i, role in enumerate(self.roles_dict)}

        fanta_team = FantaTeam()
        for role in self.roles:
            # print(f'Buying dep: {role}')
            dep_budget = self.budget_dict[role]
            role_df = self.roles_dict[role]
            dep_size = self.num_by_role[role]
            dep_players = self.pick_department(players_df=role_df, budget=dep_budget, dep_size=dep_size, strategy=dep_strategy)
            for p in dep_players:
                fanta_team.add_player(p)
        return fanta_team

    def pick_department(self, players_df: pd.DataFrame, budget: int, dep_size: int, strategy: Literal['ALL1', 'BAL']):
        if strategy == 'ALL1':
            players = self.all1_strategy(players_df, budget, dep_size)
        # if strategy == 'BAL':
        #     players = self.bal_strategy(players_df, budget, dep_size)
        return players

    def all1_strategy(self, df, budget, n_players):
        df = df.copy()
        p_budgets = [budget - (n_players-1)] + [1 for i in range(n_players-1)]
        players = []
        for i, budget in enumerate(p_budgets):
            # Get highest-cost players within budget
            # idxs = df[df['cost'] <= budget]['cost'].idxmax()
            cost = df[df['cost'] <= budget]['cost'].max()
            equal_cost_players = df.loc[(df['cost'] == cost)]

            player_row = equal_cost_players.sample(n=1)
            player_bought = Player.from_df(name=player_row['name'].values[0], df=df)
            # Redistribute unused budget
            budget_unused = budget - player_row['cost'].values[0]
            if i < len(p_budgets) - 1:
                p_budgets[i+1] += budget_unused
            # Drop bought player from the table and add to the list
            df.drop(index=player_row.index.item(), axis=0, inplace=True)
            players.append(player_bought)
        return players

    def bal_strategy(self, df,  dep_size):
        pass

    def buy_player(self, df, budget):
        pass