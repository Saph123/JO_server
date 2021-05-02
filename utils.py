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
    lut = json.load(open("configs/lut.json"))
    return lut[sport_name]

