# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import sys
import subprocess
import logging
import utilsunit
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal
from bots.botsconfig import *

if sys.version_info[0] > 2:
    basestring = unicode = str

# plugin unitretry.zip
# activate routes
# not an acceptance test
# ftp server needs to be activated (plain ftp, port 21)
# before running: delete all transactions.!!!
""" input: mime (complex structure); 2 different edi attachments, and ' tekst' attachemnt
    some user scripts are written in this unit test; so one runs errors will occur; write user script which prevents error in next run
    runs OK if no errors in unit tests; that is : no exceptions are raised. The bots-engine runs do give errors, but this is needed for retries
"""


def change_communication_type(idchannel, to_type):
    botslib.changeq(
        """UPDATE channel
                        SET type = %(to_type)s
                        WHERE idchannel = %(idchannel)s
                        """,
        {"to_type": to_type, "idchannel": idchannel},
    )


def scriptwrite(path, content):
    f = open(path, "w")
    f.write(content)
    f.close()


def indicate_rereceive():
    count = 0
    for row in botslib.query(
        """SELECT idta
                            FROM    filereport
                            ORDER BY idta DESC
                            """
    ):
        count += 1
        botslib.changeq(
            """UPDATE filereport
                            SET retransmit = 1
                            WHERE idta=%(idta)s
                            """,
            {"idta": row[str("idta")]},
        )
        if count >= 2:
            break


def indicate_send():
    count = 0
    for row in botslib.query(
        """SELECT idta
                            FROM    ta
                            WHERE status=%(status)s
                            ORDER BY idta DESC
                            """,
        {"status": EXTERNOUT},
    ):
        count += 1
        botslib.changeq(
            """UPDATE ta
                            SET retransmit = %(retransmit)s
                            WHERE idta=%(idta)s
                            """,
            {"retransmit": True, "idta": row[str("idta")]},
        )
        if count >= 2:
            break


if __name__ == "__main__":
    pythoninterpreter = "python2.7"
    botsinit.generalinit("config")
    utilsunit.dummylogger()
    botsinit.connect()

    #############route unitretry_automatic###################
    # channel has type file: this goes OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 1482:
        raise Exception("1 filesize not OK: %s" % row["filesize"])
    # change channel type to ftp: errors (run twice)
    change_communication_type("unitretry_automatic_out", "ftp")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 2,
            "lasterror": 2,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 2,
            "lasterror": 2,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 4,
            "lasterror": 0,
            "lastdone": 4,
            "lastok": 0,
            "lastopen": 0,
            "send": 4,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # run automaticretrycommunication again: no new run is made, same results as last run
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 4,
            "lasterror": 0,
            "lastdone": 4,
            "lastok": 0,
            "lastopen": 0,
            "send": 4,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 1482:
        raise Exception("2 filesize not OK: %s" % row["filesize"])
    # rereceive last 2 files
    indicate_rereceive()
    subprocess.call([pythoninterpreter, "bots-engine.py", "--rereceive"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 1482:
        raise Exception("3 filesize not OK: %s" % row["filesize"])
    # resend last 2 files
    indicate_send()
    subprocess.call([pythoninterpreter, "bots-engine.py", "--resend"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report

    # ***run with communciation errors, run OK, communciation errors, run OK, run automaticretry
    # change channel type to ftp: errors
    change_communication_type("unitretry_automatic_out", "ftp")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 2,
            "lasterror": 2,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 1482:
        raise Exception("4 filesize not OK: %s" % row["filesize"])
    # change channel type to ftp: errors
    change_communication_type("unitretry_automatic_out", "ftp")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 2,
            "lasterror": 2,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 1482:
        raise Exception("5 filesize not OK: %s" % row["filesize"])
    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 4,
            "lasterror": 0,
            "lastdone": 4,
            "lastok": 0,
            "lastopen": 0,
            "send": 4,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # change channel type to ftp: errors
    change_communication_type("unitretry_automatic_out", "ftp")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 2,
            "lasterror": 2,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [
            pythoninterpreter,
            "bots-engine.py",
            "unitretry_automatic",
            "unitretry_automatic3",
        ]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 1482:
        raise Exception("6 filesize not OK: %s" % row["filesize"])
    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type("unitretry_automatic_out", "file")
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report

    #############route unitretry_mime: logic for mime-handling is different for resend
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 1,
            "lasterror": 0,
            "lastdone": 1,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 741:
        raise Exception("7 filesize not OK: %s" % row["filesize"])
    # change channel type to ftp: errors (run twice)
    change_communication_type("unitretry_mime_out", "ftp")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 1,
            "lasterror": 1,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    change_communication_type("unitretry_mime_out", "ftp")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 1,
            "lasterror": 1,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 741:
        raise Exception("8 filesize not OK: %s" % row["filesize"])
    # change channel type to mimefile and do automaticretrycommunication: OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report

    # run automaticretrycommunication again: no new run is made, same results as last run
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 1,
            "lasterror": 0,
            "lastdone": 1,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 741:
        raise Exception("9 filesize not OK: %s" % row["filesize"])

    # ***run with communciation errors, run OK, communciation errors, run OK, run automaticretry
    # change channel type to ftp: errors
    change_communication_type("unitretry_mime_out", "ftp")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 1,
            "lasterror": 1,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 1,
            "lasterror": 0,
            "lastdone": 1,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 741:
        raise Exception("10 filesize not OK: %s" % row["filesize"])
    # change channel type to ftp: errors
    change_communication_type("unitretry_mime_out", "ftp")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 1,
            "lasterror": 1,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 1,
            "lasterror": 0,
            "lastdone": 1,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 741:
        raise Exception("11 filesize not OK: %s" % row["filesize"])
    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 2,
            "lasterror": 0,
            "lastdone": 2,
            "lastok": 0,
            "lastopen": 0,
            "send": 2,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # change channel type to ftp: errors
    change_communication_type("unitretry_mime_out", "ftp")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 1,
            "lastreceived": 1,
            "lasterror": 1,
            "lastdone": 0,
            "lastok": 0,
            "lastopen": 0,
            "send": 0,
            "processerrors": 1,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    # channel has type file: this goes OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call([pythoninterpreter, "bots-engine.py", "unitretry_mime"])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 1,
            "lasterror": 0,
            "lastdone": 1,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report
    row = utilsunit.getreportlastrun()
    if row[str("filesize")] != 741:
        raise Exception("12 filesize not OK: %s" % row["filesize"])
    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type("unitretry_mime_out", "mimefile")
    subprocess.call(
        [pythoninterpreter, "bots-engine.py", "--automaticretrycommunication"]
    )  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            "status": 0,
            "lastreceived": 1,
            "lasterror": 0,
            "lastdone": 1,
            "lastok": 0,
            "lastopen": 0,
            "send": 1,
            "processerrors": 0,
        },
        utilsunit.getreportlastrun(),
    )  # check report

    logging.shutdown()
    botsglobal.db.close
    print("Tests OK!!!")
