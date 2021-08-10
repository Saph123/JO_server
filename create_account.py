
from __future__ import print_function
from http.server import BaseHTTPRequestHandler,HTTPServer
import ssl
import sys
import os
import socket
import mariadb
import simplejson
import time    
import json
import hashlib
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



cur.execute("SELECT * from users;")
for (id,user,pwd,autho,date) in cur:
    if username == user:
        print(username, "already existing ")
        break
            
cur.execute("INSERT INTO users (username, password, autho,submission_date) VALUES (?,?,?,?)", (username,password,"None",time.strftime('%Y-%m-%d %H:%M:%S')))