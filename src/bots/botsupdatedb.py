# -*- coding: utf-8 -*-




import atexit
import click
import logging
import os
import socket
import sys
from django.utils.translation import gettext as _

from . import botslib
from . import botsinit
from . import botsglobal


def sqlite_database_is_version3():
    for row in botslib.query('''PRAGMA table_info(routes)'''):
        if row[str('name')] == 'translateind':
            if row[str('type')] == 'bool':
                return False
            else:
                return True
    raise Exception('Could not determine version of database')


QUERYSTRING = '''
PRAGMA writable_schema = 1;
UPDATE SQLITE_MASTER SET SQL =
'CREATE TABLE "routes" (
    "id" integer NOT NULL PRIMARY KEY,
    "idroute" varchar(35) NOT NULL,
    "seq" integer unsigned NOT NULL,
    "active" bool NOT NULL,
    "fromchannel_id" varchar(35) REFERENCES "channel" ("idchannel"),
    "fromeditype" varchar(35) NOT NULL,
    "frommessagetype" varchar(35) NOT NULL,
    "tochannel_id" varchar(35) REFERENCES "channel" ("idchannel"),
    "toeditype" varchar(35) NOT NULL,
    "tomessagetype" varchar(35) NOT NULL,
    "alt" varchar(35) NOT NULL,
    "frompartner_id" varchar(35) REFERENCES "partner" ("idpartner"),
    "topartner_id" varchar(35) REFERENCES "partner" ("idpartner"),
    "frompartner_tochannel_id" varchar(35) REFERENCES "partner" ("idpartner"),
    "topartner_tochannel_id" varchar(35) REFERENCES "partner" ("idpartner"),
    "testindicator" varchar(1) NOT NULL,
    "translateind" integer NOT NULL,
    "notindefaultrun" bool NOT NULL,
    "desc" text,
    "rsrv1" varchar(35),
    "rsrv2" integer,
    "defer" bool NOT NULL,
    "zip_incoming" integer,
    "zip_outgoing" integer,
    UNIQUE ("idroute", "seq"))'
WHERE NAME = 'routes';
PRAGMA writable_schema = 0;
'''


def sqlite3():
    if sqlite_database_is_version3():
        print('Database sqlite3 is already bots version 3. No action is taken.')
        return 2

    print('Start changing sqlite3 database to bots version 3.')
    cursor = botsglobal.db.cursor()
    try:
        #channel ****************************************
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "rsrv3" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "keyfile" VARCHAR(256) ''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "certfile" VARCHAR(256) ''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "testpath" VARCHAR(256) ''')
        #filereport ****************************************
        cursor.execute('''DROP INDEX "filereport_reportidta" ''')
        cursor.execute('''ALTER TABLE "filereport" ADD COLUMN "filesize" INTEGER DEFAULT 0''')
        #partner *************************************
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr1" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr2" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr3" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr4" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr5" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "name1" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "name2" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "name3" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "address1" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "address2" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "address3" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "city" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "postalcode" VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "countrysubdivision" VARCHAR(9) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "countrycode" VARCHAR(3) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "phone1" VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "phone2" VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "desc" TEXT ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "startdate" DATE ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "enddate" DATE ''')
        #report ****************************************
        cursor.execute('''CREATE INDEX "report_ts" ON "report" ("ts")''')
        cursor.execute('''ALTER TABLE "report" ADD COLUMN "filesize" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "report" ADD COLUMN "acceptance" INTEGER DEFAULT 0''')
        #routes ****************************************
        cursor.execute('''ALTER TABLE "routes" ADD COLUMN "zip_incoming" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "routes" ADD COLUMN "zip_outgoing" INTEGER DEFAULT 0''')
        #ta ****************************************
        cursor.execute('''DROP INDEX "ta_script" ''')
        cursor.execute('''CREATE INDEX "ta_reference" ON "ta" ("reference")''')
        cursor.execute('''ALTER TABLE "ta" ADD COLUMN "filesize" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "ta" ADD COLUMN "numberofresends" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "ta" ADD COLUMN "rsrv5" VARCHAR(35) DEFAULT '' ''')
    except:
        txt = botslib.txtexc()
        botsglobal.db.rollback()
        cursor.close()
        print('Error in adding fields to sqlite3 database: "%s".' % (txt))
        return 1
    else:
        botsglobal.db.commit()
        cursor.close()

    cursor = botsglobal.db.cursor()
    try:
        cursor.executescript(QUERYSTRING)
    except:
        txt = botslib.txtexc()
        botsglobal.db.rollback()
        cursor.close()
        print('Error in changing sqlite3 database-schema "routes": "%s".' % (txt))
        return 1
    else:
        botsglobal.db.commit()
        cursor.close()

    print('Succesful changed sqlite3 database to bots version 3.')
    return 0


def postgresql_psycopg2():
    print('Start changing postgresql database to bots version 3.')
    cursor = botsglobal.db.cursor()
    try:
        #channel ****************************************
        cursor.execute('''ALTER TABLE "channel" ALTER COLUMN "filename" TYPE VARCHAR(256)''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "rsrv3" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "keyfile" VARCHAR(256) ''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "certfile" VARCHAR(256) ''')
        cursor.execute('''ALTER TABLE "channel" ADD COLUMN "testpath" VARCHAR(256) ''')
        #ccode ****************************************
        cursor.execute('''ALTER TABLE "ccode" ALTER COLUMN "rightcode" TYPE VARCHAR(70)''')
        cursor.execute('''ALTER TABLE "ccode" ALTER COLUMN "attr1" TYPE VARCHAR(70)''')
        #filereport ****************************************
        cursor.execute('''ALTER TABLE "filereport" DROP CONSTRAINT "filereport_pkey" ''')  # remove primary key
        cursor.execute(
            '''ALTER TABLE "filereport" DROP CONSTRAINT "filereport_idta_key" ''')  # drop contraint UNIQUE(idta, reportidta)
        cursor.execute('''DROP INDEX "filereport_idta" ''')  # drop index on idta (will be primary key)
        cursor.execute('''DROP INDEX "filereport_reportidta" ''')
        cursor.execute('''ALTER TABLE "filereport" DROP COLUMN "id" ''')
        cursor.execute(
            '''ALTER TABLE "filereport" ADD CONSTRAINT "filereport_pkey" PRIMARY KEY("idta")''')  # idta is primary key
        cursor.execute('''ALTER TABLE "filereport" ALTER COLUMN "errortext" TYPE TEXT''')
        cursor.execute('''ALTER TABLE "filereport" ADD COLUMN "filesize" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "filereport" ADD COLUMN "acceptance" INTEGER DEFAULT 0''')
        #partner *************************************
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr1" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr2" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr3" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr4" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "attr5" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "name1" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "name2" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "name3" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "address1" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "address2" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "address3" VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "city" VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "postalcode" VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "countrysubdivision" VARCHAR(9) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "countrycode" VARCHAR(3) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "phone1" VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "phone2" VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "desc" TEXT ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "startdate" DATE ''')
        cursor.execute('''ALTER TABLE "partner" ADD COLUMN "enddate" DATE ''')
        #persist ****************************************
        cursor.execute('''ALTER TABLE "persist" ALTER COLUMN "content" TYPE TEXT''')
        #report ****************************************
        cursor.execute('''CREATE INDEX "report_ts" ON "report" ("ts")''')
        cursor.execute('''ALTER TABLE "report" ADD COLUMN "filesize" INTEGER DEFAULT 0''')
        #routes ****************************************
        cursor.execute(
            '''ALTER TABLE "routes" ALTER COLUMN "translateind" TYPE integer USING CASE WHEN "translateind"=FALSE THEN 0 ELSE 1 END''')
        cursor.execute('''ALTER TABLE "routes" ADD COLUMN "zip_incoming" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "routes" ADD COLUMN "zip_outgoing" INTEGER DEFAULT 0''')
        #ta ****************************************
        cursor.execute('''DROP INDEX "ta_script" ''')
        cursor.execute('''CREATE INDEX "ta_reference" ON "ta" ("reference")''')
        cursor.execute('''ALTER TABLE "ta" ALTER COLUMN "errortext" TYPE TEXT ''')
        cursor.execute('''ALTER TABLE "ta" ADD COLUMN "filesize" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "ta" ADD COLUMN "numberofresends" INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE "ta" ADD COLUMN "rsrv5" VARCHAR(35) DEFAULT '' ''')
    except:
        txt = botslib.txtexc()
        botsglobal.db.rollback()
        cursor.close()
        print('Error in changing postgresql database: "%s".' % (txt))
        return 1
    else:
        botsglobal.db.commit()
        cursor.close()

    print('Succesful changed postgresql database to bots version 3.')
    return 0


def mysql():
    print('Start changing mysql database to bots version 3.')
    cursor = botsglobal.db.cursor()
    try:
        #channel ****************************************
        cursor.execute('''ALTER TABLE `channel` MODIFY `filename` VARCHAR(256) NOT NULL''')
        cursor.execute('''ALTER TABLE `channel` ADD COLUMN `rsrv3` INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE `channel` ADD COLUMN `keyfile` VARCHAR(256) ''')
        cursor.execute('''ALTER TABLE `channel` ADD COLUMN `certfile` VARCHAR(256) ''')
        cursor.execute('''ALTER TABLE `channel` ADD COLUMN `testpath` VARCHAR(256) ''')
        #ccode ****************************************
        cursor.execute('''ALTER TABLE `ccode` MODIFY `rightcode` VARCHAR(70)''')
        cursor.execute('''ALTER TABLE `ccode` MODIFY `attr1` VARCHAR(70)''')
        #filereport ****************************************
        cursor.execute('''ALTER TABLE `filereport` CHANGE `id` `id` INTEGER ''')  # drop autoincrement
        cursor.execute('''ALTER TABLE `filereport` DROP PRIMARY KEY ''')  # drop index on id
        cursor.execute('''ALTER TABLE `filereport` DROP COLUMN `id` ''')  # drop id veld
        cursor.execute('''ALTER TABLE `filereport` DROP KEY `idta` ''')  # remove UNIQUE constraint
        #~ cursor.execute('''ALTER TABLE `filereport` DROP INDEX `reportidta` ''')  #not possible as index name is not known
        cursor.execute('''ALTER TABLE `filereport` MODIFY `errortext` TEXT''')
        cursor.execute('''ALTER TABLE `filereport` ADD COLUMN `filesize` INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE `filereport` ADD COLUMN `acceptance` INTEGER DEFAULT 0''')
        #partner *************************************
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `attr1` VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `attr2` VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `attr3` VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `attr4` VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `attr5` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `name1` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `name2` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `name3` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `address1` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `address2` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `address3` VARCHAR(70) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `city` VARCHAR(35) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `postalcode` VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `countrysubdivision` VARCHAR(9) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `countrycode` VARCHAR(3) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `phone1` VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `phone2` VARCHAR(17) ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `desc` TEXT ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `startdate` DATE ''')
        cursor.execute('''ALTER TABLE `partner` ADD COLUMN `enddate` DATE ''')
        #persist ****************************************
        cursor.execute('''ALTER TABLE `persist` MODIFY `content` TEXT''')
        #report ****************************************
        cursor.execute('''CREATE INDEX `report_ts` ON `report` (`ts`)''')
        cursor.execute('''ALTER TABLE `report` ADD COLUMN `filesize` INTEGER DEFAULT 0''')
        #routes ****************************************
        cursor.execute('''ALTER TABLE `routes` ADD COLUMN `zip_incoming` INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE `routes` ADD COLUMN `zip_outgoing` INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE `routes` MODIFY `translateind` integer NOT NULL''')
        #ta ****************************************
        #~ cursor.execute('''ALTER TABLE `ta` DROP INDEX `script` ''')   #not possible as index name is not known
        cursor.execute('''CREATE INDEX `ta_reference` ON `ta` (`reference`)''')
        cursor.execute('''ALTER TABLE `ta` ADD COLUMN `filesize` INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE `ta` ADD COLUMN `numberofresends` INTEGER DEFAULT 0''')
        cursor.execute('''ALTER TABLE `ta` ADD COLUMN `rsrv5` VARCHAR(35) DEFAULT '' ''')
        cursor.execute('''ALTER TABLE `ta` MODIFY `errortext` TEXT ''')
    except:
        txt = botslib.txtexc()
        botsglobal.db.rollback()
        cursor.close()
        print('Error in changing mysql database: "%s".' % (txt))
        return 1
    else:
        botsglobal.db.commit()
        cursor.close()

    print('Succesful changed mysql database to bots version 3.')
    return 0


@click.command()
@click.option('--configdir', '-c', default='config', help='path to config-directory.')
def start(configdir):
    """Update database.
    """
    botsinit.generalinit(configdir)  # find locating of bots, configfiles, init paths etc.

    #**************check if another instance of bots-engine is running/if port is free******************************
    try:
        engine_socket = botslib.check_if_other_engine_is_running()
    except socket.error:
        sys.exit(3)
    else:
        atexit.register(engine_socket.close)

    #**************initialise logging******************************
    process_name = 'updatedatabase'
    botsglobal.logger = botsinit.initenginelogging(process_name)
    atexit.register(logging.shutdown)
    for key, value in botslib.botsinfo():  # log info about environement, versions, etc
        botsglobal.logger.info('%(key)s: "%(value)s".', {'key': key, 'value': value})

    #**************connect to database**********************************
    try:
        botsinit.connect()
    except Exception as msg:
        botsglobal.logger.exception(
            _('Could not connect to database. Database settings are in bots/config/settings.py. Error: "%(msg)s".'), {'msg': msg})
        sys.exit(3)
    else:
        botsglobal.logger.info(_('Connected to database.'))
        atexit.register(botsglobal.db.close)

    #**************handle database lock****************************************
    # set a lock on the database; if not possible, the database is locked: an
    # earlier instance of bots-engine was terminated unexpectedly.
    if not botslib.set_database_lock():
        warn = _('!Bots database is locked!\n'
                 'Bots-engine has ended in an unexpected way during the last run.\n'
                 'Most likely causes: sudden power-down, system crash, problems with disk I/O, bots-engine terminated by user, etc.')
        botsglobal.logger.critical(warn)
        sys.exit(3)
    atexit.register(botslib.remove_database_lock)

    if botsglobal.settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        terug = sqlite3()
    elif botsglobal.settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        terug = mysql()
    elif botsglobal.settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        terug = postgresql_psycopg2()

    sys.exit(terug)


if __name__ == '__main__':
    start()
