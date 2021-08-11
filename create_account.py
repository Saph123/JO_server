
from __future__ import print_function
from http.server import BaseHTTPRequestHandler,HTTPServer
import ssl
import sys
import os
import socket
import mariadb
import simplejson
import time
import re
import random
import json
import hashlib
import string
from utils import fix_json, update_playoff_match, user_is_authorized, update_list, update_poules_match, log, fix_json

try:
    conn = mariadb.connect(
        user="root",
#        password=""
        database="JO"

    )
except mariadb.Error as e:
    print("Error connecting to MariaDB Platform: {%s}"%e)
    sys.exit(1)
cur = conn.cursor()
conn.autocommit = True
liste_users = []
for dirpath, dirnames, filenames in os.walk("teams"):
    for filename in filenames:
        if ".json" in filename:
            raw_players = [ x for x in open(os.path.join(dirpath,filename), "r").readlines() if "Players" in x]
            for each_line in raw_players:
                if "/" in each_line:
                    player_list = re.findall("Players\":.*?}", each_line)
                    if player_list:
                        for player in player_list:
                            for user in player.replace("Players\": \"", "")[:-2].split("/"):
                                if user not in liste_users:
                                    liste_users.append(user)
print(liste_users, len(liste_users))
lower = string.ascii_lowercase
num = string.digits
all = num + lower
liste_password = []
passwordlist = open("passwordlist.txt", "w")
for username in liste_users:
    username = username.replace("é", "e").replace("è","e")
    already_existing = False
    cur.execute("SELECT * from users;")
    for (id,user,pwd,autho,date) in cur:
        if username == user:
            print(username, "already existing, so not creating")
            already_existing = True
            break
    if not already_existing:
        not_commited = True
        while not_commited:
            password = random.sample(all, 4)
            password = "".join(password)
            if password not in liste_password:
                liste_password.append(password)
                passwordlist.write(username + " " + password  + "\n")
                password = hashlib.sha384(password.encode("utf-8")).hexdigest()
                cur.execute("INSERT INTO users (username, password, autho,submission_date) VALUES (?,?,?,?)", (username, password,"None",time.strftime('%Y-%m-%d %H:%M:%S')))
                not_commited = False
passwordlist.close()
