import json
import os
import pandas
from utils import create_empty_dict, store_infos, get_sport_config, get_athletes
from utils import config_has_player_per_team_limit, config_has_team_limit, generate_teams

excel_sheet = pandas.read_excel(os.path.join(os.getcwd()+"/JO_2020.xlsx"), sheet_name=None, engine="openpyxl")
athletes = create_empty_dict(excel_sheet)

useful_data = ("Nom Prénom",
               "Sexe")
sports_name = ("10 km de Meyssiez (9,5 km 150 D+)",
          "Volley",
          "Waterpolo (Tournoi par équipe de 5 )",
          "Lancer de tong",
          "Ping pong",
          "Babyfoot",
          "Flechette",
          "Blindtest ventriglisse relais bière",
          "Polish Horseshoes",
          "Tournoi de ShiFuMi",
          "100m Ricard ",
          "Beer pong",
          "Dodgeball",
          "Course d'orientation",
          "Krossfit",
          "Concours de pizza",
          "Concours de gros cuissots",
          "Maximum de distance au rameur en équipe")
sports = dict()
for sport_name in sports_name:
    sports[sport_name] = dict()
for sheet in excel_sheet:
    for column_name in excel_sheet[sheet]:
        if column_name in useful_data:
            athletes = store_infos(excel_sheet[sheet][column_name], athletes, column_name)
        if column_name in sports_name:
            sport_config = get_sport_config(column_name)
            sport_votes = excel_sheet[sheet][column_name]
            sports[column_name]["athletes"] = get_athletes(sport_votes, athletes)
            sports[column_name]["teams"] = generate_teams(sport_config, get_athletes(sport_votes, athletes))
    break
json.dump(sports["Volley"], open("test.json", "w"), ensure_ascii=False)