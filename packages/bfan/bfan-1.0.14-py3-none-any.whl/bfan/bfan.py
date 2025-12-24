#!/usr/bin/env python3
"""

Usage:
  bfan.py run  [--image=<path or name>] [--view=(compact | summary | jsonSummary)] [--env=<env1=val1,env2=val2>] [--clearPassed --stdout --genXml --outputName=<outputName> --arch=<binArch> --tags=<equation> --step=<stepName1,stepName2> --noclean (--prefix <paths>)] [<path>...]
  bfan.py clean  [<path>...]
  bfan.py diff   [<path>...]
  bfan.py update [<path>...]
  
TODO1: impelent --prefix in order to define search path to binary: 
      bfan.py run --arch=cep1 --prefix=product/product1-1.1.1/cep1/bin:product/product2-2.1.1/cep1/bin
   or
      bfan.py run --arch=cep1 --prefix=fileWithPrefixes.txt
TODO2: add extension to executable. use difrent excensin for difrent arch. ex. for cep1 use .sh for win usr .exe

"""
import json
import time
import glob 
from mako.template import Template
from datetime import datetime
from xml.sax.saxutils import escape
from pathlib import Path
import re
import difflib 
import yaml
import pathlib
from docopt import docopt
import shutil
import subprocess
import os
import sys
import  io
from threading import Thread, Lock
from multiprocessing import Queue
#from queue import Queue
from multiprocessing import Process
import signal
import traceback
import importlib.util
from _ast import arg
import  psutil
import socket
DBGMSG = False

#from builtins import None
ALLOWED_ACTION={'run':['diff','exitCode','timeout','run','background','skip','kill','shell'], 'diff':['diff'],'update':['diff']}
DEFAULT_TIMEOUT = 1200
CONFIG_CASCHE = {}      
#BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_CONFIG_FILE = "def.yaml"
TEST_RESULT_DIR =  "result"
TEST_SRC_DIR     = "source"
CONFIG_FILE_NAME     = "config.yaml"


def replace_tags_with_bools(tags, equation):
    # This regex matches words (alphanumeric and underscores) not being 'and', 'or', 'not'
    # and skips parentheses and operators
    def replacer(match):
        word = match.group(0)
        if word in ['and', 'or', 'not', 'True', 'False']:
            return word
        return str(word in tags)

    # Use regex to replace tag names (words) that are not Python operators
    return re.sub(r'\b\w+\b', replacer, equation)



def evaluate_boolean_expression(expr: str) -> bool:
    try:
        # Evaluate the boolean expression using Python's eval
        # It's safe here because the input is constrained to boolean logic
        result = eval(expr)
        if isinstance(result, bool):
            return result
        else:
            raise ValueError("Expression did not evaluate to a boolean.")
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        return None



def get_host_name():
    try:
        host_name = socket.gethostname()
        return host_name
    except Exception as e:
        print(f"Error getting host name: {e}")
        return None


class FilterWritter():
    def __init__(self,filename):
        self.f=open(filename,"w")
        self.lines=[]
    def write(self,line):
        self.f.write(line)
        self.f.write("\n")
        self.lines.append(line)
        return line
    def close(self):
        return self.f.close()

def FindConfigPath():
    path = os.getcwd()
    count=0;
    while (not os.path.isdir(path + os.sep + ".bfan")):
        path = path + os.sep +".." 
        count = count + 1
        if count > 4:
            return None
        
    return path + os.sep + ".bfan"



def LoadSuitConfig(path):
    if not os.path.isfile(path):
        return None
    
    if path not in CONFIG_CASCHE:
        try:
            with open(path) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                CONFIG_CASCHE[path] = config
        except IOError:
            msg = "Could not read file: '{}'".format(path)
            print (msg)
            exit(1)
        except yaml.scanner.ScannerError as e:
            print(e)        
            exit(1)
            
    return  CONFIG_CASCHE[path]
        



        
def LoadFilter(name, suite,  configPath):
    find = False
    # try to find in test dir
    
    path = os.getcwd() + os.sep + "filters" + os.sep + name + ".py"
    find = os.path.isfile(path)
    if not find:
    # try to find in suite dir
        path = configPath + os.sep +"suites"+os.sep + suite + os.sep + "filters" + os.sep + name + ".py"       
        find = os.path.isfile(path)

    if not find:
        # try tofind in global filters
        path = configPath + os.sep + "filters" + os.sep + name + ".py"
        find = os.path.isfile(path)
    if not find:       
        return None

    spec = importlib.util.spec_from_file_location("module.name", path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return foo


def streamReader(pipe,transcriptFunction):
    while True:
        time.sleep(0.1)
        #print("wait for line")
        #sys.stdout.flush()
        line = pipe.readline()
        #print("got line: '{}'".format(line))
        #sys.stdout.flush()
        if line:
            transcriptFunction(line.rstrip())            
        if (not line):
            break

def streamWriter(pipe,transcriptFunction, stdinFileName):

    file = open(stdinFileName, 'r')
    time.sleep(0.1)
    for line in file:
        line = line.rstrip()
        transcriptFunction(">> {}".format(line))
        #pipe.write(bytes(line, 'utf-8'));
        pipe.write(line);
        pipe.write("\n");
        pipe.flush()
        time.sleep(0.2)

    pipe.close()
    
    
            
def IsChildrenRunning(children, timeout=10):
    try:
        for processId in children:
            children[processId].wait(timeout=timeout)
            if DBGMSG:
                print("[dbg]: all children has been closed", flush=True)
    except:
        if DBGMSG:
            print("[dbg]: Child {} has not ben closed by its parent".format(children[processId].pid), flush=True)
        return True
    return False



def kill_child_processes(children, sig=signal.SIGTERM):
    for processId in children:
         try:
             if DBGMSG:
                 print("[dbg]: Killing child process: {}".format(children[processId].pid), flush=True)
             sys.stdout.flush()
             children[processId].send_signal(sig)
         except:
             pass

def backgroundMonitor(q,proc,t1,t2, cmd):
    parent = psutil.Process(proc.pid)
    if DBGMSG:
        print("[dbg]: backgroundMonitor started for {} ".format(proc.pid), flush=True)
    sys.stdout.flush()
    childMap={}
    errorCode = 0

    while(True):
        try:
            data = q.get(block=False)
        except:
            data = None
            
        try:
            proc.wait(timeout=1.3)
            t1.join()
            t2.join()
            break
        
        except subprocess.TimeoutExpired:
            pass
        #print("waiting")
        
        children = parent.children(recursive=True)
        for child in children:
            if child.pid not in childMap:
                if DBGMSG:
                    print("[dbg]: Detect new child: {}".format(child.pid), flush=True)
                sys.stdout.flush()
                childMap[child.pid] = child

        disappiredChildren=[]
        for childPid in childMap:
            if not childMap[childPid].is_running():
                if DBGMSG:
                    print("[dbg]: Child process '{}' has gone.".format(childPid), flush=True)
                disappiredChildren.append(childPid)
                sys.stdout.flush()
        for childPid in disappiredChildren:
            childMap.pop(childPid, None)


        if data:        
            try:
                proc.wait(timeout=1.3)
                if DBGMSG:
                    print("[dbg]: The background process '{}' ({}) has been closed unexpectedly".format(cmd, proc.pid), flush=True)
                q.put("The background process '{}' ({}) has been closed unexpectedly".format(cmd, proc.pid))

            except subprocess.TimeoutExpired:
                if DBGMSG:
                    print("[dbg]: Proces {} is running".format(proc.pid), flush=True)
            
            if DBGMSG:
                print("[dbg]: Going to send kill signal to :{}".format(proc.pid), flush=True)  
            sys.stdout.flush() 
            proc.send_signal(signal.SIGINT)
            if DBGMSG:
                print("[dbg]: Waiting for finish:{}".format(proc.pid), flush=True)

            try:
                proc.wait(timeout=10)
                if DBGMSG:
                    print("[dbg]: seems that main process '{}' has been closed sucessfully. Let's join it".format(proc.pid), flush=True)
                sys.stdout.flush()
            except subprocess.TimeoutExpired:
                q.put("The main proces '{}' has not been closed sucessfully".format(proc.pid))
                if DBGMSG:
                    print("[dbg]: The main proces '{}' has not been closed sucessfully".format(proc.pid), flush=True)
                    print("[dbg]: Let's kill it.", flush=True)
                sys.stdout.flush()
                proc.send_signal(signal.SIGKILL)


            if IsChildrenRunning(childMap):
                if DBGMSG:
                    print("[dbg]: Closeing children of {} process".format(proc.pid), flush=True)
                kill_child_processes(childMap)
            if DBGMSG:
                print("[dbg]: Joining... {} ".format(proc.pid), flush=True)
            sys.stdout.flush()
        #timeoutFlag=True
            t1.join()
            t2.join()
            if DBGMSG:
                print("[dbg]: Process {} has been fully joined".format(proc.pid), flush=True)
            q.put("")
            break
    
    
    #sys.stdout.flush()
def searchExecutable(cmdSplit,config, transcriptFunction):
    base = os.environ.get('BFAN_BASE')
    if base == None:
        base = os.sep;
    else:
        base = base + os.sep
    versionToPath={}
    pathsToCheck = []
    if "prefix" in config:
        for item in config["prefix"]:
            if "${version}" in item:
                itemsplit=item.split("${version}")
                itemB2 = os.path.basename(itemsplit[0])
                itemB1 = os.path.dirname(itemsplit[0])
                       
                regPattern =  Template( base+itemsplit[0]+r"(\d+(\.\d+)*)"+itemsplit[1]).render(arch=config["arch"])
        
                p = re.compile(regPattern)
                validVersions=[]
                if not os.path.isdir(base+itemB1):
                   continue
                for x in os.listdir(base+itemB1):
                    pathToCheck = Template( base+itemB1+os.sep+x+itemsplit[1]).render(arch=config["arch"])
                    m = p.match(pathToCheck)
                    pathsToCheck.append(pathToCheck)
                    if not m:
                        continue
                    validVersions.append(m.group(1))
                    versionToPath[m.group(1)] = pathToCheck
                validVersions.sort(reverse=True, key=lambda s: [int(u) for u in s.split('.')])
                for version in validVersions:
                    pathToCheck = versionToPath[version]+os.sep+cmdSplit[0]
                    if os.path.isfile(pathToCheck):
                        cmdSplit[0] = pathToCheck
                        return cmdSplit
                #transcriptFunction("Error: unable to find executable: '{}'.".format(cmdSplit[0]))
                #transcriptFunction("   Tried in following directories:")
                #for p in pathsToCheck:
                #    transcriptFunction("   " +p)
            else:
                pathToCheck =  Template(item).render(arch=config["arch"]) + os.sep+cmdSplit[0]
                if os.path.isfile(pathToCheck):
                    cmdSplit[0] = pathToCheck
                    return cmdSplit
    return cmdSplit
#what it is ? kuku
def getInternalEnvironmentVariables(pathToBin, arch, configPath):
    ienv={}
    ienv["base"] = os.environ.get('BFAN_BASE')
    if os.environ.get('BFAN_LIBBASE'):
        ienv["libbase"] = os.environ.get('BFAN_LIBBASE')
    else:
        ienv["libbase"] = ienv["base"]

    ienv["arch"] = arch

    ienv["PWD"] = os.path.dirname(pathToBin)
    
    ienv["dist"] = ienv["base"]
    ienv["bfanJsonPath"] = pathToBin+os.sep+"bfan.json"
    ienv["configPath"] = configPath

    return ienv

def variablePreprocessing(inputString, ienv,suite):
    try:
        inputString = Template(inputString).render(PWD=ienv["PWD"],dist=ienv["dist"],base=ienv["base"],libbase=ienv["libbase"],arch=ienv["arch"], configPath=ienv["configPath"], suite=suite)
    except:
        print("Error: when parsing suit configuration. Variable definition is wrong")
        return None;
       
    return inputString

def replace_placeholders(template: str, data: dict) -> str:
    pattern = re.compile(r"\$\{(\w+)\}")
    return pattern.sub(lambda m: data.get(m.group(1), m.group(0)), template)

#what it is ? kuku
def readEnvFrombfan_json(ienv,suite):
    path = ienv["bfanJsonPath"]
    ret = {}
    if os.path.isfile(path):
        with open(path, 'r') as f:
            localConfig = json.load(f)        
        for varName, var in localConfig["env"]["variables"].items():
           
            ret[varName] =  variablePreprocessing(var, ienv,suite) 
            if not ret[varName]:
                return None;
    return ret    


def systemVariablePreprocessing(text: str) -> str:
    # Regex to match $VAR_NAME (letters, numbers, underscore)
    pattern = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")
    
    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))  # if missing, keep original
    
    return pattern.sub(replacer, text)


def mergeEnvConfig(env1, envList, ienv,suite):
    ret = env1.copy()
    for env2 in envList:
        for key,value in env2.items():
            if key in ret:
                ret[key]= ret[key] + ":" + value
            else:
                ret[key]= value

    for key in ret:
        ret[key] = variablePreprocessing(ret[key], ienv,suite)
        if ret[key] == None:
            return None;
    
    for key in ret:
        newValue = systemVariablePreprocessing(ret[key])
        if newValue != None:
            ret[key] = newValue
            
    return ret
 

class TranscriptWriterListener():
    def __init__(self, verboseTranscript):
        self.current = "None"
        self.f=None
        self.verbose = verboseTranscript
        self.bf=None
        self.diffFile=None
        self.diffFileName=None
        self.backgrunfPath=os.path.abspath(TEST_RESULT_DIR + os.sep + "transcript.{}".format("background"))
        
    def error(self,msg):
        if self.f:
            self.f.write("Error: {}\n".format(msg))
        if self.verbose:
            print("Error: {}\n".format(msg));
            sys.stdout.flush()
        pass
    
    def cleaning(self,msg):
        pass    
   
    def startDiff(self,testName,src,ref,diffName,stepName,suite):      
        self.diffFileName = diffName                                               
        
    def diff(self,line,testName,stepName,suite,diffName):
        if not self.diffFile:
            self.diffFile = open(self.diffFileName,"w+")
            
        if self.diffFile:          
            self.diffFile.write(line+"\n")
            
    def stopDiff(self):
        if self.diffFile:
            self.diffFile.close()
            self.diffFile = None
            self.diffFileName = None
            
    def transcript(self,msg):
        if self.f:
            self.f.write(msg+"\n")
            self.f.flush()
        if self.verbose:
            print("[{}]: {}".format(self.current, msg));
            sys.stdout.flush()
    
    def startBackground(self):
        return

                   
    def background(self,msg):
        if not self.bf:
            self.bf = open(self.backgrunfPath,"a+")
        if self.bf:
            self.bf.write(msg+"\n")
            self.bf.flush()
            self.bf.close()
            self.bf = None
        if self.verbose:
            print("[@background]: "+msg);
            sys.stdout.flush()

          
    def log(self,msg):
        if self.f:
            self.f.write(msg+"\n")
        if self.verbose:
            print("[@log]: "+msg);
            sys.stdout.flush()
            
    def startAction(self,name):
        if self.f:
            self.f.flush()
        
    def startStep(self,testName,stepName,suite):
        self.current = testName + "." + stepName
        if self.f:
            self.f.close()
            self.f=None
        self.f = open(TEST_RESULT_DIR + os.sep + "transcript.{}".format(stepName),"a+")
    
    def startTest(self,testName,suite):
        pass
    
    def endStep(self,testName,stepName,suite,status,reason,stepTime):
        if self.f:
            self.f.close()
            self.f=None
       
    def endTest(self,status,name,msg,suite,testTime):
        if self.bf:
            self.bf.close()
            self.bf=None
            
class JunitGenerator():
    def __init__(self,binArch, reportName = 'report'):
        self.data={}
        self.binArch = binArch
        self.reportName = reportName
        self.errors=[]

    def startDiff(self,testName,src,ref,diffName,stepName,suite):
        #self.data[suite]['tests'][testName]["steps"][stepName]["diffFiles"].append({"src":src,"ref":ref,"diff":diffName})
        self.data[suite]['tests'][testName]["steps"][stepName]["diff"].append({"status":True,"src":src,"ref":ref,"diff":os.path.abspath(diffName)}) 

    #def diff(self,line,testName,stepName,suite,diffName):
    def error(self,msg):
        self.errors.append(msg)

    def startTest(self, testName, suite):
        if (not suite in self.data):
            self.data[suite]={'failed':0,'passed':0,'skipped':0,'tests':{}}
        
        if (not testName in self.data[suite]['tests']):
            self.data[suite]['tests'][testName]={'passed':True,'msg':"","steps":{},'now':datetime.now()}
    
    def startStep(self,testName,stepName, suite):
        self.data[suite]['tests'][testName]["steps"][stepName]={'time':"?",'passed':True,'msg':"","diff":[]}        
    
    def endStep(self,testName,stepName,suite,status,reason,stepTime):
        self.data[suite]['tests'][testName]["steps"][stepName]['passed'] = status
        self.data[suite]['tests'][testName]["steps"][stepName]['msg'] = reason
        self.data[suite]['tests'][testName]["steps"][stepName]['time'] = stepTime
        #TODO: add path to diff
        
        
    def endTest(self,status,name,msg,suite,testTime):
        self.data[suite]['tests'][name]['time']=testTime     
        self.data[suite]['tests'][name]['msg']=msg     
        
    def finish(self, status,time):
        fileName = "{}.xml".format(self.reportName)
        if len(self.binArch) > 0:
            fileName = "{}.{}.xml".format(self.reportName,self.binArch)

        f=open(fileName,'w')

        if not f:
            print("Error: unable to create file: '{}'".format(fileName))
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<testsuites>\n')
        
        for suite in self.data:
            testsInSuite=len(self.data[suite]['tests'].keys())
            f.write('<testsuite name="{}.{}" tests="{}" time="{}" >\n'.format(suite,self.binArch,testsInSuite,time))
            for test in self.data[suite]['tests']:

                f.write('<testcase name="{}" classname="{}" time="{}">\n'.format(test,test,self.data[suite]['tests'][test]['time']))
                f.write('<system-out>\n')
                f.write("".center(60,"*"))
                f.write('\n')
                message = "{} [{}] - {}s".format(test, self.data[suite]['tests'][test]['now'].strftime("%d/%m/%Y %H:%M:%S"), self.data[suite]['tests'][test]['time'])
                f.write(message.center(60," "))
                f.write('\n')
                f.write("".center(60,"*"))
                f.write('\n')
                failed = False;

                for step in self.data[suite]['tests'][test]['steps']:
                    step_time = self.data[suite]['tests'][test]["steps"][step]['time']
                    
                    status = "Error"
                    if self.data[suite]['tests'][test]['steps'][step]['passed']:
                        status = "OK"
                    f.write('{:<45} {:<5} - {}s\n'.format(step, status, step_time))
                    if self.data[suite]['tests'][test]['steps'][step]['passed'] != True:      
                       failed = True
                f.write('</system-out>\n')

               
                if (failed):
                    #f.write('<failure message="Error:{}">\n'.format(",\n".join(self.errors)))
                    #f.write('<failure message="Error">\n')
                    f.write('<failure message="Error: {}">\n'.format(self.data[suite]['tests'][test]['msg']))
                    for step in self.data[suite]['tests'][test]['steps']:
                        if self.data[suite]['tests'][test]['steps'][step]['passed'] != True:                       
                            
                            f.write(self.data[suite]['tests'][test]['steps'][step]['msg'])
                            f.write("\n")
                            for diff in self.data[suite]['tests'][test]["steps"][step]["diff"]:
                                if not os.path.isfile(diff['diff']):
                                    continue
                                f.write("\n================================================================================\n")
                                f.write("diff {} {} > {}\n".format(diff['src'],diff['ref'], diff['diff']))
    
                                if (os.path.isfile(diff['diff'])):
                                    df = open(diff['diff'],"r")
                                    for line in df.readlines():
                                        f.write(escape(line))
                                    df.close()
                                    f.write("\n")            
                                #else:
                                #    f.write("Unable to locate diff file '{}'".format(diff['diff']))
                                #    f.write(os.getcwd())                
                    if len(self.errors):
                        f.write('MSG: \n{}'.format("\n".join(self.errors)))    
                    f.write('</failure>\n')
                f.write('</testcase>\n')                            
            f.write('</testsuite>\n') 
        
        f.write('</testsuites>\n')
            
        f.close()
          
      
            
class CompactTestExecutionListener():
    def error(self,msg):
        print(msg)
    
    def cleaning(self,msg):
        print(msg,end="")
        pass    
   
    def cleanDone(self,status,msg):
        print(msg)
        
    def startTest(self,testName,suite):
        print("".center(60,"*"))
        now = datetime.now()
        message = "{} [{}]".format(testName, now.strftime("%d/%m/%Y %H:%M:%S"))
        print(message.center(60," "))
        print("".center(60,"*"))
    
    def startStep(self,testName,stepName,suite):
        print(stepName.ljust(50, ' '),end="")
    
    def finish(self, status, time):
        if status:
            print("Pass.")
        else:
            print("Failed.")
    
    
    def endStep(self,testName,stepName,suite,status,reason,stepTime):
        print(reason.rjust(10, ' '))

    def endTest(self,status,name,msg,suite,testTime):
        print("Test duration: {} s".format(testTime), flush=True)
        if (status):            
            print("Test Passed", flush=True)
        else:
            print("Test failed:{}".format(msg), flush=True)

class PassFailedFileWiter():
    def __init__(self):
        self.passList=[]
        self.failedList=[]

    def error(self,msg):
        pass

    def cleaning(self,msg):
        pass

    def cleanDone(self,status,msg):
        pass

    def startTest(self,testName,suite):
        pass

    def startStep(self,testName,stepName,suite):
        pass

    def finish(self, status, time):
        #print("write passed_list.txt file", flush=True)
        f = open("passed_list.txt", "w")
        for item in self.passList:
            f.write(item + "\n")
        f.close()

        #print("write failed_list.txt file", flush=True)
        f = open("failed_list.txt", "w")
        for item in self.failedList:
            f.write(item + "\n")
        f.close()


    def endStep(self,testName,stepName,suite,status,reason,stepTime):
        pass

    def endTest(self,status,name,msg,suite,testTime):
        if status:
            self.passList.append(name)
        else:
            self.failedList.append(name)



def find_procs_by_name(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() == proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def getArgs(s):
    args = []
    cur  = ''
    inQuotes = 0
    for char in s.strip():
        if char == ' ' and not inQuotes:
            args.append(cur)
            cur = ''
        elif char == '"' and not inQuotes:
            inQuotes = 1
            #cur += char
        elif char == '"' and inQuotes:
            inQuotes = 0
            #cur += char
        else:
            cur += char
    args.append(cur)
    return args

class CMDExecutor():
    def __init__(self, configPath):
        self.backgroundActionsToKill=[]
        self.backgroundEnv=[]
        self.configPath = configPath


    def killBackgrounded(self):
        errorMsg = ""
        for item in self.backgroundActionsToKill:
            item[0].put("stop")
            item[1].join()
            errorMsg = errorMsg + item[0].get(block=True)
        self.backgroundActionsToKill=[]
        return errorMsg

    def killBackgroundedByList(self, toKill):
        errorMsg = ""
        for item in toKill:
            item[0].put("stop")
            item[1].join()
            errorMsg = errorMsg + item[0].get(block=True)
        toKill=[]
        return errorMsg

    def killBackgroundedById(id):
        inx = 0;
        for process in self.backgroundActionsToKill:
            if process[2] == id:
                break;
            inx = inx + 1
        killStatus = ""

        if inx < len(self.backgroundActionsToKill):
            killStatus = self.killBackgroundedByList([self.backgroundActionsToKill[inx]])
            del self.backgroundActionsToKill[inx]
        else:
           return "Unable to find background proces id = {}".format(id)
        
        return killStatus

    def readEnvFromConfig(self,configPath, env):
        config = LoadSuitConfig(configPath)
        if not config:
            return None
        
        if not 'env' in config:
            return None
        
        if not 'variables' in config['env']:
            return None
        
        for item in config["env"]["variables"]:
            env[item] = config["env"]["variables"][item]

    def replace_vars(self,command, varmap):
        ret=[]
        for text in command:
            pattern = re.compile(r'\$([A-Za-z_]\w*)')
    
            def repl(match):
                var_name = match.group(1)
                return str(varmap.get(var_name, match.group(0)))  # fallback to original if missing
            ret.append(pattern.sub(repl, text))
        return ret

    def shellCmd(self,command, transcriptFunction,suite, config, background=False,timeout=1200,env=None,backgroundId=None,shell=False):
        homeDir = str(Path.home())
        
        globalTargetDirPath = homeDir + os.sep +".bfan"+ os.sep + CONFIG_FILE_NAME
        suitelTargetDirPath = homeDir + os.sep +".bfan"+ os.sep +"suites"+os.sep + suite + os.sep + CONFIG_FILE_NAME

        self.readEnvFromConfig(globalTargetDirPath, env)
        self.readEnvFromConfig(suitelTargetDirPath, env)

        
                                      
        
        #self.config= z = {**config, **LoadSuitConfig(self.suite)}

        orignalCommand = command
        prefix = "";
        sdtinAndCmd = command.split("|")
        stdinFileName = None;
        if len(sdtinAndCmd) == 2:
            command = sdtinAndCmd[1]
            stdinFileName = sdtinAndCmd[0]
            stdinFileName= stdinFileName.lstrip()
            stdinFileName= stdinFileName.rstrip()

        
        if (stdinFileName):
            if not os.path.isfile(stdinFileName):
                transcriptFunction("Unable to find input file '{}'".format(stdinFileName))
                return 1,False

#        ret[varName] =   Template(var).render(PWD=os.path.dirname(pathToBin),dist=base,base=base,libbase=libbase,arch=arch)
#kuku        

        command = replace_placeholders(command, env)

        cmdSplit = getArgs(command) #command.split()
        cmdSplit = searchExecutable(cmdSplit,config, transcriptFunction)
        cmdName = os.path.basename(cmdSplit[0])


        #if find_procs_by_name(cmdName):
        #    transcriptFunction("Process With '{}' already exist.".format(command.split()[0]))
        #    return -127,False
        
        ienv = getInternalEnvironmentVariables(os.path.dirname(cmdSplit[0]), config["arch"], self.configPath)
        envWithLocalConfig = readEnvFrombfan_json(ienv,suite)
        if  envWithLocalConfig == None:
            transcriptFunction("Unable to process variable settings from local json config. Error in template?")
            return 1,False

        newenv={}
        env_dict = dict(os.environ)
        finalEnv = mergeEnvConfig(newenv, [env] + [envWithLocalConfig]+self.backgroundEnv, ienv,suite)
        if finalEnv == None:
            transcriptFunction("Unable to process variable settings from suit config. Error in template?")
            return 1,False


        if "SYSTEMROOT" in os.environ:
            finalEnv["SYSTEMROOT"] = os.environ["SYSTEMROOT"]

        for key, value in finalEnv.items():
            transcriptFunction("[bfan]> export {}={}".format(key, value))
        
        transcriptFunction("[bfan]> hostname = {}".format(get_host_name()))
        transcriptFunction("[bfan]> homeDir = {}".format(homeDir))

        transcriptFunction("[bfan]> Run command: '{}' at: '{}'".format(orignalCommand, os.getcwd()))

        cmdSplit = self.replace_vars(cmdSplit, finalEnv)
        command = " ".join(cmdSplit)

        transcriptFunction("[bfan]> command evaluates to: '{}' ".format(command))
        timeoutFlag=False
        oldPath = os.getcwd()
        success = False


        try:
            proc = subprocess.Popen(cmdSplit,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE,env=finalEnv, bufsize=1, universal_newlines=True)
            success = True
        except FileNotFoundError:
            transcriptFunction("[bfan]> Command '{}' not found!!!.".format(cmdSplit[0]))

        if (success == False) and (len(cmdSplit[0]) > 2) and (cmdSplit[0][0]!='.'):
            cmdSplit[0] = "./"+cmdSplit[0]
            transcriptFunction("[bfan]> Will try '{}'".format(cmdSplit[0]))
            try:
                proc = subprocess.Popen(cmdSplit,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE,env=finalEnv, bufsize=1, universal_newlines=True)
            except FileNotFoundError:
                transcriptFunction("[bfan]> Command '{}' not found.".format(command.split()[0]))
                return -127,False

        os.chdir(oldPath)
        t1 = Thread(target=streamReader, args=[proc.stdout, transcriptFunction])
        t2 = Thread(target=streamReader, args=[proc.stderr, transcriptFunction])
        if (stdinFileName):
            tstdIn = Thread(target=streamWriter, args=[proc.stdin, transcriptFunction, stdinFileName])
        
        t1.start()
        t2.start()
        if (stdinFileName):
            tstdIn.start()
    
        if background:
            self.backgroundEnv.append(envWithLocalConfig)
            q = Queue()
            t3 = Thread(target = backgroundMonitor, args =(q,proc,t1,t2, cmdName))
            t3.start()
            self.backgroundActionsToKill.append([q,t3,backgroundId])
            returnCode=True
            return returnCode,timeoutFlag

        try:
            proc.wait(timeout=timeout)
            returnCode = proc.returncode

        except subprocess.TimeoutExpired:
            proc.send_signal(signal.SIGTERM)
            proc.wait()
            timeoutFlag=True
        t1.join()
        t2.join()
        if (stdinFileName):
            tstdIn.join()
        returnCode = proc.returncode
        return returnCode,timeoutFlag





class TestExecutor():
    def __init__(self,path,tel,ydef,config,stepFilter=None):
        self.ydef = ydef
        self.configPath = FindConfigPath()
        self.testName = os.path.basename(os.getcwd())
        self.suite=pathlib.Path(os.getcwd()).suffix[1:]
        self.tel = tel
        self.expectedExitCode=0
        self.timeout=DEFAULT_TIMEOUT
        self.stepFilter=stepFilter
        self.config= z = {**config, 
                          **LoadSuitConfig(self.configPath + os.sep +"suites"+os.sep + self.suite + os.sep + CONFIG_FILE_NAME)}
        

        globalConfig = LoadSuitConfig(self.configPath + os.sep + os.sep + CONFIG_FILE_NAME)
        if globalConfig:
            if 'env' in self.config and 'env' in globalConfig:
                if 'variables' in self.config['env'] and 'variables' in globalConfig['env']:
                    joined_map = {**self.config['env']['variables'], **globalConfig['env']['variables']}
                    self.config['env']['variables'] = joined_map
        #    self.config = joined_map
                                      
                                      
                            

        self.stepName = "??"
        self.cmdExecutor = CMDExecutor(self.configPath)

    
    def do_run_Action_kill(self,tel, action, spec):
        id = int(spec)
        killStatus = self.cmdExecutor.killBackgroundedById(id)

        if len(killStatus):
            return False,False,killStatus
        return True,True,"OK"

    def do_run_Action_exitCode(self,tel, action, spec):
        self.expectedExitCode = spec    
        return True,True,""
    
    def do_run_Action_timeout(self,tel, action, spec):
        self.timeout = spec    
        return True,True,""

 
    def getEnv(self):
        allEnv={}
        for item in os.environ:
            matchObj = re.match( r'BFAN_(\S+)', item)
            if matchObj:            
                allEnv[matchObj.group(1)] =os.environ[item]
            
        
        for item in self.config["env"]["variables"]:
            if not item in allEnv:
                allEnv[item] = self.config["env"]["variables"][item]     
        return allEnv
       
    def do_run_Action_skip(self, tel, action, spec):
        return False,True,"Skipped ({})".format(spec)
    
    def do_run_Action_run(self, tel, action, spec):
        oldPath = os.getcwd()
        os.chdir(TEST_RESULT_DIR)
        
        #tel.transcript("Run Command: {}".format(spec))
                
        returnCode,timeoutFlag = self.cmdExecutor.shellCmd(spec,tel.transcript,self.suite,self.config, False, self.timeout ,self.getEnv())
        if timeoutFlag:
            os.chdir(oldPath)
            return True,False, "Timeout {}s (command:{})".format(self.timeout,spec )        
        if self.expectedExitCode != returnCode:
            os.chdir(oldPath)
            return True,False, "Unexpect Exist Code: {} != {} (command: {})".format(self.expectedExitCode,returnCode,spec)

        self.expectedExitCode = 0
        self.timeout = DEFAULT_TIMEOUT
        os.chdir(oldPath)
        return True,True,"OK"
    
    def do_run_Action_shell(self, tel, action, spec):
        oldPath = os.getcwd()
        os.chdir(TEST_RESULT_DIR)
        
        #tel.transcript("Run Command: {}".format(spec))
                
        returnCode,timeoutFlag = self.cmdExecutor.shellCmd(spec,tel.transcript,self.suite,self.config, False, self.timeout ,self.getEnv(),shell=True)
        if timeoutFlag:
            os.chdir(oldPath)
            return True,False, "Timeout {}s (command:{})".format(self.timeout,spec )        
        if self.expectedExitCode != returnCode:
            os.chdir(oldPath)
            return True,False, "Unexpect Exist Code: {} != {} (command: {})".format(self.expectedExitCode,returnCode,spec)

        self.expectedExitCode = 0
        self.timeout = DEFAULT_TIMEOUT
        os.chdir(oldPath)
        return True,True,"OK"
    
    def do_run_Action_background(self,tel, action, spec): 
        tel.startBackground()
        oldPath = os.getcwd()
        os.chdir(TEST_RESULT_DIR)
        #plitedSpec = spec.split(" ")
        splitedSpec = re.split(r'[\n\t\f\v\r ]+', spec)
        id = 0;
        if splitedSpec[0].isdigit():
            spec = " ".join(splitedSpec[1:])
            id = int(splitedSpec[0])

        tel.background("Run in background[{}]: {}".format(id, spec))
        returnCode,timeoutFlag = self.cmdExecutor.shellCmd(spec,tel.background,self.suite, self.config,True, self.timeout, self.getEnv(), id)
        os.chdir(oldPath)
        return True,True,"OK"
    
        
    def do_run_Action_diff(self, tel, action, spec):      
        filters,source,reference,sourceFiltered,referenceFiltered=parseDiffSpec(spec)
        diffFile = "{}.{}".format(source,"diff")
        tel.startDiff(self.testName,source,reference,diffFile,self.stepName,self.suite)
        
        if not os.path.isfile(source):
            tel.stopDiff()
            return True,False,"Nothing to filter, no source file: {}".format(source)
        
        if not os.path.isfile(reference):
            tel.stopDiff()
            return True,False,"Nothing to filter, no reference file: {}".format(reference)
        
        srcf=FilterWritter(sourceFiltered)
        reff=FilterWritter(referenceFiltered)
        
        fs,fr = loadFilterChain(tel,srcf, reff, filters, self.suite,  self.configPath);
        if not fs or not fr:
            tel.stopDiff()
            return True,False,"problem with chain setup"
    
    
        if not filterFile(tel,source,fs):
            return True,False,"problem with src filters"
        if not filterFile(tel,reference,fr):
           return True,False,"problem with src filters"
        
        if srcf.lines == None:
            tel.stopDiff()
            return True,False,"problem with src filters"
        if reff.lines == None:
            tel.stopDiff()
            return True,False,"problem with ref filters"
        #d = difflib.Differ()
        #diff = list(d.compare(refFilteredContent, srcFilteredContent))
        diff = difflib.unified_diff(reff.lines, srcf.lines, fromfile=referenceFiltered, tofile=sourceFiltered)
        #diff = difflib.ndiff(refFilteredContent, srcFilteredContent)
        status = True
        reason = "OK"
        for line in diff:
            if status:
                reason = "Diff"
            status = False;
            tel.diff(line,self.testName,self.stepName,self.suite,diffFile)
        continueStep = True
        tel.stopDiff()
        return continueStep,status,reason
    
    def  do_diff_Action_diff(self, tel, action, spec):           
        return self.do_run_Action_diff(tel, action, spec)

    def runPostTestHook(self, tel, postCommandAction):
        oldPath = os.getcwd()
        os.chdir(TEST_RESULT_DIR)

        stepName = "postRunHook"

        returnCode,timeoutFlag = self.cmdExecutor.shellCmd(postCommandAction,tel.transcript,self.suite,self.config, False, self.timeout ,self.getEnv())
        if timeoutFlag:
            os.chdir(oldPath)
            return True,False, "Timeout {}s (command:{})".format(self.timeout,postCommandAction )
        if self.expectedExitCode != returnCode:
            os.chdir(oldPath)
            return True,False, "Unexpect Exist Code: {} != {} (command: {})".format(self.expectedExitCode,returnCode,postCommandAction)

        self.expectedExitCode = 0
        self.timeout = DEFAULT_TIMEOUT
        os.chdir(oldPath)
        return True,True,"OK"
 
    def  do_update_Action_diff(self, tel, action, spec):
        filters,source,reference,sourceFiltered,referenceFiltered=parseDiffSpec(spec)
        if not os.path.isfile(source):
            return False,"Nothing to update. Missing src file: {}".format(source)
        tel.log("Coping {} -> {}".format(source,reference))
        shutil.copyfile(source, reference)
        return True,True,"OK"
    

    def startTestInCurrentDir(self, tel, command, ydef):
        try:
            path = TEST_CONFIG_FILE
            
            testStatus = True
            testReason = []
            
            for step in ydef['steps']:
                stepStatus=True
                stepReason = []
                stepName = next(iter(step))
                
                # Skip steps if stepFilter is set and doesn't match
                if self.stepFilter and stepName not in self.stepFilter:
                    continue
                    
                stepStartTime = datetime.now().replace(microsecond=0)
                tel.startStep(self.testName, stepName,self.suite)
                self.stepName = stepName
                
                actions = reorderActions(step[stepName])           
                for actionSpec in actions:                
                    action = next(iter(actionSpec))
                     
                    if action not in ALLOWED_ACTION[command]:
                        continue
                    
                    callFunction = "do_{}_Action_{}".format(command,action)
                    tel.startAction(action)
                    if not hasattr(self, callFunction):
                        msg = "Not implemented action: '{}'".format(callFunction)
                        stepStatus = False;
                        testStatus = False
                        testReason.append(msg)
                        continue
                                                        
                    
                    obj = getattr(self, callFunction)
                    continueStep,status,msg = obj(tel,action, actionSpec[action])                     
                    if status == False or continueStep == False:
                        stepReason.append(msg) 
                        
                    if status == False:
                        stepStatus = False;
                        testStatus = False
                        testReason.append(msg)
                        
                    if continueStep == False:                                                                                        
                        break                     
    
                if stepStatus and len(stepReason) == 0:
                    stepReason=['OK']
                
                now = datetime.now().replace(microsecond=0)
                stepTime = (now - stepStartTime).total_seconds()
            
                tel.endStep(self.testName,stepName,self.suite,stepStatus,",".join(stepReason),stepTime)
                self.stepName = "?"
            
            if testStatus and len(testReason) == 0:
                testReason=['?']        
    
            if os.environ.get('BFAN_POSTRUNHOOK'):
                stepReason=[]
                tel.startStep(self.testName, "postTestHook", self.suite)
                continueStep,status,msg = self.runPostTestHook(tel, os.environ.get('BFAN_POSTRUNHOOK'))
                if status == False or continueStep == False:
                    stepReason.append(msg)
                if stepStatus and len(stepReason) == 0:
                    stepReason=['OK']
                if status == False:
                     stepStatus = False;
                     testStatus = False
                     testReason.append(msg)
                tel.endStep(self.testName,"postTestHook",self.suite,stepStatus,",".join(stepReason),123)

        except:
            e = sys.exc_info()
            testReason.append("{}".format("".join(traceback.format_exception(*e))))   
            testStatus=False

        self.cmdExecutor.killBackgrounded()
        return testStatus,",".join(testReason)


class TestRunner():
    def __init__(self,path,tel,ydef,config,stepFilter=None,noclean=False):
        self.ydef = ydef
        self.testName = os.path.basename(os.getcwd())
        self.suite=pathlib.Path(os.getcwd()).suffix[1:]
        self.tel = tel
        self.backgroundActionsToKill=[]
        self.expectedExitCode=0
        self.timeout=DEFAULT_TIMEOUT
        #self.config= z = {**config, **LoadSuitConfig(self.suite)}
        self.stepName = "??"
        self.backgroundEnv=[]
        self.stepFilter=stepFilter
        self.noclean=noclean
        self.testExecutor = TestExecutor(path,tel,ydef,config,stepFilter)
#        self.localConfigPaths=[]
        #print(self.config)

    def onDiffCommand(self):   
          
        thisStatus = False
        msg = ""
            
        try:                          
            thisStatus,msg=self.testExecutor.startTestInCurrentDir(self.tel,'diff',self.ydef)            
            if not thisStatus:
                self.tel.error(msg)
        except:
            e = sys.exc_info()
            msg = "{}".format("".join(traceback.format_exception(*e)))   
            thisStatus=False
        return thisStatus,msg
    
    def onUpdateCommand(self):                   
        thisStatus,msg=self.testExecutor.startTestInCurrentDir(self.tel,'update',self.ydef)
        if not thisStatus:
            self.tel.error(msg)
        return thisStatus
        
    def onRunCommand(self):        
        msg=""
        thisStatus = True
        testStartTime = datetime.now().replace(microsecond=0)
        try:
            #kuku
            # time.sleep(0.1)
            # self.tel.startTest(self.testName,self.suite)
            # time.sleep(0.1)
            # now = datetime.now().replace(microsecond=0)
            # testTime = (now - testStartTime).total_seconds()
            # self.tel.endTest(True,self.testName,"OK",self.suite,testTime)
            # return True

        

            self.tel.startTest(self.testName,self.suite)
            # Skip clean when running a single step, but always prepare result directory
            
            if not self.noclean:
                cleanInCurrentDir(AgregatTestExecutionListener()) # empty agregat quiet
                prepareResultInCurrentDir(self.tel)
            #thisStatus,msg = self.startTestInCurrentDir(self.tel,'run',self.ydef)   
            thisStatus,msg = self.testExecutor.startTestInCurrentDir(self.tel,'run',self.ydef)   
            
                  
        except:
            e = sys.exc_info()
            msg = "{}".format("".join(traceback.format_exception(*e)))   
            thisStatus=False

        now = datetime.now().replace(microsecond=0)
        testTime = (now - testStartTime).total_seconds()
        self.tel.endTest(thisStatus,self.testName,msg,self.suite,testTime)        
        return thisStatus

        
    
class AgregatTestExecutionListener():
    def __init__ (self):
        self.agregat =[]
        self.mutex = Lock()
    
    def add(self,item):
        self.agregat.append(item)
        
    def remove(self,item):
        self.agregat.remove(item)
        
    def error(self,msg):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'error'):
                    item.error(msg)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
    
    def cleaning(self,msg):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'cleaning'):
                    item.cleaning(msg)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
    
    def cleanDone(self,status,msg):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'cleanDone'):
                    item.cleanDone(status,msg)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
    
    def startStep(self,testName,stepName,suite):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'startStep'):
                    item.startStep(testName,stepName,suite)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
        
    def startAction(self,name):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'startAction'):
                    item.startAction(name)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
    def startBackground(self):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'startBackground'):
                    item.startBackground()
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
    def background(self,msg):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'background'):
                    item.background(msg)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
    def transcript(self,msg):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'transcript'):
                    item.transcript(msg)
            sys.stdout.flush()
        finally:
            self.mutex.release()

    def log(self,msg):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'log'):
                    item.log(msg)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
    def startTest(self,testName,suite):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'startTest'):
                    item.startTest(testName,suite)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
        
    def endTest(self,status, name,msg,suite,testTime):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'endTest'):
                    item.endTest(status, name,msg,suite,testTime)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
        
    def startDiff(self,testName,src,ref,diffName,stepName,suite):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'startDiff'):
                    item.startDiff(testName,src,ref,diffName,stepName,suite)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
    def stopDiff(self):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'stopDiff'):
                    item.stopDiff()
            sys.stdout.flush()
        finally:
            self.mutex.release()
                        
        
    def diff(self,line,testName,stepName,suite,diffName):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'diff'):
                    item.diff(line,testName,stepName,suite,diffName)
            sys.stdout.flush()
        finally:
            self.mutex.release()
        
    def finish(self, status, time):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'finish'):
                    item.finish(status, time)
            sys.stdout.flush()
        finally:
            self.mutex.release()

        
    def addTest(self, testName):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'addTest'):
                    item.addTest(testName)
        finally:
            self.mutex.release()
            
        
    
    def endStep(self,testName,stepName,suite,status,reason,stepTime):
        self.mutex.acquire()
        try:
            for item in self.agregat:
                if hasattr(item, 'endStep'):
                    item.endStep(testName,stepName,suite,status,reason,stepTime)
            sys.stdout.flush()
        finally:
            self.mutex.release()
            
        
        
class VerboseTestExecutionListener():
    #def __init__(self):
        
    def error(self,msg):
        print('Error: {}'.format(msg))        
    
    def cleaning(self,msg):
        print(msg)
    
    def transcript(self,msg):
        print(msg)
        
        
    def log(self, msg):
        print(msg)
        
    def startTest(self,testName,suite):
        print("start test '{}'".format(testName))
    
    def startDiff(self,testName,src,ref,diffName,stepName,suite):
        print("diff {}/{} {}/{}".format(testName,src,testName,ref))
        
    def diff(self,line,testName,stepName,suite,diffName):
        print(line)

    def finish(self, status, time):
        if status:
            print("Pass.")
        else:
            print("Failed.")
    
class JsonSummaryTestExecutionListener():
    def startTest(self,testName,suite):
        obj = {"event":"startTest","testName":testName, "suite":suite}
        print(json.dumps(obj))

        
    def endTest(self,status,name,msg,suite,testTime):
        obj = {"event":"endTest","testName":name, "suite":suite, "status":status, "testTime":testTime}
        print(json.dumps(obj))
        

    def finish(self, status, time):
        obj = {"event":"finish", "status":status, "testTime":time}
        print(json.dumps(obj))
    
    def addTest(self, testName):
        obj = {"event":"addTest", "testName":testName}
        print(json.dumps(obj))
    
    def error(self,msg):
        obj = {"event":"error", "msg":msg}
        print(json.dumps(obj))


class SummaryTestExecutionListener():
    def __init__ (self):
        self.waiting = 0
        self.inprogress = 0
        self.failed = 0
        self.passed = 0
        self.faliledList=[]
        print("{:<8}{:<8}{:<8}{:<8}".format("Waiting","Runing","Passed","Failed"))
        self.printUpdate()
    
    def printUpdate(self):
        print("\r{:<8}{:<8}{:<8}{:<8}".format(self.waiting,self.inprogress,self.passed,self.failed),end='')
        sys.stdout.flush()
        
            
    def startTest(self,testName,suite):
        self.waiting = self.waiting -1
        self.inprogress = self.inprogress + 1        
        self.printUpdate()
        
        
    def endTest(self,status,name,msg,suite,testTime):
        self.inprogress = self.inprogress - 1
        if (status):
            self.passed = self.passed + 1
        else:
            self.failed = self.failed + 1
            self.faliledList.append({'name':name,'msg':msg})
        self.printUpdate()
        

    def finish(self, status, time):
        print("")
        if len(self.faliledList) > 0:
            print('\nFailed list:')
            for item in self.faliledList:
                print("{} {}".format(item['name'],item['msg']))
               
        if status:
            print("\nPass.")
        else:
            print("\nFailed.")
    
    def addTest(self, testName):
        self.waiting = self.waiting + 1
        if self.waiting < 100:
            self.printUpdate()
    
    def error(self,msg):
        print('Error: {}'.format(msg)) 
    
def parseDiffSpec(spec):
    tmp1 = spec.split("|")
    #mp2 = tmp1[0].split(" ")
    tmp2 = re.split(r'[\n\t\f\v\r ]+', tmp1[0])
    source = tmp2[0]
    reference = tmp2[1]
    sourceFiltered = TEST_RESULT_DIR + os.sep + os.path.basename(source)+".sfiltered"
    referenceFiltered = TEST_RESULT_DIR + os.sep + os.path.basename(reference)+".rfiltered"
    filters = tmp1[1:]
    filters =  [i.strip() for i in filters]
    return filters,source,reference,sourceFiltered,referenceFiltered

    
def filterFile(tel,fin,filters):
    lines=[]
    lineCounter=0;
    try:
        with open(fin) as f:
            while True:
                line = f.readline()
                #print("1-->{}".format(line))
                if not line:
                    #print("-------")
                    break
                line = line.strip()
                #print("2-->{}".format(line))

                line = filters.write(line)
                #print("3-->{}".format(line))

                if line:
                    lines.append(line)
                    lineCounter = lineCounter + 1
                #print("4-->{}".format(line))

            BufferedLines = filters.close()
            if (BufferedLines):
                for item in BufferedLines:
                    lines.append(item)
                    lineCounter = lineCounter + 1
            f.close()
    except IOError:
        tel.error("Could not read file: '{}'".format(fin))
        return False

    if lineCounter == 0:
        tel.error("Filtered file is empty: '{}'".format(fin))
        return False
    
    return True

class BuildInfilter():
    def __init__(self,out):
        self.out=out
    def write(self,line):
        if line.startswith("[bfan]>"):
            return 
        return self.out.write(line)
    def close(self):
        self.out.close()

def loadFilterChain(tel, srcf, reff, filters, suite, configPath):
    fs = srcf
    fr = reff

    fs = BuildInfilter(fs)
    fr = BuildInfilter(fr)

    for filter in filters:
        factory = LoadFilter(filter, suite, configPath)
        
        if not factory:
            tel.error("Unable to load filter: {}".format(filter))
            return None,None
        fs = factory.Filter(fs)
        fr = factory.Filter(fr)
        
    return fs,fr

def isTestcaseStructure(path):
    if not os.path.isfile(path+os.sep+TEST_CONFIG_FILE):
        return False
    return True
   
    
def cleanInCurrentDir(tel):
    path = os.getcwd()
    
    if not isTestcaseStructure(path):
        tel.cleaning("Cleaning '{}'...".format(os.path.basename(path)))        
        tel.cleanDone(False,"Error: The '{}' folder is not a testcase.".format(os.getcwd()))        
        return False
    
    if os.path.isdir(path+os.sep+TEST_RESULT_DIR):
        tel.cleaning("Cleaning '{}'...".format(os.path.basename(path)))
        shutil.rmtree(path+os.sep+TEST_RESULT_DIR)
        tel.cleanDone(True,"OK")
    return True
       
def prepareResultInCurrentDir(tel):
    if os.path.isdir(TEST_SRC_DIR):
        tel.log("coping data...")
        shutil.copytree(TEST_SRC_DIR, TEST_RESULT_DIR, symlinks=False, dirs_exist_ok=True)
    else:
        # No source directory, just ensure result directory exists
        if not os.path.isdir(TEST_RESULT_DIR):
            os.mkdir(TEST_RESULT_DIR)

# Move diff action at the end of step
# Move skip at the begining
def reorderActions(actions):
    diffActions=[]
    reorderedActions=[]
    firstActions=[]
    for action in actions:
        actionName = next(iter(action))
        if actionName == "diff":
            diffActions.append(action)
        elif actionName == "skip":
            firstActions.append(action)
        else:
            reorderedActions.append(action)
            
    reorderedActions = firstActions + reorderedActions + diffActions
        
    return reorderedActions 
    


def listenerFactory(name):
    if name == "compact":        
        return CompactTestExecutionListener()
    elif name == "verbose":
        return VerboseTestExecutionListener()
    elif name == "summary":        
        return SummaryTestExecutionListener()
    elif name == "jsonSummary":        
        return JsonSummaryTestExecutionListener()
    return CompactTestExecutionListener()

def FilterOutBaseOnTag(equation,ydef):
    if len(equation) == 0:
        return True;
    ttags=[];
    
    if "tags" in ydef:
        ttags = ydef['tags'].split(",")
        tequation = replace_tags_with_bools(ttags, equation)
        res = evaluate_boolean_expression(tequation)
        return res
    else:
        return False
            

def readTestDefinition(path):
    try:
        with open(path+os.sep+TEST_CONFIG_FILE) as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except IOError:
        print("Could not read file: '{}'".format(path))
        exit(1)
    except yaml.scanner.ScannerError as e:
        print(e)        
        exit(1)
            
        
def colectTestcasesToExecute(paths,tags):
    testList=[]
    for item in paths:        
        if os.path.isfile(item):
            with open(item) as f:
                while True:
                    testDir = f.readline()
                    testDir = testDir.rstrip()
                    if not testDir:                   
                        break
                    if isTestcaseStructure(testDir):
                        ydef = readTestDefinition(testDir)
                        if FilterOutBaseOnTag(tags,ydef):
                            testList.append({'path':testDir,'ydef':ydef})                      
                    else:
                        print("Error: path in file list is not test dir: '{}'".format(testDir))
                        exit(1)
                f.close()
        elif os.path.isdir(item):
            if isTestcaseStructure(item):
                ydef = readTestDefinition(item)
                if FilterOutBaseOnTag(tags,ydef):
                    testList.append({'path':item,'ydef':ydef})
            else:
                for pathTotest in glob.glob(item+ '/**/def.yaml', recursive=True):
                    fullTestDir=os.path.dirname(pathTotest)
                    if os.path.isfile(fullTestDir):
                        continue
                    if isTestcaseStructure(fullTestDir):   
                        ydef = readTestDefinition(fullTestDir) 
                        if FilterOutBaseOnTag(tags,ydef):
                            testList.append({'path':fullTestDir,'ydef':ydef})        
                    else:                       
                        print ("Error: wrong testcase path: '{}'".format(fullTestDir))
                        exit(1)
        else:
            print ("Error: path is not dir or file: '{}'".format(item))
            exit(1)
    
    return testList
   

def setupenvFromCommandLine(cmdenv, image):
    if image:
        os.environ["BFAN_{}".format("IMAGE")] = image

    if not cmdenv:
        return
    cmdenvSplited=cmdenv.split(',')
    for item in cmdenvSplited:
        itemSplited = item.split('=')
        if len(itemSplited) != 2:
            print("Error while parsing '--env'")
            exit(1)
            continue
        key = itemSplited[0].strip()
        value = itemSplited[1].strip()
        os.environ["BFAN_{}".format(key)] = value



#***********************************************************************
#*                       MAIN                                          *
#***********************************************************************
def main():
    startTime = datetime.now().replace(microsecond=0)  
    arguments = docopt(__doc__, version='bfan 1.0.14')
    setupenvFromCommandLine(arguments['--env'], arguments['--image'])
    
    #print(arguments)
    tags=""
    if arguments['--tags']:
        tags =arguments['--tags']
      
    if arguments['--stdout']:
        verboseTranscript = True
    else:
        verboseTranscript = False

  
    lisnerName = arguments["--view"]
    #[--view verbose | compact | sumary]

    # if arguments["--view"]:
    #     if arguments["compact"]:
    #         lisnerName = "compact"
    #     elif arguments["summary"]:
    #         lisnerName = "summary"
    #     elif arguments["jsonSummary"]:
    #         lisnerName = "jsonSummary"


    if len(arguments['<path>']) == 0 :
        arguments['<path>'] = ['./']
 
    if (not arguments['--arch']):
        arguments['--arch'] = ""


    # if arguments['env']:
    #     pathToBin = os.path.abspath(arguments['<pathToExec>'])
    #     if os.path.isfile(pathToBin):
    #         pathToBin = os.path.dirname(pathToBin)
    #     pathToBtestJson = pathToBin+os.sep+"bfan.json"
    #     if not  os.environ.get('BFAN_BASE'):
    #         base =  os.path.abspath(pathToBin+"../../../../../../")
    #         os.environ['BFAN_BASE'] = base
    #         print("Waring: BFAN_BASE is not defined. But deducted as: {}".format(base))
    #     if not os.path.isfile(pathToBtestJson):
    #         print("Error: file not found: {}".format(pathToBtestJson))
    #         exit(1)
    #     ienv = getInternalEnvironmentVariables(pathToBin, arguments['--arch'],FindConfigPath())
    #     env = readEnvFrombfan_json(ienv,suite)
    #     for key, value in env.items():
    #         print("export {}={}".format(key, value))
    #     exit(0)

 
    testPathToRun = colectTestcasesToExecute(arguments['<path>'], tags)

    if len(testPathToRun) == 0:
        print("Error: no testcases to run.")
        exit(1)
    
    # Validate --step parameter - if --step flag is present but no step name provided
    if arguments['run'] and arguments['--step'] and (arguments['--step'] is None or len(arguments['--step'].strip()) == 0):
        print("Error: --step parameter requires a step name.")
        print("\nAvailable steps:")
        for item in testPathToRun:
            print("\nTest: {}".format(item['path']))
            if 'steps' in item['ydef']:
                for step in item['ydef']['steps']:
                    stepName = next(iter(step))
                    print("  - {}".format(stepName))
            else:
                print("  (no steps defined)")
        exit(1)
        
    status = None
    tel = AgregatTestExecutionListener()

    if lisnerName == None :
        if len(testPathToRun) > 1:
            lisnerName = "summary"
        else:
            lisnerName = "compact"

    
    oldPath = os.getcwd()
    status=True 
    config={}


    if arguments['run']:
        testStarted=False
        tel.add(listenerFactory(lisnerName))
#        if len(testPathToRun) > 1 :

        tel.add(PassFailedFileWiter())
        config["arch"] = arguments['--arch']
 
        if (arguments['--genXml']):
            if (arguments['--outputName']):
                tel.add(JunitGenerator(arguments['--arch'], arguments['--outputName']))
            else:
                tel.add(JunitGenerator(arguments['--arch']))
            
        
        for item in testPathToRun:
            tel.addTest(item)

        oldPath = os.getcwd()

        for item in testPathToRun:           
            os.chdir(item['path'])
            writer = TranscriptWriterListener(verboseTranscript)
            
            tel.add(writer) 
           
            stepName = arguments['--step'].split(',') if arguments['--step'] else None
            
            noclean = arguments.get('--noclean', False)
            testRunner = TestRunner(item,tel,item['ydef'],config,stepName,noclean)
            
            if testRunner.onRunCommand() == False:
                status=False;
            else:
                if arguments['--clearPassed']:
                    cleanInCurrentDir(AgregatTestExecutionListener()) # empty agregat quiet
            tel.remove(writer)
            del writer   
            del testRunner  
            os.chdir(oldPath)  
     
    if arguments['diff']:
        for item in testPathToRun:
            os.chdir(item['path'])
            writer = listenerFactory("verbose")
            tel.add(writer)  
            item = testPathToRun[0]
            
            testRunner = TestRunner(item,tel,item['ydef'],config)
            status,msg = testRunner.onDiffCommand()
            print (msg  )
            tel.remove(writer)
            del writer   
            del testRunner
            os.chdir(oldPath)       

    if arguments['update']:
        if len(testPathToRun) != 1 :
            print("Error: only one test at time can be updated.")
            exit (1)

        item = testPathToRun[0]
        os.chdir(item['path'])
        writer = listenerFactory("verbose")
        tel.add(writer)
        testRunner = TestRunner(item,tel,item['ydef'],config)
        testRunner.onUpdateCommand()
        tel.remove(writer)
        del writer   
        del testRunner
        os.chdir(oldPath)  
        
            
    if arguments['clean']:       
        tel.add(listenerFactory("compact"))
        try:
            for item in testPathToRun:
                os.chdir(item)                
                if not cleanInCurrentDir(tel):            
                    status = False;
                os.chdir(oldPath)                
        except:
            e = sys.exc_info()
            msg = "{}".format("".join(traceback.format_exception(*e)))       
            tel.error(msg)
 
    now = datetime.now().replace(microsecond=0)
    finishTime = (now - startTime).total_seconds()               
    tel.finish(status,finishTime)
    if status:                                                                                       
        exit(0)                                                                                      
    else:   
        exit(1)
 
 
   
#***********************************************************************
#*                       MAIN                                          *
#***********************************************************************
if __name__ == '__main__':
   main()
    
    
#TODO
# kill.bfan - bacground transcript is not generated when kill occure
# kill.bfan - improve this testcase to better test kill




# import re

# def replace_tags_with_bools(tags, equation):
#     # This regex matches words (alphanumeric and underscores) not being 'and', 'or', 'not'
#     # and skips parentheses and operators
#     def replacer(match):
#         word = match.group(0)
#         if word in ['and', 'or', 'not', 'True', 'False']:
#             return word
#         return str(word in tags)

#     # Use regex to replace tag names (words) that are not Python operators
#     return re.sub(r'\b\w+\b', replacer, equation)

# # Example usage:
# tags1 = ["tag1", "tagx", "regression"]
# equation1 = "(tag1 or tagx) and regression"
# print(replace_tags_with_bools(tags1, equation1))
# # Output: "(True or True) and True"

# tags2 = ["regression"]
# equation2 = "gen4 or gen5 or regression"
# print(replace_tags_with_bools(tags2, equation2))
# # Output: "False or False or True"





# def evaluate_boolean_expression(expr: str) -> bool:
#     try:
#         # Evaluate the boolean expression using Python's eval
#         # It's safe here because the input is constrained to boolean logic
#         result = eval(expr)
#         if isinstance(result, bool):
#             return result
#         else:
#             raise ValueError("Expression did not evaluate to a boolean.")
#     except Exception as e:
#         print(f"Error evaluating expression: {e}")
#         return None

# # Example usage:
# print(evaluate_boolean_expression("(True or True) and True"))       # Output: True
# print(evaluate_boolean_expression("False or False or True"))        # Output: True
# print(evaluate_boolean_expression("False or False or not True"))    # Output: False

