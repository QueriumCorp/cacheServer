###############################################################################
# xxx

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install PyMySQL

# run the program:
# python3 cleanCacheMma.py /path/to/configFile.json
# Evan
# python3 /Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/cleanCacheMma.py /Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/config/configEvan.json
# ai00
# python3 /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/cleanCacheMma.py /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/config/config_ai00.json
# python3 /usr/local/bin/cleanCacheMma /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/config/config_ai00.json

# Crontab on ai00: at 03:03 on every Saturday in Austin time
# 03 22 * * 6 nohup python3 /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/cleanCacheMma.py /var/lib/tomcat8/webapps/webMathematica/api/CommonCore/cronjob/cacheServer/config/config_ai00.json >> /var/lib/tomcat8/webapps/webMathematica/api/logs/cleanCacheMma_`date +\%m\%d`.log

# NOTE:
# Design document
# https://docs.google.com/document/d/1Pe4SdHZVSr9Tpgg20RIif1SNmAaDdlfeEazZNaeltDw/edit?usp=sharing
###############################################################################
import json
import pymysql
import time
import sys
import os, signal
from datetime import date, timedelta

###############################################################################
# Global Variables
###############################################################################
# CMDLENGTH = 4
CMDLENGTH = 2

EXITCODE_NOMMA = 5
EXITCODE_NOLICENSE = 6
EXITCODE_IMGFAIL = 7
EXITCODE_REPOFAIL = 8
EXITCODE_BADMAINPATH = 9

###############################################################################
#   Support functions
###############################################################################
def readJson(file):
    with open(file) as fd:
        return json.load(fd)

###############################################################################
#   Delete cache_mma entries that were created x days ago
###############################################################################
def cleanCacheMma(days):
    conn = pymysql.connect(
        conf["db_host"], conf["db_user"],
        conf["db_pass"], conf["db_database"],
        use_unicode=True, charset="utf8")

    sql = "DELETE FROM cache_mma WHERE created < NOW() - INTERVAL %s DAY"
    # sql = "SELECT created from cache_mma WHERE created < NOW() - INTERVAL %s DAY"
    # print(sql)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, days)
            conn.commit()
    except pymysql.Error as er:
        print("readCacheMmaTbl: Unable to read")
        print(er)
    finally:
        conn.close()

###############################################################################
#   Testing and debugging
###############################################################################
def runTesting():
    print("RUNNING TEST")

    sys.exit()


###############################################################################
#   Main
###############################################################################
print("\nCURRENT RUN: " + time.strftime("%c"))

#########################
#   Handle Configuration
#########################
## Validate arguments
if len(sys.argv) < 2 or len(sys.argv) > 2:
    print ("Valid command:\npython3 /path/to/cleanCacheMma /path/to/config.json")
    sys.exit()

## Make sure the config argument is a valid file
if not os.path.isfile(str(sys.argv[1])):
    print ("Not a valid file: "+sys.argv[1])
    sys.exit()

if __name__ == '__main__':

    ## Read the configuration file
    conf = readJson(str(sys.argv[1]))
    print(json.dumps(conf, indent=4))

    ## Run testing
    # runTesting()

    ## Clean cache_mma after cleanAfter days
    if "cleanAfter" in conf.keys():
        cleanCacheMma(conf["cleanAfter"])
    else:
        cleanCacheMma(30)