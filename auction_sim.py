from random import shuffle
from typing import List

from team_classes import FantaTeam, Player
import numpy as np

class Picker:
    base_choice = ['A']*6 + ['C']*8 + ['D']*8 + ['P']*3

    def __init__(self, choice: List[str] = None):
        if choice:
            self.choice = choice
        else:
            #self.choice = sorted(Picker.base_choice, key=lambda k: np.random.random())
            self.choice = Picker.base_choice


class AuctionSimulator:
    def __init__(self, players_df, n_pickers):
        self.players_df = players_df
        self.roles_dict = {}
        self.n_pickers = n_pickers
        self.meta = Picker.base_choice*n_pickers #todo
        self.opp_pickers = [Picker() for i in range(n_pickers)]

    def pick_team(self, picker: Picker, seed: int = 0) -> FantaTeam:
        roles = self.players_df["role"].unique()
        self.roles_dict = {role: self.players_df[self.players_df["role"] == role].sort_values(by="avg_score", ascending = False) for role in roles}
        fanta_team = FantaTeam()
        for i in range(25):
            np.random.seed(seed)
            order_of_play = np.random.permutation(self.n_pickers)
            for turn in order_of_play:
                if turn == 0:
                    # pick my player
                    my_choice = picker.choice[i]
                    my_player = self.drop_next_player(role=my_choice)
                    fanta_team.add_player(my_player)
                else:
                    # pick from the list
                    meta_choice = self.opp_pickers[turn-1].choice[i]
                    my_player = self.drop_next_player(role=meta_choice)
        return fanta_team

    def drop_next_player(self, role):
        df = self.roles_dict[role]
        player_row = df.iloc[0]
        name = player_row['name']
        cost = -1
        fscore_history = [player_row[f'week_{i}'].item() for i in range(1, 39)]
        vote_history = [player_row[f'vote_{i}'].item() for i in range(1, 39)]

        player = Player(name=name, cost=cost, role=role, vote_history=vote_history, score_history=fscore_history)

        df = df.drop(index=df.index[0], axis=0)
        self.roles_dict[role] = df

        return player

