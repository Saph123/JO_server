
import requests
import copy
import os
import datetime
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
    table["levels"] = levels + 1
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


def team_to_next_step(sport, match_id):
    with open(f"teams/{sport}_playoff.json", "r") as file:
        data = json.load(file)
        matches = data["matches"]
        for match in matches:
            if match["uniqueId"] == match_id:
                results = match["score"].split(":")
                winner = "team1" if int(results[0]) > int(results[1]) else "team2"
                next_match = match['nextmatch']
                next_match_id = int(next_match.split(":")[0])
                for new_match in matches:
                    if new_match["uniqueId"] == next_match_id:
                        team = "team1" if "A" in next_match else "team2"
                        new_match[team] = match[winner]
                        if not match["over"]:
                            new_match[team] = ""

    with open(f"teams/{sport}_playoff.json", "w") as file:
        json.dump(data, file, ensure_ascii=False)


def user_is_authorized(username, sport):
    with open(f"teams/{sport}_status.json", "r") as file:
        data = json.load(file)
        return username in data["arbitre"] or username in ("Max", "Antoine", "Ugo")


def retrieve_score(match_data):
    score = match_data["score"]
    assert score.count(":") == 1
    score_team1, score_team2 = score.split(":")
    return int(score_team1), int(score_team2)


def update_playoff_match(sport, match_id, match_data):
    if not match_data["team1"] or not match_data["team2"]:
        return
    score_team1, score_team2 = retrieve_score(match_data)
    with open(f"teams/{sport}_playoff.json", "r") as file:
        matches_data = json.load(file)
        for match in matches_data["matches"]:
            if match_id == match["uniqueId"]:
                match["score"] = match_data["score"]
                results = match["score"].split(":")
                winner = 1 if score_team1 > score_team2 else 2
                if int(results[0]) == int(results[1]):
                    winner = 0 
                match["over"] = match_data["over"]
    with open(f"teams/{sport}_playoff.json", "w") as file:
        json.dump(matches_data, file, ensure_ascii=False)
    if match_data["level"] != matches_data["levels"] - 1:
        team_to_next_step(sport, match_id)
    else:
        file_name = f"{sport}_summary.json"
        teams = dict(Teams=list())
        winner_name = match_data[f"team{winner}"]
        teams["Teams"].append(dict(Players=winner_name, rank=1))
        second = match_data["team1"] if winner == 2 else match_data["team2"]
        teams["Teams"].append(dict(Players=second, rank=2))
        thirds = []
        for match in matches_data["matches"]:
            if match["level"] == matches_data["levels"] - 2:
                third = match["team1"] if match["over"] == 2 else match_data["team2"]
                thirds.append(third)
        for third in thirds:
            teams["Teams"].append(dict(Players=third, rank=3)) 
        with open(f"results/sports/{file_name}", "w") as file:
            json.dump(teams, file, ensure_ascii=False)


def update_poules_match(sport, match_id, match_data):
    with open(f"teams/{sport}_poules.json", "r") as file:
        matches_data = json.load(file)
        for poule in matches_data["groups"]:
            if poule["name"] == match_data["poulename"]:
                for match in poule["matches"]:
                    if match_id == match["uniqueId"]:
                        match["score"] = match_data["score"]
                        match["over"] = match_data["over"]
                        poule = compute_points(poule)
    with open(f"teams/{sport}_poules.json", "w") as file:
        json.dump(matches_data, file, ensure_ascii=False)
    teams = dict(Teams=list())
    with open(f"teams/{sport}_poules.json", "r") as file:
        matches_data = json.load(file)
        all_poules_over = True
        for poule in matches_data["groups"]:
            if not poule["over"]:
                poule_over = True
                for match in poule["matches"]:
                    if not match["over"]:
                        poule_over = False
                poule["over"] = poule_over
            if not poule_over:
                all_poules_over = False
        if all_poules_over:
            with open(f"teams/{sport}_status.json", "r") as file:
                data = json.load(file)
            if "playoff" in data["states"]:
                for poule in matches_data["groups"]:
                    teams["Teams"].append(dict(Players=get_n_th(poule, 1)["name"]))
                matches_data["groups"].reverse()
                for poule in matches_data["groups"]:
                    teams["Teams"].append(dict(Players=get_n_th(poule, 2)["name"]))
                table = generate_table(teams["Teams"], 2)
                file_name = f"{sport}_playoff.json"
                with open(f"teams/{file_name}", "w") as file:
                    json.dump(table, file, ensure_ascii=False)
                    data["status"] = "playoff"
                    with open(f"teams/{sport}_status.json", "w") as file:
                        json.dump(data, file)
            else:
                for poule in matches_data["groups"]:
                    teams["Teams"].append(dict(Players=get_n_th(poule, 1)["name"], rank=1))
                    teams["Teams"].append(dict(Players=get_n_th(poule, 2)["name"], rank=2))
                    teams["Teams"].append(dict(Players=get_n_th(poule, 3)["name"], rank=3))
                file_name = f"{sport}_summary.json"
                with open(f"results/sports/{file_name}", "w") as file:
                    json.dump(teams, file, ensure_ascii=False)
        else:
            with open(f"teams/{sport}_status.json", "r") as file:
                data = json.load(file)
            data["status"] = "poules"
            with open(f"teams/{sport}_status.json", "w") as file:
                json.dump(data, file)


def get_n_th(poule, n):
    poule_copy = copy.deepcopy(poule)
    nbr_of_teams = len(poule_copy["teams"])
    teams = []
    while len(teams) < n:
        highest_pts = 0
        best_team = ""
        best_diff = 0
        for team in poule_copy["teams"]:
            if len(teams) == nbr_of_teams - 1:
                best_team = poule_copy["teams"][0]
                break
            points = team["points"]
            diff = team["diff"]
            team_name = team["name"]
            if highest_pts < points:
                highest_pts = points
                best_diff = diff
                best_team = team
            elif highest_pts == points:
                if best_diff < diff:
                    highest_pts = points
                    best_diff = diff
                    best_team = team
                elif best_diff == diff:
                    for match in poule_copy["matches"]:
                        if match["team1"] == best_team["name"] and match["team2"] == team_name:
                            if match["over"] == 2:
                                best_team == team
                        elif match["team2"] == best_team["name"] and match["team1"] == team_name:
                            if match["over"] == 1:
                                best_team == team
        teams.append(best_team)
        poule_copy["teams"].remove(best_team)
    print(teams[-1])
    return teams[-1]


def compute_points(poule):
    for team in poule["teams"]:
        team["wins"] = 0
        team["loses"] = 0
        team["diff"] = 0
        team["played"] = 0
        team["points"] = 0
    for match in poule["matches"]:
        if not match["over"]:
            continue
        score_team1, score_team2 = retrieve_score(match)
        if score_team1 or score_team2:
            diff = score_team1 - score_team2
            for team in poule["teams"]:
                if team["name"] == match["team1"]:
                    if diff > 0:
                        team["wins"] += 1
                        team["points"] += 3
                    elif diff < 0:
                        team["loses"] += 1
                    else:
                        team["points"] += 1
                    team["played"] += 1
                    team["diff"] += diff
                if team["name"] == match["team2"]:
                    if diff < 0:
                        team["wins"] += 1
                        team["points"] += 3
                    elif diff > 0:
                        team["loses"] += 1
                    else:
                        team["points"] += 1
                    team["played"] += 1
                    team["diff"] -= diff
    return poule


def update_list(sport, data):
    with open(f"teams/{sport}.json", "r") as file:
        matches_data = json.load(file)
        for player_data in data:
            level = player_data["level"]
            player_name = player_data["username"]
            serie = matches_data["Series"][level]
            for player in serie["Teams"]:
                if player_name == player["Players"]:
                    player["rank"] = player_data["rank"]
                    if "score" in player_data:
                        player["score"] = player_data["score"]
        if len(matches_data["Series"]) > 1:
            if all(serie_is_over(serie) for serie in matches_data["Series"][1:]):
                matches_data["Series"][0]["Teams"] = []
                for player_data in data:
                    level = player_data["level"]
                    serie = matches_data["Series"][level]
                    for player in serie["Teams"]:
                        if player["rank"] and player["rank"] <= serie["Selected"]:
                            next = serie["NextSerie"]
                            if not next == -1:
                                if not any(team["Players"] == player["Players"] for team in matches_data["Series"][next]["Teams"]):
                                    matches_data["Series"][next]["Teams"].append(dict(Players=player["Players"], rank=0))
                                print(matches_data["Series"][next]["Teams"])
            else:
                matches_data["Series"][0]["Teams"] = []
                for _ in range(4):
                    matches_data["Series"][0]["Teams"].append(dict(Players="", rank=0))


    with open(f"teams/{sport}.json", "w") as file:
        json.dump(matches_data, file, ensure_ascii=False)
    if "Pizza" in sport:
        return
    teams=dict(Teams=[])
    for team in matches_data["Series"][0]["Teams"]:
        if team["rank"]:
            teams["Teams"].append(team)
    file_name = f"{sport}_summary.json"
    with open(f"results/sports/{file_name}", "w") as file:
        json.dump(teams, file, ensure_ascii=False)


def generate_pizza_results():
    players_score = []
    for player in players_list():
        players_score.append(dict(Players=player, score=0))
    for judge in players_list():
        with open(f"teams/Pizza/{judge}.json", "r") as pizz_file:
            for team in json.load(pizz_file)["Series"][0]["Teams"]:
                if team["rank"] == 1:
                    for someone in players_score:
                        if someone["Players"] in team["Players"]:
                            someone["score"] += 1
    players_score = sorted(players_score, key = lambda i: i['score'])
    players_score.reverse()
    max_score = players_score[0]["score"]
    rank = 1
    for player in players_score:
        if player["score"] == max_score:
            player["rank"] = rank
        else:
            max_score = player["score"]
            rank += 1
            if rank == 4:
                break
            player["rank"] = rank
    with open(f"results/sports/Pizza_summary.json", "w") as file:
        json.dump(dict(Teams=players_score), file, ensure_ascii=False)


def serie_is_over(serie):
    selected = serie["Selected"]
    if selected:
        for rank in range(selected):
            if all(team["rank"] != rank for team in serie["Teams"]):
                return False
            else:
                print(f"Serie has n°{rank}")
        return True
    return False

def log(sport, username, data):
    with open(f"logs/{sport}.log", "a") as file:
        date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        file.write(f"{date}: {username}:\n {data}\n")


def fix_json():
    for filename in os.listdir("/home/JO/JO_server/teams"):
        if ".json" in filename:
            file_handler = open(os.path.join("/home/JO/JO_server/teams", filename), "a")
            file_handler.write("\n\n\n\n")
            file_handler.close()


def players_list():
    return ['Gazou', 'Mathieu', 'Carol-Ann', 'Beranger', 'Remi', 'Guibra', 'Girex', 'Johan', 'Micka', 'Chris', 'La Guille', 'Max', 'Mathias', 'Shmave', 'Lapinou', 'Lucas', 'Boolbi', 'Ugo', 'Hugo', 'Jose', 'Prompsaud', 'Thomas', 'Brice', 'Antoine', 'Emma', 'Ines', 'Sam', 'Willy', 'Babouche', 'Armand', 'Jolan', 'Florent', 'Florian', 'Quentin', 'Chloe', 'Charlene', 'Pierrick', 'Patrice', 'Mimo', 'Mich']


def activities_list(include_date=False):
    if include_date:
        return {
    "Soirée d'ouverture!":["2021-08-26T20:00:00", "2021-08-27T09:30:00"],
    "Trail":["2021-08-27T09:30:00", "2021-08-27T11:00:00"],
    "Dodgeball":["2021-08-27T11:00:00", "2021-08-27T13:00:00"],
    "Pizza":["2021-08-27T13:00:00", "2021-08-27T15:00:00"],
    "Tong":["2021-08-27T15:00:00", "2021-08-27T18:00:00"],
    "Babyfoot":["2021-08-27T15:00:00", "2021-08-27T18:00:00"],
    "Flechette":["2021-08-27T15:00:00", "2021-08-27T18:00:00"],
    "PingPong":["2021-08-27T15:00:00", "2021-08-27T18:00:00"],
    "Orientation":["2021-08-27T18:00:00", "2021-08-27T19:00:00"],
    "Beerpong":["2021-08-27T19:00:00", "2021-08-28T00:00:00"],
    "Volley":["2021-08-28T10:00:00", "2021-08-28T13:00:00"],
    "Waterpolo":["2021-08-28T14:00:00", "2021-08-28T15:00:00"],
    "Larmina":["2021-08-28T14:00:00", "2021-08-28T15:00:00"],
    "Natation":["2021-08-28T15:00:00", "2021-08-28T17:30:00"],
    "SpikeBall":["2021-08-28T15:00:00", "2021-08-28T17:30:00"],
    "Ventriglisse":["2021-08-28T17:30:00", "2021-08-28T19:00:00"],
    "100mRicard":["2021-08-28T19:00:00", "2021-08-29T04:00:00"],
    "Petanque":["2021-08-29T11:00:00", "2021-08-29T13:00:00"],
    "Molky":["2021-08-29T11:00:00", "2021-08-29T13:00:00"],
    "Rangement":["2021-08-29T14:00:00", "2021-08-29T15:30:00"],
    "Remiseprix":["2021-08-29T15:30:00", "2021-08-29T17:30:00"]
    }
    return ["Trail", "Dodgeball", "Pizza", "Tong", "Babyfoot", "Flechette", "PingPong", "Orientation", "Beerpong", "Volley", "Waterpolo", "Larmina", "Natation", "SpikeBall", "Ventriglisse", "100mRicard", "Petanque", "Molky"]



def sort_list(list):
    new_list = []
    for activity in activities_list():
        if activity in list:
            new_list.append(activity)
    return new_list


def get_results(athlete):
    results = dict(nr1=[], nr2=[], nr3=[])
    for filename in os.listdir("results/sports/"):
        print(filename)
        if "_summary.json" in filename:
            sport = filename.replace("_summary.json", "")
            with open(f"results/sports/{filename}", "r") as file:
                sport_results = json.load(file)
                for team in sport_results["Teams"]:
                    if athlete in team["Players"]:
                        rank = team["rank"]
                        results[f"nr{rank}"].append(sport)
    return results


def update_results(athlete):
    results = get_results(athlete)
    gold_medals = len(results["nr1"])
    silver_medals = len(results["nr2"])
    bronze_medals = len(results["nr3"])
    points = bronze_medals + 20 * silver_medals + 400 * gold_medals
    final_results = dict(
        gold_medals=dict(number=gold_medals, sports=results["nr1"]),
        silver_medals=dict(number=silver_medals, sports=results["nr2"]),
        bronze_medals=dict(number=bronze_medals, sports=results["nr3"]),
        points=points)
    return final_results


def update_global_results():
    results = []
    for athlete in players_list():
        result = update_results(athlete)
        result["name"] = athlete
        results.append(result)
        print(result)
    results = sorted(results, key = lambda i: i['points'])
    results.reverse()
    rank = 0
    score = 1000000  # vous voyez ce que ça fait déjà 1 million Larmina ?
    inc = 1
    final_results = []
    for result in results:
        if result["points"] < score:
            score = result["points"]
            rank += inc
            inc = 1
        else:
            inc += 1
        res = dict(
            rank=rank,
            name=result["name"],
            gold=result["gold_medals"],
            silver=result["silver_medals"],
            bronze=result["bronze_medals"])
        final_results.append(res)
        
    with open(f"results/global.json", "w") as file:
        json.dump(final_results, file)


def generate_event_list(name):
    arbitre_list = []
    playing_list = []
    parse_json(name, "_status.json", arbitre_list)
    parse_json(name, "_playoff.json", playing_list)
    parse_json(name, "_poules.json", playing_list)
    parse_json(name, ".json", playing_list, exclude="_")
    arbitre_list = sort_list(arbitre_list)
    playing_list = sort_list(playing_list)
    print(arbitre_list)
    print(playing_list)
    with open(f"athletes/{name}.json", "w") as athlete_file:
        json.dump(dict(arbitre=arbitre_list, activities=playing_list), athlete_file)


def parse_json(name_searched, suffix, list_to_append, exclude=None):
    for filename in os.listdir("teams/"):
        if suffix in filename:
            if exclude is None or not exclude in filename:
                with open(f"teams/{filename}", "r") as file:
                    if name_searched in file.read():
                        list_to_append.append(filename.split(suffix)[0])

def calculate_rank_clicker(clicker, username):
    for player in clicker:
        if player.get("Players") == username:
            previous_rank = player.get("rank")
            break
    
    
    clicker_new = sorted(clicker, key = lambda i: i['Clicks'])
    clicker_new.reverse()

    rank = 0
    score = 1000000 * 1000000  # Assez bien oui!
    inc = 1
    final_results = []
    for result in clicker_new:
        if result["Clicks"] < score:
            score = result["Clicks"]
            rank += inc
            inc = 1
        else:
            inc += 1
        res = dict(
            rank=rank,
            Players=result["Players"],
            Clicks=result["Clicks"])
        final_results.append(res)
    for player in final_results:
        if player.get("Players") == username:
            new_rank = player.get("rank")
            break
    if previous_rank == new_rank:
        final_results = clicker
    with open(f"teams/Clicker.json", "w") as file:
        json.dump(final_results, file)


def send_notif(to, title, body):
    with open("tokens.txt", "r") as tokens_file:
        tokens = tokens_file.readlines()
    print(tokens)
    if not to == "all":
        for token in tokens:
            if to in token:
                tokens = [token]
                break
    print(tokens)
    for token in tokens:
        if "ExponentPushToken" in token:
            data = {"to": token.split(":")[0], "title":title, "body":body}
            print(data)
            req = requests.post("https://exp.host/--/api/v2/push/send", data = data)