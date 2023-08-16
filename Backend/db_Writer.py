import logging
import os
import random
import time
import uuid
from argparse import ArgumentParser, RawTextHelpFormatter

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras

global cur

def func_ReturnRows(n_MaxCount, s_Table, s_searchStr, s_SrchFld):
    OK = openConnection ()
    if OK == True:
        str_SQL = 'Select * from ' + s_Table
        if (len(s_searchStr) > 0):
            str_SQL = str_SQL + ' where ' + s_SrchFld + ' LIKE (\'%' + s_searchStr + '%\')'
        
        if (n_MaxCount>0):
            str_SQL = str_SQL + ' limit ' + str(n_MaxCount)

        psycopg2.extras.register_uuid()
        with conn.cursor() as cur:
            o_returnedData = cur.execute(str_SQL)
            logging.debug("ReturnRows: status message: %s",cur.statusmessage)
            if cur.statusmessage == 'SELECT 2':
                o_Records = cur.fetchall()
                return True, o_Records
            else:
                s_ErrorMsg = cur.statusmessage
                return False, s_ErrorMsg
    else:
        return False, OK


    return 0

def func_InsterFlags(s_ProjID, s_EnvID, s_FlagID, s_WriteRow):
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        cur.execute("UPSERT INTO flags (s_flag_unique_id, s_proj_id, s_env_id, s_flag_id, s_flag_data) VALUES(%s, %s, %s, %s, %s)", (s_ProjID+'_'+s_EnvID+'_'+s_FlagID, s_ProjID, s_EnvID, s_FlagID, s_WriteRow))
        logging.debug("InserFlags: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage

def func_InsterEnv(s_ProjID, s_EnvID, s_WriteRow):
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        cur.execute("UPSERT INTO environments (s_proj_id_unique, s_env_id, s_env_data, s_proj_id) VALUES(%s, %s, %s, %s)", (s_ProjID+'_'+s_EnvID, s_EnvID, s_WriteRow, s_ProjID))
        logging.debug("InserEnv: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage

def func_InsterProject(s_ProjID,s_WriteRow):
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        cur.execute("UPSERT INTO projects (s_Proj_ID, s_Proj_Data) VALUES(%s, %s)", (s_ProjID, s_WriteRow))
        logging.debug("InsertProject: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage

def openConnection():
    global conn

    opt = parse_cmdline()
    logging.basicConfig(level=logging.DEBUG if opt.verbose else logging.INFO)
    try:
        # Attempt to connect to cluster with connection string provided to the script.
        db_url = opt.dsn
        conn = psycopg2.connect(db_url, application_name="$ docs_simplecrud_psycopg2", cursor_factory=psycopg2.extras.RealDictCursor)
        return True
    except Exception as e:
        logging.fatal("database connection failed")
        logging.fatal(e)
        return False

def main(tableID,state,s_ProjID,s_EnvID,s_FlagID, s_WriteRow ): #1=open + execute, 2=execute + close, 0=execute only
    if (state == 1 or state == 3):
        openConnection()
    match tableID:
        case 'projects':
            execStatus = func_InsterProject(s_ProjID,s_WriteRow)
        case 'environments':
            execStatus = func_InsterEnv(s_ProjID,s_EnvID,s_WriteRow)
        case 'flags':
            execStatus = func_InsterFlags(s_ProjID,s_EnvID,s_FlagID,s_WriteRow)

    print(execStatus)
    if (state == 2 or state==3):
        # Close communication with the database.
        conn.close()
    return execStatus


def parse_cmdline():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-v", "--verbose",
                        action="store_true", help="print debug info")

    parser.add_argument(
        "dsn",
        #default=os.environ.get("DATABASE_URL"),
        default="postgresql://john:FxXm44tjf2BSG1GQywmKGQ@solid-sphinx-11729.7tt.cockroachlabs.cloud:26257/LD_Search?sslmode=verify-full",
        nargs="?",
        help="""\
database connection string\
 (default: value of the DATABASE_URL environment variable)
            """,
    )

    opt = parser.parse_args()
    if opt.dsn is None:
        parser.error("database connection string not set")
    return opt


#if __name__ == "__main__":
#    main()