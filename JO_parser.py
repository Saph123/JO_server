import os
import hashlib
import subprocess
import re
import shutil
import pandas as pd
import zipfile
import datetime
import time
import json

excel_sheet = pd.read_excel(os.path.join(os.getcwd()+"/JO_2020.xlsx"), sheet_name=None, engine="openpyxl")
matches = dict()
matches["matches"] = []
match = dict()
for sheet in excel_sheet:
    equipe_ventriglisse = []
    if "ventriglisse" in sheet:
        print(type(excel_sheet[sheet]))
        for row in excel_sheet[sheet]:
            print(str(row))
            if "equipe" in str(row):
                equipe_ventriglisse.append(str(row))
        arbitre = str(excel_sheet[sheet].loc[:,"arbitre"], encoding="utf-16").replace("NaN","").replace("\n","/").replace("  ","").replace("/ /","")[:-2]
        for index,equipe in enumerate(equipe_ventriglisse):
            print(equipe)
            # team = ""
            team = str(excel_sheet[sheet].loc[:,equipe], encoding="utf-16").replace("NaN","").replace("\n","/").replace("  ","")
            equipe_ventriglisse[index]=team

        for i in range(0, len(equipe_ventriglisse), 2):
            match["match"] = index
            match["team1"] = equipe_ventriglisse[i]
            match["team2"] = equipe_ventriglisse[i+1]
            match["score"] = "0:0"
            match["over"] = 0
            match["level"] = 0
            matches["matches"].append(match)
        matches["levels"] = 1
        test = open("ventriglisse_match.json","w")
        json.dump(matches, test)
            # print(excel_sheet[sheet].loc[:,equipe].to_string(index=False))
