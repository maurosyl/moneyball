import os
import pandas as pd

TEAMS_1819 = [
    'Atalanta',
    'Bologna',
    'Cagliari',
    'Chievo',
    'Empoli',
    'Fiorentina',
    'Frosinone',
    'Genoa',
    'Inter',
    'Juventus',
    'Lazio',
    'Milan',
    'Napoli',
    'Parma',
    'Roma',
    'Sampdoria',
    'Sassuolo',
    'SPAL',
    'Torino',
    'Udinese'
]

TEAMS_1920 = [
    'Atalanta',
    'Benevento',
    'Bologna',
    'Cagliari',
    'Crotone',
    'Fiorentina',
    'Genoa',
    'Verona',
    'Inter',
    'Juventus',
    'Lazio',
    'Milan',
    'Napoli',
    'Parma',
    'Roma',
    'Sampdoria',
    'Sassuolo',
    'Spezia',
    'Torino',
    'Udinese'
]
TEAMS_2021 = [
    'Atalanta',
    'Bologna',
    'Cagliari',
    'Empoli',
    'Fiorentina',
    'Genoa',
    'Verona',
    'Inter',
    'Juventus',
    'Lazio',
    'Milan',
    'Napoli',
    'Roma',
    'Salernitana',
    'Sampdoria',
    'Sassuolo',
    'Spezia',
    'Torino',
    'Udinese',
    'Venezia'
]
TEAMS_2122 = [
    'Atalanta',
    'Bologna',
    'Cagliari',
    'Empoli',
    'Fiorentina',
    'Genoa',
    'Verona',
    'Inter',
    'Juventus',
    'Lazio',
    'Milan',
    'Napoli',
    'Roma',
    'Salernitana',
    'Sampdoria',
    'Sassuolo',
    'Spezia',
    'Torino',
    'Udinese',
    'Venezia'
]
TEAMS_2223 = ['Inter','Juventus','Empoli','Milan','Fiorentina','Salernitana','Udinese','Atalanta','Lazio','Roma','Fiorentina','Torino','Cremonese','Sassuolo','Verona', 'Napoli','Lecce','Spezia','Bologna','Monza']

### clean data frame
def concat_df(path):
    all_df = pd.DataFrame()
    for i, filename in enumerate(os.listdir(path)):
        df = pd.read_excel(path + filename)
        df['week'] = i+1
        all_df = pd.concat([all_df, df], ignore_index=True, sort = False)
    return all_df


def clean_df(df, teams):
    # make "team" column
    teams = [i.upper() for i in teams]
    l = list(df[df.columns[0]])
    name = 0
    for i,el in enumerate(l):
        if (str(el) in teams or str(el).upper() in teams):
           name = el
        else:
           l[i] = name
    df[df.columns[0]] = l

    # rename and cut columns
    col_labels = { str(df.columns[0]) : 'team',
                'Unnamed: 1' : 'role',
                'Unnamed: 2' : 'name',
                'Unnamed: 3' : 'score',
                'Unnamed: 4' : 'g_scored',
                'Unnamed: 5' : 'g_taken',
                'Unnamed: 6' : 'penalty_saved',
                'Unnamed: 7' : 'penalty_failed',
                'Unnamed: 8' : 'penalty_scored',
                'Unnamed: 10' : 'amm',
                'Unnamed: 11' : 'esp',
                'Unnamed: 12' : 'assists',
                'week' : 'week'
              }
    df = df.rename(columns = col_labels, inplace = False)
    df = df[col_labels.values()]

    ## cut useless rows
    df = df.loc[(df['role'] == 'P') |
                      (df['role'] == 'C') |
                      (df['role'] == 'D') |
                      (df['role'] == 'A') |
                      (df['role'] == 'ALL')]
    # replace "6*" with "6"
    df = df.replace('6*', 6)
    # cut trainers (ALL) fron players
    df = df[df['role'] != 'ALL']
    return df


def add_fantascores(df):
    # Calculate fantascores
    f_scores = []

    for i, row in df.iterrows():
          f = row['score'] + 3 * row['g_scored'] - row['g_taken'] + row['assists'] + 3 * row['penalty_saved'] - 0.5 * row[
              'amm'] + 3 * row['penalty_scored'] - 3 * row['penalty_failed']
          f_scores.append(f)

    # Add fantascore to the df
    df['f_score'] = f_scores
    return df

def make_season_history(day2day_dir, teams_list):
    df = concat_df(day2day_dir)
    df = clean_df(df, teams_list)
    df = add_fantascores(df)
    # df.to_excel(os.path.join(DATA_PATH, f'{data_folder}.xlsx'))
    print(df.head())
    print(df['f_score'])

    players_dict = dict(name=[], role=[], team=[], played=[], avg_score=[])
    for i in range(1, 39):
        players_dict.update({f'week_{i}': []})
        players_dict.update({f'vote_{i}': []})
    print(players_dict)

    names = df['name'].unique()
    for name in names:
        df_player = df[df['name'] == name]
        df_player = df_player.sort_values(by='week')
        role = df_player['role'].values[0]
        team = df_player['team'].values[0]
        players_dict['name'].append(name)
        players_dict['role'].append(role)
        players_dict['team'].append(team)
        players_dict['played'].append(len(df_player))
        players_dict['avg_score'].append(df_player['f_score'].mean())
        for week in range(1, 39):
            row = df_player[df_player['week'] == week]
            if len(row) > 0:
                players_dict[f'week_{week}'].append(row['f_score'].values[0])
                players_dict[f'vote_{week}'].append(row['score'].values[0])
            else:
                players_dict[f'week_{week}'].append(0)
                players_dict[f'vote_{week}'].append(0)
    print(players_dict)

    df_clean = pd.DataFrame(players_dict)
    return df_clean


# data_folder = 'data/player_data/day2day/day2day_1819/'
# teams = TEAMS_1819
#
# df = concat_df(data_folder)
# df = clean_df(df, teams)
# df = add_fantascores(df)
# # df.to_excel(os.path.join(DATA_PATH, f'{data_folder}.xlsx'))
# print(df.head())
# print(df['f_score'])
#
# players_dict = dict(name=[], role=[], team=[], played = [], avg_score=[])
# for i in range(1, 39):
#     players_dict.update({f'week_{i}' : []})
# print(players_dict)
#
# names = df['name'].unique()
# for name in names:
#     df_player = df[df['name'] == name]
#     df_player = df_player.sort_values(by='week')
#     role = df_player['role'].values[0]
#     team = df_player['team'].values[0]
#     players_dict['name'].append(name)
#     players_dict['role'].append(role)
#     players_dict['team'].append(team)
#     players_dict['played'].append(len(df_player))
#     players_dict['avg_score'].append(df_player['f_score'].mean())
#     for week in range(1, 39):
#         row = df_player[df_player['week'] == week]
#         if len(row) > 0:
#             players_dict[f'week_{week}'].append(row['f_score'].values[0])
#         else:
#             players_dict[f'week_{week}'].append(-1)
# print(players_dict)
#
# df_clean = pd.DataFrame(players_dict)
# df_clean.to_excel('players_df.xlsx')


    # print(df_player)

