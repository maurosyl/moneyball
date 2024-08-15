import datetime
import random
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import utils
from buyer_sim import BuyerSimulator
from playground.fanta_sim_GPT import FantaSimulator

def play_strategy(players_df, team_strategy, use_defence_bonus: bool=True):
    buyer_sim = BuyerSimulator(players_df=players_df)
    fanta_team = buyer_sim.pick_team(
        team_strategy=team_strategy,
        dep_strategy='ALL1',
        budget=500,
        seed=0
    )
    simulator = FantaSimulator(fanta_team, fitness_type='oracle', defence_bonus=use_defence_bonus)
    season_df, weekly_scores = simulator.simulate_season(defence_bonus=use_defence_bonus)
    return weekly_scores

def get_goals_distr(weekly_scores):
    goals_distr = np.zeros(10)
    for w in weekly_scores:
        goals = int(np.floor((w - 60)/6))
        goals = min(goals, 9)
        goals_distr[goals] += 1
    return goals_distr

def randomize_costs(costs):
    multipliers = 0.75 + np.random.rand(len(costs))/2
    costs_randomized = costs*multipliers
    return costs_randomized

###### LOGGING
import sys

t0 = time.time()
n_iter = 2000
data_path = '../data/player_data/season_scores_w_cost/season_history_2223.xlsx'
players_df = pd.read_excel(data_path)
strategies = [
    [0.02, 0.02, 0.66, 0.3],
    [0.02, 0.02, 0.3, 0.66],
    [0.05, 0.05, 0.45, 0.4],
    [0.1, 0.1, 0.1, 0.7],
    [0.1, 0.1, 0.7, 0.1],
    [0.1, 0.05, 0.8, 0.05],
    [0.1, 0.15, 0.25, 0.5],
    [0.1, 0.15, 0.45, 0.3],
    [0.1, 0.3, 0.45, 0.15],
    [0.15, 0.25, 0.25, 0.35],
    [0.2, 0.3, 0.15, 0.35],
    [0.2, 0.4, 0.3, 0.1],
    [0.2, 0.5, 0.2, 0.1]
]


################# LOGGING##################à
# Open the file in write mode
log_file = open(f'logs/log_N{n_iter}_bDEF_{time.time()}.txt', 'w')

# Save the original stdout so we can revert sys.stdout later
original_stdout = sys.stdout

# Redirect sys.stdout to the file
sys.stdout = log_file

# Reset sys.stdout to its original state
# sys.stdout = original_stdout
################# LOGGING##################à

original_costs = players_df['cost']
player_df_backup = players_df.copy()

strategies_goal_distrs = []
for team_strategy in strategies:
    print(f'team strategy: {team_strategy}')
    strat_over_72 = []
    strat_total_points = []
    weekly_goals_distr = np.zeros(10)
    for i in range(n_iter):
        players_df['cost'] = randomize_costs(players_df['cost'].values)

        weekly_scores = play_strategy(players_df, team_strategy)

        n_over_72 = len([x for x in weekly_scores if x >= 72])
        total_points = np.sum(weekly_scores)
        weekly_goals_distr += get_goals_distr(weekly_scores)


        strat_over_72.append(n_over_72)
        strat_total_points.append(total_points)

        # Restore original costs
        players_df['cost'] = original_costs

    strategies_goal_distrs.append(weekly_goals_distr)

    avg_total_points = np.mean(strat_total_points)
    std_total_points = np.std(strat_total_points)
    avg_over_72 = np.mean(strat_over_72)
    std_over_72 = np.std(strat_over_72)

    print(f'goals distribution: {weekly_goals_distr}')
    print(f'avg_total_points: {avg_total_points/38}')
    print(f'std_total_points: {std_total_points/38}')
    print(f'avg_over_72: {avg_over_72}')
    print(f'std_over_72: {std_over_72}')
    print('\n')

    # plt.hist(x=strat_total_points)
    # plt.show()

assert players_df.equals(player_df_backup)

print(f"\t {[strat for strat in strategies]} \t")
for i, d1 in enumerate(strategies_goal_distrs):
    string = f"{strategies[i]} \t "
    for j, d2 in enumerate(strategies_goal_distrs):
        prob_12, prob_equal, prob_21 = utils.compare_distributions(d1, d2)
        string += f"[{np.round(prob_12,2)},{np.round(prob_equal,2)}, {np.round(prob_21,2)}] \t"
        #print(f'strategy {strategies[i]} vs {strategies[j]}')
        #print(f'prob_12: {prob_12}')
        #print(f'prob_equal: {prob_equal}')
        #print(f'prob_21: {prob_21} \n')
    print(string)
t1 = time.time()
print(f'time: {t1-t0}')