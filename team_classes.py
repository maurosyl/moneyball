from dataclasses import dataclass
from typing import List, Literal

import numpy as np
import pandas as pd

class RealTeam:
    pass

@dataclass
class Player:
    name: str
    score_history: np.array
    vote_history: np.array
    cost: int
    # home: RealTeam
    # opponent_history: List[RealTeam]
    role: Literal['P', 'C', 'D', 'A']

    @staticmethod
    def from_df(df: pd.DataFrame, name: str):
        player_row = df[df['name'] == name]
        cost = player_row['cost'].item()
        score_history = [player_row[f'week_{i}'].item() for i in range(1, 39)]
        vote_history = [player_row[f'vote_{i}'].item() for i in range(1, 39)]
        role = player_row['role'].values[0]
        player = Player(name=name, cost=cost, role=role, score_history=score_history, vote_history=vote_history)
        return player


class FantaTeam:
    P: list[Player]
    D: list[Player]
    C: list[Player]
    A: list[Player]
    roles = ["P", "D", 'C', 'A']
    team_dict = dict(P=[], D=[], C=[], A=[])
    team_df = pd.DataFrame(columns=['name', 'role', 'cost', 'avg_score'], index=range(25))

    def __init__(self):
        self.team_dict = {role: [] for role in FantaTeam.roles}
        self.team_df = pd.DataFrame(columns=['name', 'role', 'cost', 'avg_score'])

    def add_player(self, player: Player):
        self.team_dict[player.role].append(player)
        player_dict = dict(
            name=player.name,
            role=player.role,
            cost=player.cost,
            avg_score=np.mean([s for s in player.score_history if s != 0])
        )
        self.team_df = self.team_df._append(player_dict, ignore_index=True)

    def get_avg_total(self):
        return self.team_df['avg_score'].sum()

    def populate_team(self, players_df):
        pass

    def make_roster(self):
        pass