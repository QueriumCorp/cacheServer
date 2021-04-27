###############################################################################
# xxx

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install PyMySQL
# python3 -m pip install psutil
# python3 -m pip install gitpython

# run the program:
# python3 triggerCaching.py /path/to/configFile.json
# Evan
# python3 /Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/cacheServer.py /Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/config/configEvan.json
# ai00
# python3 /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/cacheServer.py /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/config/config_ai00.json
# python3 /usr/local/bin/cacheServer /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/config/config_ai00.json

# NOTE:
# Design document
# https://docs.google.com/document/d/1Pe4SdHZVSr9Tpgg20RIif1SNmAaDdlfeEazZNaeltDw/edit?usp=sharing
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import json
import pymysql
import time
import sys
import psutil
import os, signal
from datetime import datetime
import git
import math
import multiprocessing
import subprocess
from subprocess import TimeoutExpired
import shutil
import test
import logging
logging.basicConfig(level=logging.DEBUG)

###############################################################################
# Global Variables
###############################################################################
# CMDLENGTH = 4
CMDLENGTH = 2
# CACHESCRIPT = 'runPrecompCache.m'
# CACHESCRIPT = 'runCaching.m'
CACHESCRIPT = 'sleeping.py'
TIMELIMIT = 600
WAITTIME = 10

TESTSCRIPT = "/tmp/testLicense.wl"
TESTLICENSE = "22222+33333"
TESTRESULT = "55555"

EXITCODE_NOMMA = 5
EXITCODE_NOLICENSE = 6
EXITCODE_IMGFAIL = 7
EXITCODE_REPOFAIL = 8
EXITCODE_BADMAINPATH = 9
EXITCODE_INVALIDREF = 10

###############################################################################
#   Support functions
###############################################################################
def readJson(file):
    with open(file) as fd:
        return json.load(fd)

###
#  args: [id, pid, started, limitMmaTime]
###
def killItQ(args):
    ## if pid is not set, can't kill pid
    if args[1] == -1:
        print(args[0],"killItQ - pid is NOT set")
        return(False)

    ## if started timestamp is not set, can't kill pid
    if args[2] == None:
        print(args[0], "killItQ - started is NOT set")
        return(False)

    ## if limitMmaTime is not set, use the default value of TIMELIMIT
    limitMmaTime = args[3]
    if args[3] is None:
        print(args[0], "killItQ - limitMmaTime is not set" +
            ", using the default of "+TIMELIMIT)
        limitMmaTime = TIMELIMIT

    ## does the process still exist?
    if not psutil.pid_exists(args[1]):
        print(args[0], args[1], "killItQ - does not exist")
        updateCacheMmaTbl(args[0],
            ["status", "msg"],
            [
                "notFound",
                "pid wasn't found on HOST_ID: "+os.environ.get("HOST_ID")
            ]
        )
        return(False)

    ## if pid is not a caching process, return False
    pro = psutil.Process(args[1])
    if len(pro.cmdline())!=CMDLENGTH or CACHESCRIPT not in pro.cmdline():
        print(args[0], args[1], "killItQ - doesn't fit the description")
        return(False)

    ## if a caching process has been running within limitMmaTime, return False
    timeDelta = datetime.now()-args[2]
    if timeDelta.total_seconds() < limitMmaTime:
        return(False)

    return True

def updateCacheMmaTbl(id, cols, vals):
    conn = pymysql.connect(
        os.environ.get("DB_HOST"), os.environ.get("DB_USER"),
        os.environ.get("DB_PASS"), os.environ.get("DB_NAME"),
        use_unicode=True, charset="utf8")

    sqlSet = "=%s, ".join(cols)+"=%s"
    sql = "UPDATE cache_mma SET "+sqlSet+" WHERE id=%s"

    sqlVals = tuple(vals + [id])
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, sqlVals)
            conn.commit()
    except pymysql.Error as er:
        print("updateKilledProInTbl: Unable to update")
        print(er)
    finally:
        conn.close()

    return id

def readCacheMmaTbl(cols, vals, colsRtrn, fltr=''):
    conn = pymysql.connect(
        os.environ.get("DB_HOST"), os.environ.get("DB_USER"),
        os.environ.get("DB_PASS"), os.environ.get("DB_NAME"),
        use_unicode=True, charset="utf8")

    sqlFldsRtrn = ",".join(colsRtrn)
    sqlCond = "=%s AND ".join(cols)+"=%s "
    sql = "SELECT "+sqlFldsRtrn+" FROM cache_mma WHERE "+sqlCond+fltr
    logging.debug("readCacheMmaTbl: "+sql)
    sqlVals = tuple(vals)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, sqlVals)
            rslt = cursor.fetchall()
    except pymysql.Error as er:
        logging.warning(str(os.getpid())+" readCacheMmaTbl: Unable to read")
    finally:
        conn.close()

    return rslt

def readCacheMmaObjs(cols, vals, colsRtrn, fltr=''):
    data = readCacheMmaTbl(cols, vals, colsRtrn, fltr)

    return(list(map(lambda aRow: dict(zip(colsRtrn, aRow)), data)))

def mkWolfFile():
    if not os.path.isfile(os.environ.get('LICENSE_FILE')):
        with open(os.environ.get('LICENSE_FILE'), "w") as fd:
            fd.write("Print["+os.environ.get('LICENSE_TEST')+"]")

def checkoutRef(repo, aRef):
    refBranch = str(math.ceil(time.time()))
    print(os.getpid(),'checking out a ref:', aRef)
    # newBranch = repo.create_head(refBranch, aRef)
    # print("newBranch:", newBranch)
    try:
        newBranch = repo.create_head(refBranch, aRef)
        print(os.getpid(),'created a branch for the ref: '+refBranch)
    except git.BadName as err:
        print(os.getpid(), "invalid git ref:", aRef)
        return False
        # print(os.getpid(), err)
    except ValueError as err:
        print(os.getpid(), "checkoutRef: ValueError:", aRef)
        return False

    repo.heads[refBranch].checkout()
    assert repo.active_branch.commit.hexsha == aRef

    return True

def getPendingMma(fltr=""):
    cols = [
        'id',
        'question_id',
        'mma_id',
        'gradeStyle',
        'qsh',
        'policies',
        'limitStepTime',
        'limitSteps',
        'limitMmaTime',
        'cachingOrder',
        'hintL',
        'showMeL',
        'gitCacheOn',
        'gitHash',
        'gitBranch',
        'gitRedis',
        'timeOutTime',
        'ruleMatchTimeOutTime',
        'clearOldCacheQ',
        'modQidType'
    ]

    rslt = readCacheMmaObjs(
        ['host_id','status'],
        [os.environ.get("HOST_ID"), 'pending'],
        cols,
        fltr
    )
    return rslt

## Prep a JSON argument for Mathematica. Depending on an OS, the argment needs
## to be encoded twice (linux) or once (darwin - MacOS)
def prepArg(arg):
    if sys.platform == 'linux':
        return json.dumps(json.dumps(arg, separators=(',', ':')))

    return json.dumps(arg, separators=(',', ':'))

def on_terminate(proc):
    print("process {} terminated with exit code {}".format(proc, \
                                                           proc.returncode))

###############################################################################
#   Get a pending task of HOST_ID from cache_mma
#   Returns: a task dictionary with fields listed in getPendingMma()
###############################################################################
def getPendingMmaObj():
    data = getPendingMma(fltr='ORDER BY RAND() LIMIT 1')

    if len(data)>0:
        return data[0]

    return({})

def getPendingMmaMany():
    return(getPendingMma())

def strToBool(str):
    return True if str.lower()=="true" else False

###############################################################################
#   Get settings from environment
###############################################################################
def getImgSettings():
    settings = {
        "cachingOn": strToBool(os.environ.get('CACHING_ON')),
        "jsonResponse": strToBool(os.environ.get('JSON_RESPONSE')),
        "redisOn": strToBool(os.environ.get('REDIS_ON')),
        "saveStateInStateOn": strToBool(os.environ.get('SAVESTATEINSTATE_ON')),
        "autoCachingOn": strToBool(os.environ.get('AUTOCACHING_ON')),
        "redisConnTime": int(os.environ.get('REDIS_CONNTIME')),
        "loadFromImgOn": strToBool(os.environ.get('LOADFROMIMG_ON'))
    }

    return settings

###############################################################################
#   If the CommonCore repo (/path/gitHash) already exists on
#   the server, use it. Otherwise, clone it from GitHub.
#   NOTE: the server needs to have github authentication to Querium via ssh
#   Parameters:
#   task: getPendingMmaObj()
#   path: root cache directory
#   Returns:
#   - a full path to CommonCore repo on success
#   - False on fails
###############################################################################
def cloneRepo(task, path, repoName='CommonCore'):
    ## Repo may already present
    wrkPath = os.path.join(path, task['gitHash'])
    wrkRepoPath = os.path.join(wrkPath, repoName)
    if task['gitHash'] != "latest" and os.path.isdir(wrkRepoPath):
        logging.info(str(os.getpid())+" The repo is already present")
        return wrkPath, wrkRepoPath

    ## Update the main repo
    mainPath = os.path.join(path, 'main')
    if not os.path.isdir(mainPath):
        os.mkdir(mainPath)
        logging.info(str(os.getpid())+" Created the main repo directory")

    ## If the main repo doesn't exist, clone it
    mainRepoPath = os.path.join(mainPath, repoName)
    logging.info("mainRepoPath: "+ mainRepoPath)
    if not os.path.isdir(mainRepoPath):
        logging(str(os.getpid()), " Cloning the repo .....")
        repo = git.Repo.clone_from(
            os.environ.get("REPO_URL"),
            mainRepoPath,
            branch=task['gitBranch']
        )
        ## Validate the repo
        assert repo.active_branch.name == task['gitBranch']

    ## Update the main repo reference to the latest codebase on gitBranch
    mainRepo = git.Repo(mainRepoPath)
    for remote in mainRepo.remotes:
        remote.fetch()
    if task['gitHash'] == "latest":
        mainRepo.git.checkout(task['gitBranch'])
        mainRepo.git.pull()
        logging.info(
            str(os.getpid())+" Pulled the latest code on "+task['gitBranch'])

        ## Return the repo path if it already there
        wrkPath = os.path.join(path, mainRepo.active_branch.commit.hexsha)
        wrkRepoPath = os.path.join(wrkPath, repoName)
        if os.path.isdir(wrkRepoPath):
            logging.info(str(os.getpid())+" The repo is already present")
            return wrkPath, wrkRepoPath
    else:
        ## Checkout a gitHash ref
        if not checkoutRef(mainRepo, task['gitHash']):
            sys.exit(EXITCODE_INVALIDREF)
    logging.info(str(os.getpid())+' Codebase: '+mainRepo.active_branch.commit.hexsha)

    ## Return the repo path if it already there
    wrkPath = os.path.join(path, mainRepo.active_branch.commit.hexsha)
    wrkRepoPath = os.path.join(wrkPath, repoName)
    if task['gitHash'] == mainRepo.active_branch.commit.hexsha and \
        os.path.isdir(wrkRepoPath):
        logging.info(str(os.getpid())+" The repo is already present")
        return wrkPath, wrkRepoPath

    ## Create a working directory for commitHash
    wrkPath = os.path.join(path, mainRepo.active_branch.commit.hexsha)
    wrkRepoPath = os.path.join(wrkPath, repoName)
    # print ("wrkPath:", wrkPath)
    if not os.path.isdir(wrkPath):
        os.mkdir(wrkPath)
        destination = shutil.copytree(mainRepoPath, wrkRepoPath)
        return wrkPath, destination

    if not os.path.isdir(wrkRepoPath):
        destination = shutil.copytree(mainRepoPath, wrkRepoPath)
        return wrkPath, destination

    return False

###############################################################################
#   Handle expired process: if a caching process has been running longer than
#   current time - started time > limitMmaTime
###############################################################################
def handleExpiredProcesses():
    rslt = readCacheMmaTbl(
        ['host_id','status'],
        [os.environ.get("HOST_ID"), "running"],
        ['id','pid','started','limitMmaTime'],
        fltr='ORDER BY started'
    )
    # print(rslt)

    for info in rslt:
        if(killItQ(info)):
            logging.info(
                str(info[0])+": "+str(info[1])+
                " has been running too long - killing it"
            )
            os.kill(info[1], signal.SIGKILL)
            updateCacheMmaTbl(
                info[0],
                ['status', 'finished', 'msg'],
                ["killed", datetime.now(), "run too long"]
            )

###############################################################################
#   Handle hang Mathematica processes: Some caching process are not terminating
#   gracefully. These processes continue to exist and consume resource. They
#   should be killed.
###############################################################################
def handleHangProcesses():
    ## get pids of this host from cache_mma that completed their task
    ## successfully and started time is in last HANGTIME hours
    fltrCus = 'AND started > DATE_ADD(NOW(), INTERVAL-'
    fltrCus += os.environ.get("HANGTIME")
    fltrCus += ' HOUR) ORDER BY started'
    pidsInDb = readCacheMmaObjs(
        ['host_id','status'],
        [os.environ.get("HOST_ID"), "success"],
        ['id','pid'],
        fltr=fltrCus
    )
    # print ("Hang check:", pidsInDb)

    ## if any of these pids are still running or hang, terminate them
    hangProcs = []
    for p in psutil.process_iter():
        if 'WolframKernel' not in p.name():
            continue
        if 'runCaching.wl' not in ' '.join(p.cmdline()):
            continue

        ## filter pids in cache_mma by runCaching pid
        info = list(filter(lambda x: x['pid']==p.pid, pidsInDb))
        if len(info)<1:
            continue

        logging.info("Terminating: "+str(p.pid))
        p.terminate()
        hangProcs.append(p)
        now = datetime.now()
        updateCacheMmaTbl(
            info[0]['id'],
            ["status", "finished"],
            ["successButHang", now]
        )
        logging.info("Updated "+str(info[0]['id'])+
               ": (status,finished) ->"+
               "(successButHang,"+now.strftime("%m-%d-%Y %H:%M:%S")+")")


    ## if no matches, return
    if len(hangProcs) < 1:
        # print ("No hang process")
        return True

    ## wait WAITTIME seconds for the hang processes to terminate
    gone, alive = psutil.wait_procs(hangProcs, timeout=WAITTIME,
                                    callback=on_terminate)
    logging.info("Gone: "+str(len(gone)))
    logging.info("Alive: "+str(len(alive)))

    ## kill the hanging processes that are still alive
    for p in alive:
        logging.info("Still alive - killing it: "+str(p.pid))
        p.kill()


###############################################################################
#   Check for Mathematica license availability
###############################################################################
def aquireLicenseQ():
    ## make a temp test file
    mkWolfFile()

    ## Run wolframScript to test Mathematica license availability
    try:
        rslt = subprocess.check_output([
            os.environ.get("WOLFRAMSCRIPT"),
            "-script",
            os.environ.get('LICENSE_FILE')], timeout=5
        )
    except subprocess.TimeoutExpired as er:
        logging.warning(str(os.getpid())+" AquireLicenseQ: TimeoutExpired")
        return False

    if os.environ.get('LICENSE_RSLT') not in rslt.decode("utf-8"):
        logging.warning(str(os.getpid())+" License is NOT available")
        return False

    return True

###############################################################################
#   If any processes are dead, remove them from JOBS
#   NOTE: the JOBS are processes that are running cache script in Mathematica.
#   Number of JOBS limited to number of Mathematica licenses available
###############################################################################
def manageJobs():
    ## Locate dead jobs
    idxOfDead = []
    for i in range(len(JOBS)):
        # print(i, 'JOBS[i]:', JOBS[i])
        if not JOBS[i].is_alive():
            logging.info(str(i)+" Job is DEAD")
            idxOfDead.append(i)
        else:
            logging.info(str(i)+ " Job is ALIVE")

    ## Pop the dead jobs in the descending order by their index:
    ## largest to smallest index, Otherwise, running processes can get popped
    idxOfDead.sort(reverse=True)
    # print('idxOfDead:', idxOfDead)
    for i in idxOfDead:
        JOBS.pop(i)

###############################################################################
#   Make an image of StepWise for caching. The image will be created under
#   images directory
#   Parameters:
#   path: full directory where images directory will be
#   [scrptDflt]: Mathematica script that generates caching image can be
#       specified. Otherwise: an imaging script should be located:
#       /path/CommonCore/SCRIPT_MKIMG or
#       /DIR_ROOT/gitHash/CommonCore/SCRIPT_MKIMG
###############################################################################
def mkImage(path, scrptDflt="", timeDflt=300):

    ## If the image directory doesn't exist, create one
    dirImg = os.path.join(path, 'images')
    if not os.path.isdir(dirImg):
        logging.info(str(os.getpid())+" StepWise image dir: "+dirImg)
        os.mkdir(dirImg)

    ## If the cache image is present, no need to generate again
    fileCacheImg = os.path.join(dirImg, os.environ.get('FILEIMG'))
    if os.path.isfile(fileCacheImg):
        logging.info(
            str(os.getpid())+" StepWise image already exists:"+fileCacheImg)
        return fileCacheImg

    ## Make an argument for making image
    args = getImgSettings()
    args["dirCommonCore"] = os.path.join(path, 'CommonCore')
    args["img"] = fileCacheImg

    ## If the cache image isn't present, generate one
    script = os.path.join(args["dirCommonCore"], os.environ.get('SCRIPT_MKIMG'))
    if scrptDflt != "":
        script = scrptDflt
    if not os.path.isfile(script):
        logging.warning(
            str(os.getpid())+" Make image script doesn't exist:"+script)
        return False

    ## Run the imaging script to generate a StepWise image
    try:
        subprocess.run(
            [os.environ.get('WOLFRAMSCRIPT'), "-script", script, prepArg(args)],
            timeout=timeDflt, check=True
        )
    except subprocess.CalledProcessError as err:
        logging.warning("Error (mkImage): "+err)
        return False
    except TimeoutExpired as err:
        logging.warning("Error (mkImage): "+err)
        return False

    ## Verify the image was created
    if os.path.isfile(fileCacheImg):
        return fileCacheImg

    return False

###############################################################################
#   Cache a task
#   Parameters:
#   script: a full path to a caching script
#   task: dictionary of (conf + a pending task from cache_mma)
###############################################################################
def runCaching(script, task, timeDflt=3605):
    ## Validate the script's existence
    if not os.path.isfile(script):
        logging.info(str(os.getpid())+" Caching script doesn't exist: "+script)
        return False

    ## configure timeout
    timeLimit = timeDflt
    if "limitMmaTime" in task.keys() and isinstance(task['limitMmaTime'], int):
        timeLimit = task['limitMmaTime']+5

    ## Run the caching script
    try:
        subprocess.run(
            [os.environ.get('WOLFRAMSCRIPT'),"-script", script, prepArg(task)],
            timeout=timeLimit, check=True
        )
    except subprocess.CalledProcessError as err:
        logging.warning("Error (runCaching): "+err)
    except TimeoutExpired as err:
        logging.warning("Error (runCaching): "+err)

###############################################################################
#   Determine whether to start a new process or not
###############################################################################
def pullTriggerQ():
    pullQ = False
    while not pullQ:
        ## Kill Mathematica processes that got stuck
        handleExpiredProcesses()

        ## Kill Mathematica processes that are hang after completing their tasks
        handleHangProcesses()

        ## Manage current jobs
        manageJobs()
        if len(JOBS)>=int(os.environ.get('JOB_LIMIT')):
            logging.info('Reached jobLimit: '+os.environ.get('JOB_LIMIT'))
            time.sleep(int(os.environ.get('SLEEPTIME')))
            continue

        ## Check any pending tasks in cache_mma
        if len(getPendingMmaObj())>0:
            pullQ = True
        else:
            # print('Waiting for a task .....')
            time.sleep(int(os.environ.get('SLEEPTIME')))

    return True

###############################################################################
#   New process
###############################################################################
def trigger(lock):
    logging.info(str(os.getpid())+' Starting a JOB')

    runCachingQ = True
    lock.acquire()
    try:
        ## Is there a Mathematica license
        if not aquireLicenseQ():
            sys.exit(EXITCODE_NOLICENSE)

        ## Get a pending mma info
        task = getPendingMmaObj()
        if len(task)<1:
            sys.exit(EXITCODE_NOMMA)

        ## Update id's status='aquired'
        updateCacheMmaTbl(task['id'], \
            ['pid', 'status'], [os.getpid(), 'acquired'])

        ## cloneRepo returns
        ## /path/to/[ref] and /path/to/[ref]/CommonCore if the repo was created
        ## successfully. Otherwise, it returns False
        wrkDir, pathRepo = cloneRepo(task, os.environ.get('DIR_ROOT'))
        logging.info(str(os.getpid())+" The working dir: "+wrkDir)
        if pathRepo is False:
            sys.exit(EXITCODE_REPOFAIL)
        logging.info(str(os.getpid())+" The repo path: "+pathRepo)

        ## Make StepWise image for caching. mkImage returns a full path to an
        ## image file. Otherwise, it is False
        fFileImg = mkImage(wrkDir)
        if fFileImg is False:
            sys.exit(EXITCODE_IMGFAIL)
    except SystemExit as e:
        if e.code == EXITCODE_NOMMA:
            logging.warning(str(os.getpid())+' No pending mma')
        if e.code == EXITCODE_NOLICENSE:
            logging.warning(str(os.getpid())+' No Mathematica license')
        if e.code == EXITCODE_IMGFAIL:
            logging.warning(
                str(os.getpid())+' Failed on making the cache image')
        if e.code == EXITCODE_REPOFAIL:
            logging.warning(str(os.getpid())+' Failed on cloning the repo')
        if e.code == EXITCODE_BADMAINPATH:
            logging.warning(str(os.getpid())+' Invalid main path')
        runCachingQ = False
    finally:
        lock.release()

    ## Start the caching code in Mathematica
    if runCachingQ:
        ## update the task dict with conf
        task.update(getImgSettings())
        task['dirCommonCore'] = pathRepo
        task['img'] = fFileImg

        ## Build a fullpath to caching script and run it
        scriptCaching = os.path.join(pathRepo, os.environ.get('SCRIPT_CACHING'))
        runCaching(scriptCaching, task)

    logging.info(str(os.getpid())+' ENDING the job')


###############################################################################
#   Main
###############################################################################
logging.info("\nCURRENT RUN: "+time.strftime("%c"))

#########################
#   Testing
#########################
test.boolTest()

if __name__ == '__main__':
    ## Create DIR_ROOT directory if it isn't already there
    if not os.path.isdir(os.environ.get('DIR_ROOT')):
        logging.info("Created DIR_ROOT: "+os.environ.get('DIR_ROOT'))
        os.mkdir(os.environ.get('DIR_ROOT'))

    ## Create a lock for handling critical section among multiple processes
    lock = multiprocessing.Lock()
    ## Keeping track of the number of processes(JOBS). It's needed for Mathematica
    ## license limit
    JOBS = []
    ## Start a new JOB if there is a pending task and a Mathematica license
    while pullTriggerQ():
        aJob = multiprocessing.Process(target=trigger, args=(lock,))
        JOBS.append(aJob)
        aJob.start()