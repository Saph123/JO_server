import json
import os
import pandas
from utils import concatenate_players, get_file_name, get_sport_config, generate_table
from utils import generate_pools

path = os.path.join(os.getcwd()+"/JO_2021.xlsx")

sports_name = ("10 km de Meyssiez (9,5 km 150 D+)",
          "Volley",
          "Petanque",
          "Molky",
          "Waterpolo (Tournoi par équipe de 5 )",
          "Lancer de tong",
          "Ping pong",
          "Babyfoot",
          "Flechette",
          "Blindtest ventriglisse relais bière",
          "Polish Horseshoes",
          "100m Ricard ",
          "Beer pong",
          "Dodgeball",
          "Course d'orientation",
          "Concours de pizza",
          "Natation Synchronisée",
          "Spikeball")

for sport_name in sports_name:
    excel_sheet = pandas.read_excel(path, sheet_name=sport_name, engine="openpyxl")
    teams_list = dict()
    teams_list["Teams"] = []
    unique_id = 1
    for column_name in excel_sheet: 
        if "team" in column_name:
            team_dict = dict()
            team_dict["stillingame"] = "True" 
            team_dict["uniqueid"] = unique_id
            team_dict["Players"] = concatenate_players(excel_sheet, column_name)
            teams_list["Teams"].append(team_dict)
            unique_id += 1
        file_name = get_file_name(sport_name)
    with open(f"teams/{file_name}", "w") as file:
        json.dump(teams_list, file, ensure_ascii=False)
    sport_config = get_sport_config(sport_name)
    if sport_config["Type"] == "Table":
        print(sport_name)
        teams_per_match = sport_config["Teams per match"]
        table = generate_table(teams_list["Teams"], teams_per_match)
        file_name = file_name[:-5] + "_playoff.json"
        with open(f"teams/{file_name}", "w") as file:
            json.dump(table, file, ensure_ascii=False)
    elif sport_config["Type"] == "Pool":
        print(sport_name)
        pools = generate_pools(teams_list["Teams"])
        file_name = file_name[:-5] + "_poules.json"
        with open(f"teams/{file_name}", "w") as file:
            json.dump(pools, file, ensure_ascii=False)