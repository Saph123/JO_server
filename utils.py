import random
import json

def create_empty_dict(excel_sheet):
    athletes = dict()
    for sheet in excel_sheet:
        for column in excel_sheet[sheet]:
            athlete_id = 0
            for _ in excel_sheet[sheet][column]:
                athletes[str(athlete_id)] = dict()
                athlete_id += 1
    return athletes


def store_infos(column, athletes, to_store):
    athlete_id = 0
    for data in column:
        athletes[str(athlete_id)][to_store] = data
        athlete_id +=1
    return athletes


def get_sport_config(sport_name):
    file_name = get_file_name(sport_name)
    return json.load(open(f"configs/{file_name}"))


def get_file_name(sport_name):
    lut = json.load(open("configs/LUT.json"))
    return lut[sport_name]


def get_athletes(sport_votes, athletes):
    athlete_id = 0
    athletes_list = []
    yes_list = ("Participant", "Coureur", "Cuisinier (tout seul ou en equipe)", "Chaud")
    for vote in sport_votes:
        if vote in yes_list:
            athletes_list.append(athletes[str(athlete_id)])
        athlete_id += 1
    random.shuffle(athletes_list)
    return athletes_list


def config_has_team_limit(config):
    return "Wanted teams" in config


def config_has_player_per_team_limit(config):
    return "Wanted players per team" in config


def generate_teams(config, athletes):
    number_of_athletes = len(athletes)
    if config_has_player_per_team_limit(config):
        number_of_teams = int(number_of_athletes / config["Wanted players per team"])
        print(f'Expecting {number_of_teams} teams')
        if number_of_athletes % config["Wanted players per team"]:
            if "Accepted players per team" in config:
                more_teams = config["Accepted players per team"] < config["Wanted players per team"]
                number_of_teams = number_of_teams + 1 if more_teams else number_of_teams - 1
    elif config_has_team_limit(config):
        number_of_teams = config["Wanted teams"]
        print(f'Expecting {number_of_teams} teams')
    boobs_number = get_boobs_number(athletes)
    teams = dict()
    for team_number in range(number_of_teams):
        teams[f'team_{team_number}'] = []
    while boobs_number:
        for team in teams:
            for athlete in athletes:
                if athlete["Sexe"] == "F":
                    teams[team].append(athlete['Nom Prénom'])
                    athletes.remove(athlete)
                    boobs_number -= 2
                    break
    for team in teams:
        if len(teams[team]) < len(teams['team_0']):
            teams[team].append(athletes[0]['Nom Prénom'])
            athletes.remove(athletes[0])
    while athletes:
        for team in teams:
            if athletes:
                teams[team].append(athletes[0]['Nom Prénom'])
                athletes.remove(athletes[0])
    player_per_team = len(teams['team_0'])
    for team in teams:
        if len(teams[team]) < player_per_team:
            teams[team].append('')
    return teams


def get_boobs_number(athletes):
    boobs_number = 0
    for athlete in athletes:
        if athlete["Sexe"] == "F":
            boobs_number += 2
    return boobs_number