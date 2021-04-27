###############################################################################
# test.py
# Testing and debugging code
###############################################################################
import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv()

def template():
    print("testing: ")
    sys.exit()

def boolTest():
    print("testing: boolTest")
    settings = {
        "cachingOn":
            True if os.environ.get('CACHING_ON').lower()=="true" else False
    }
    print(settings)

    sys.exit()

def strJoin():
    print("testing: ")
    ' '.join([str(os.getpid()), 'hi'])
    sys.exit()

def logPrint():
    logging.info(str(os.getpid())+" logPrint")
    sys.exit()

def envVar():
    print("testing: envVar")
    print(print(type(os.environ.get('HOST_ID'))))
    sys.exit()

def runTesting():
    print("RUNNING TEST")

    # # testing: cloneRepo
    # tmpTask = {
    #     'gitHash': 'latest',
    #     'gitBranch': 'testMma'}
    # tmpPathRepo = cloneRepo(tmpTask, conf['dirRoot'])
    # print ("tmpPathRepo:", tmpPathRepo)
    # assert os.path.isdir(tmpPathRepo)

    # # testing: handleHangProcesses
    # handleHangProcesses()
    # sys.exit()

# testing: cloneRepo
    # tmpTask = {
    #     'gitHash': '797094da405a8197b09595b695eb857766b0110b',
    #     'gitBranch': 'dev'}
    # tmpWd, tmpPathRepo = cloneRepo(tmpTask, conf['dirRoot'])
    # assert os.path.isdir(tmpPathRepo)
    # sys.exit()

# testing: readCacheMmaObjs
    # tmp = readCacheMmaObjs(
    #     ['gradeStyle'],
    #     ['gradeBasicAlgebra'],
    #     ['id','mma_id','gradeStyle'])
    # tmp = readCacheMmaObjs(
    #     ['id'],
    #     [2],
    #     ['id','mma_id','limitMmaTime']
    # )[0]
    # print(tmp)
    # print("limitMmaTime" in tmp.keys())
    # print("limitMmaTime:", tmp['limitMmaTime'])
    # print("int?:", isinstance(tmp['limitMmaTime'], int))
    # sys.exit()

# # testing: mkImage
#     tmpTask = {
#         'gitHash': '4e04a538420656d8932df450dff6ccf9038e03c8',
#         'gitBranch': 'cacheServer'}
#     tmpwrkDir = os.path.join(conf['dirRoot'], tmpTask['gitHash'])
#     tmpPathRepo = cloneRepo(tmpTask, tmpwrkDir)
#     assert os.path.isdir(tmpPathRepo)
#     print(os.getpid(), "The repo path: "+tmpPathRepo)
#     mkImage(tmpwrkDir, scrptDflt='/Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/mkCacheImg.wl')
#     sys.exit()

# # testing: runCaching()
#     tmpIdx = 5
#     tmpGitHash = '4f9d8916979d0f350fb4394fd708a296df5f59a1'
#     tmpLimit = 60
#     tmpLimitSteps = 1
#     tmpImgOnQ = False
#     tmpWrkDir = '/Users/evan/Documents/work/querium/coding/mma/CommonCore'
#     tmpImg = '/path/to/images/cacheImg.mx'
#     updateCacheMmaTbl(tmpIdx,
#     ["status","gitBranch", "gitHash", "gitRedis", "limitSteps", "limitStepTime"],
#     ["pending", "cacheServer", tmpGitHash, tmpGitHash, tmpLimitSteps, tmpLimit])
#     tmpTask = readCacheMmaObjs(
#         ["id"],
#         [tmpIdx],
#         [
#             'id','question_id','mma_id','gradeStyle','policies','limitStepTime',
#             'limitSteps',
#             'limitMmaTime','cachingOrder','hintL','showMeL','stepCount',
#             'stepsCompleted','timeCompleted','gitBranch','gitHash','gitRedis',
#             'timeOutTime','ruleMatchTimeOutTime','clearOldCacheQ','modQidType'
#         ]
#     )[0]
#     tmpTask.update(conf)
#     tmpTask['dirCommonCore'] = tmpWrkDir
#     tmpTask['loadFromImgOn'] = tmpImgOnQ
#     tmpTask['img'] = tmpImg
#     print(os.getpid(), tmpTask)

#     updateCacheMmaTbl(2,["status", "pid"],["aquired", os.getpid()])
#     runCaching(os.path.join(tmpWrkDir, conf["scriptCaching"]), tmpTask)
#     sys.exit()

# # testing: getPendingMmaGit
#     tmpPendingTask = getPendingMmaObj()
#     print(tmpPendingTask)
#     print("len:", len(tmpPendingTask)<1)
#     sys.exit()

# # testing
#     conf['pathToCommonCore'] = "/path/to/CommonCore"
#     conf['pathToCachingImg'] = "/path/to/cachingImg"
#     subprocess.run([
#         "/Applications/Mathematica.app/Contents/MacOS/WolframScript",
#         "-script",
#         "/Users/evan/Documents/work/querium/coding/mma/CommonCore/runTmp.wl",
#         json.dumps(conf)])
#     sys.exit()

# testing
    # updateCacheMmaTbl(
    #     5,
    #     ["status", "gitBranch", "gitHash", "gitRedis"],
    #     [
    #         "pending", "cacheServer",
    #         "10c8700ab80a596a9cf106172e2a4a54965fb2e4",
    #         "10c8700ab80a596a9cf106172e2a4a54965fb2e4"
    #     ]
    # )
    # sys.exit()
    # updateCacheMmaTbl(3,
    # ["status", "pid", "gitBranch", "gitHash", "gitRedis"],
    # ["running", 16507, "cacheServer", "66b07f2e233ad7d88799d9df526a1e2f1866e432", "9814af5075ba4dba5a870d6a0aa355c66a4d6bd2"])
    # sys.exit()

    sys.exit()


def dotEvn():
    print(os.environ.get('DIR_ROOT'))
    print(os.environ.get('HOST_ID'))
    print(os.environ.get('SLEEPTIME'))
    print(os.environ.get('DB_HOST'))
    print(os.environ.get('CACHING_ON'))
    print(os.environ.get('REDIS_ON'))
    print(os.environ.get('WOLFRAMSCRIPT'))
    print(os.environ.get('JOB_LIMIT'))


if __name__ == '__main__':
    dotEvn()