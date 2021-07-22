import random
import json
import string

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


def concatenate_players(excel_sheet, column_name):
    concat_str = ""
    for player in excel_sheet[column_name]:
        if isinstance(player, str):
            concat_str += f"{player}/"
    concat_str = concat_str[:-1]
    return concat_str


def generate_table(teams, teams_per_match):
    nbr_of_teams = len(teams)
    print(f'teams: {nbr_of_teams}')
    nbr_of_matchs = int(nbr_of_teams/teams_per_match) + (1 if nbr_of_teams%teams_per_match else 0)
    print(f'matchs: {nbr_of_matchs}')
    levels = 0
    matchs = 1
    while matchs < nbr_of_matchs:
        levels += 1
        matchs *= 2
    print(f'levels: {levels}')
    max_nbr_of_matchs = 2**levels
    print(f'max matchs: {max_nbr_of_matchs}')
    start_id = 1
    end_id = max_nbr_of_matchs + 1
    table = dict(matches=[])
    for level in range(levels + 1):
        for unique_id in range(start_id, end_id):
            next_match_id = int((unique_id + 2 - start_id) / 2) + end_id -1
            match_part = "A" if unique_id % 2 else "B"
            next_match = "" if level == levels else f"{next_match_id}:{match_part}"
            match_dict = dict(uniqueId=unique_id, team1="", team2="", score="0:0", over=0, level=level, nextmatch=next_match)
            table["matches"].append(match_dict)
        start_id = end_id
        max_nbr_of_matchs /= 2
        end_id += int(max_nbr_of_matchs)
    table["levels"] = levels
    unique_id = 1
    team_number = 1
    max_nbr_of_matchs = 2**levels
    for team in teams:
        for match_dict in table["matches"]:
            if match_dict["uniqueId"] == unique_id:
                match_dict[f'team{team_number}'] = team["Players"]
        unique_id += 1
        if unique_id > max_nbr_of_matchs:
            team_number = 2
            unique_id = 1
    
    for match_dict in table["matches"]:
        if match_dict["level"] == 1:
            break
        if not match_dict["team2"]:
            match_dict["over"] = 1
            match_dict["score"] = "23:0"
    return table


def generate_pools(teams):
    pools = dict(groups=[])
    nbr_of_teams = len(teams)
    print(f"teams: {nbr_of_teams}")
    if not nbr_of_teams % 4:
        nbr_of_pools = int(nbr_of_teams / 4)
    elif nbr_of_teams in (1, 2, 5):
        nbr_of_pools = 1
    else:
        nbr_of_pools = int(nbr_of_teams / 3)
    print(f"pools: {nbr_of_pools}")
    for pool_name in string.ascii_uppercase[:nbr_of_pools]:
        pool = dict(name=pool_name, teams=[], over=0, level=0, team_number=0, matches=[])
        pools["groups"].append(pool)
    team_nbr = 0
    for team in teams:
        team_dict = dict(name=team["Players"], wins=0, played=0, loses=0, points=0, diff=0)
        for pool in pools["groups"]:
            if pool["name"] == string.ascii_uppercase[team_nbr%nbr_of_pools]:
                pool["teams"].append(team_dict)
                pool["team_number"] +=1
                break
        team_nbr += 1
    unique_id = 1
    for pool in pools["groups"]:
        for team_number in range(pool["team_number"] - 1):
            team1 = pool["teams"][team_number]
            for team2 in pool["teams"][team_number+1:]:
                match_dict = dict(uniqueId=unique_id,
                                  team1=team1["name"],
                                  team2=team2["name"],
                                  score="0:0",
                                  over=0,
                                  level=0)
                pool["matches"].append(match_dict)
                unique_id += 1
    for pool in pools["groups"]:
        print(f"poolname: {pool['name']}")
        print(f"teams: {pool['team_number']}")
        for team in pool["teams"]:
            print(team)
        for match in pool["matches"]:
            print(match)
    return pools