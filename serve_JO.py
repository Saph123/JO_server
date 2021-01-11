from __future__ import print_function
from http.server import BaseHTTPRequestHandler,HTTPServer
import ssl
import sys
import os
import socket
import mariadb
import simplejson
import time    
import hashlib
root_dir = "/var/www/html/JO"

try:
    conn = mariadb.connect(
        user="max",
        password="analu811",
        # host="192.0.2.1",
        # port=3306,
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
        with open(path, 'rb') as file:
            # Send the html message
            self.wfile.write(file.read())
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(int(content_length)) # <--- Gets the data itself
        # self.send_header("Access-Control-Allow-Headers","*")
        if "login" in self.path:
            tmpdict = simplejson.loads("{"+str(post_data).split("{")[1].split("}")[0]+"}")
            username = tmpdict.get("username")
            password = hashlib.sha384(tmpdict.get("password").encode('utf-8')).hexdigest()
            cur.execute("SELECT * from users")
            for (id,user,pwd,autho,date) in cur:
                if user==username:
                    if password==pwd:
                        self.send_response(200,"sucessfull login")
                        self.send_header("Access-Control-Allow-Origin","*")
                        self.end_headers()
                        return
                        
            self.send_response(403,"fdp")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
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
        # self.wfile.write("")
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
