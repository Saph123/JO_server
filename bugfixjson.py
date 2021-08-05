import os

for filename in os.listdir("/home/JO/JO_server/teams"):
    if ".json" in filename:
        file_handler = open(os.path.join("/home/JO/JO_server/teams", filename), "a")
        file_handler.write("\n\n\n\n")
        file_handler.close()