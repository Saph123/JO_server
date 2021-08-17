from __future__ import print_function
from http.server import BaseHTTPRequestHandler,HTTPServer
import ssl
import sys
import os
import socket

from requests.api import head
import mariadb
import simplejson
import time    
import json
import hashlib
import requests
import re
from utils import fix_json, update_playoff_match, user_is_authorized, update_list, update_poules_match, log, fix_json
from utils import update_global_results


root_dir = os.path.dirname(os.path.realpath(__file__))

first_time = True

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
class myHandler (BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        print("get")
        # print(self.request)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        path = root_dir + self.path
        print(path)
        if os.path.exists(path):
            with open(path, 'rb') as file:
                # Send the html message
                self.wfile.write(file.read())
        else:
            print(f"Error: No such file or directory: {path}")
            self.wfile.write("")
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(int(content_length)) # <--- Gets the data itself
        print (self.path)
        #json.loads(post_data.decode('utf-8')).get("version")
        if json.loads(post_data.decode('utf-8')).get("version") == 1: ## replace here once apk is ready!
            if "login" in self.path:
                tmpdict = simplejson.loads("{"+str(post_data).split("{")[1].split("}")[0]+"}")
                username = tmpdict.get("username")
                password = hashlib.sha384(tmpdict.get("password").encode('utf-8')).hexdigest()
                cur.execute("SELECT * from users")
                for (id,user,pwd,autho,date) in cur:
                    if user.lower()==username.lower():
                        if password==pwd:
                            self.send_response(200,"sucessfull login")
                            self.send_header("Access-Control-Allow-Origin","*")
                            self.end_headers()
                            return
                            
                self.send_response(403,"fdp")
                
            elif "register" in self.path:
                # print(post_data.get("username"))
                tmpdict = simplejson.loads("{"+str(post_data).split("{")[1].split("}")[0]+"}")
                username = tmpdict.get("username")
                password = hashlib.sha384(tmpdict.get("password").encode('utf-8')).hexdigest()
                cur.execute("SELECT * from users;")
                for (id,user,pwd,autho,date) in cur:
                    if username == user:
                        print("already existing ")
                        self.send_response(403,"Login exists already my friend")
                        self.send_header("Access-Control-Allow-Origin","*")
                        self.end_headers()
                        return
                
                cur.execute("INSERT INTO users (username, password, autho,submission_date) VALUES (?,?,?,?)", (username,password,"None",time.strftime('%Y-%m-%d %H:%M:%S')))
                self.send_response(200,"Successfuly registered!")
                # else:
                    # self.send_response(403,"Login exists already my friend")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
            elif "pushmatch" in self.path:
                data = json.loads(post_data.decode('utf-8'))
                print(data)
                username = data["username"]
                sport = data["sport"]
                if user_is_authorized(username, sport):
                    match = data["match"]
                    type = data["type"]
                    if type == "playoff":
                        match_id = int(data["match"]["uniqueId"])
                        update_playoff_match(sport, match_id, match)
                    elif type == "poules":
                        match_id = int(data["match"]["uniqueId"])
                        update_poules_match(sport, match_id, match)
                    elif type == "liste":
                        update_list(sport, match)
                update_global_results()
                fix_json()
                log(sport, username, data)
                self.send_response(200, " fdp")
            elif "pushtoken" in self.path:
                data = json.loads(post_data.decode('utf-8'))
                print(data)
                if data.get("token"):
                    if not os.path.exists("tokens.txt"):
                        open("tokens.txt", "w")
                    if data.get("token") not in open("tokens.txt", "r").read(): # just to be sure we don't write again the same
                        if data.get("username"):
                            open("tokens.txt","a").write(data.get("token") + ":"+ data.get("username") +"\n")
                        else:
                            open("tokens.txt","a").write(data.get("token") + ":\n")
                    elif data.get("username") != "":
                        lines = open("tokens.txt", "r").readlines()
                        for local_token in lines:
                            if data.get("token") in local_token:
                                if data.get("username") != local_token.split(":")[-1].replace("\n", "") and data.get("username") != "":
                                    print("This token changed login!")
                                    # lines[lines.index(local_token)] = data.get("token") + ":"+ data.get("username") +"\n"
                                    to_update = True
                                    break
                                else:
                                    to_update = False
                                    print("I know already this token")
                        if to_update:
                            raw_txt = open("tokens.txt", "r").read()
                            print("(" + data.get("token") + ".*)")
                            regexp = re.findall("(" + re.escape(data.get("token")) + ".*)", raw_txt)[0]
                            raw_txt = raw_txt.replace(regexp, data.get("token") + ":"+ data.get("username") +"\n")
                            open("tokens.txt", "w").write(raw_txt)

                self.send_response(200,"fdp")
            elif "cluedo" in self.path:
                username = json.loads(post_data.decode('utf-8')).get("cluedo")
                print(username)
                if os.path.exists("lasttimecluedo"):
                    last_time = float(open("lasttimecluedo", "r").read())
                else:
                    last_time = time.time() - 6 * 60
                if time.time() > (last_time + 5 * 60): # filter 5 mins
                    print("cluedotime")
                    tokens = open("tokens.txt", "r").readlines()
                    for token in tokens:
                        if "ExponentPushToken" in token:
                            data = {"to": token.split(":")[0].replace(":",""), "title":"CLUEDO!", "body":"Demandé par : %s" % username}
                            req = requests.post("https://exp.host/--/api/v2/push/send", data = data)
                            if re.findall("DeviceNotRegistered", req.text):
                                print("device not registered anymore so removing the line")
                                full_txt = open("tokens.txt", "r").read()
                                open("tokens.txt", "w").write(full_txt.replace(token, ""))
                    open("lasttimecluedo", "w").write(str(time.time()))
                    log("Cluedo", username, "")
                else:
                    print("ignore as it's less than 5 mins since last")

            elif "pushnotif" in self.path:
                pushnotif = json.loads(post_data.decode('utf-8'))
                to_req = pushnotif.get("to")
                title = pushnotif.get("title")
                body = pushnotif.get("body")
                print(pushnotif)
                tokens = open("tokens.txt", "r").readlines()
                if pushnotif.get("to") == "all":
                    print("pushing to all!")
                    print(tokens)
                    for token in tokens:
                        if "ExponentPushToken" in token:
                            data = {"to": token.split(":")[0].replace(":",""), "title":title, "body":body}
                            print(data)
                            req = requests.post("https://exp.host/--/api/v2/push/send", data = data)
                else:
                    print("pushing to: ", to_req)
                    for token in tokens:
                        if to_req in token:
                            if "ExponentPushToken" in token:
                                data = {"to": token.split(":")[0].replace(":",""), "title":title, "body":body}
                                req = requests.post("https://exp.host/--/api/v2/push/send", data = data)
        else:
            log("Tricheur", "unkown", post_data.decode('utf-8'))
            self.send_response(403, "tricheur")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()


        return

 

def is_port_in_use(ip, port):
    res = False
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((ip, port))
    except socket.error as e:
        res = True
    finally:
        s.close()
    return res

def start_server():
    
    try:
        print("Starting http server :")
        server_address = ('', 7070)
        server = HTTPServer(server_address, myHandler)
        # server.socket = ssl.wrap_socket(server.socket, keyfile="C:/Users/mabesson/key.pem",certfile="C:/Users/mabesson/cert.pem",server_side=True )
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
    except Exception as e:
        print(e)
        raise IOError("did not start server %(exception)s" % {'exception': e})

if __name__ == "__main__":

    start_server()
