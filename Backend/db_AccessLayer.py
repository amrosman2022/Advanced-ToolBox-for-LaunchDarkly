import logging
import os
import random
import time
import uuid
from argparse import ArgumentParser, RawTextHelpFormatter
import json 
from datetime import date

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras
import es_common

global cur

def func_addquotes(char):
    x = "'{}'".format(char)
    return(x)

#----------------------------------------------------------------------------------------------------------------
#------------------ CRDB have a dedicated Tag field but UI not allowing yet to search for them ------------------
#------------------ Version 2 planned for search tags in all tables ---------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def func_SrchTables (n_Max_Cnt, s_tbl_ID, s_fld, s_crit):   #Fields = comma separated field names , Criteria =comma separated seach criteria for each field
    x=0
    #add case statement for s_table_id and repeat to reflect the 3 tables
    s_a_Fields = s_fld.split(',')
    s_a_Criteria = s_crit.split(',')
    match s_tbl_ID:
        case 'projects':
            s_fld_data = 's_proj_data'
            s_TableFields = "*"
        case 'environments':
            s_fld_data = 's_env_data'
            s_TableFields = "s_proj_id, s_env_id, s_env_data, s_env_tags"
        case 'flags':
            s_fld_data = 's_flag_data'
            s_TableFields = "s_proj_id, s_env_id, s_flag_id, s_flag_data, s_flag_tags"
    str_SQL = []
    str_SQL.append("SELECT %s FROM %s WHERE " % (s_TableFields, s_tbl_ID))
    for s_Field in s_a_Fields:
        if (x>0):
            str_SQL.append(' OR ')
        str_SQL.append("%s.%s LIKE " % (s_tbl_ID,s_fld_data))
        str_SQL.append("'")
        str_SQL.append("%" + s_Field + " " + s_a_Criteria[x] + "%")
        str_SQL.append("'")
        x=x+1
    if (n_Max_Cnt>0):
        str_SQL.append(' limit ' + str(n_Max_Cnt))      #new
    print(str_SQL)
    str_SQL = "".join(str_SQL)
    print(str_SQL)

    OK = openConnection ()
    if OK == True:
        psycopg2.extras.register_uuid()
        with conn.cursor() as cur:
            o_returnedData = cur.execute(str_SQL)
            logging.debug("ReturnRows: status message: %s",cur.statusmessage)
            if cur.rowcount > 0:
                o_Records = cur.fetchall()
                return True, o_Records
            else:
                s_ErrorMsg = cur.statusmessage
                return False, s_ErrorMsg
    else:
        return False, OK

def func_RetunRowCount(s_Table):
    OK = openConnection ()
    if OK == True:
        str_SQL = 'Select count(*) from ' + s_Table
        psycopg2.extras.register_uuid()
        with conn.cursor() as cur:
            o_returnedData = cur.execute(str_SQL)
            logging.debug("ReturnRows: status message: %s",cur.statusmessage)
            if cur.statusmessage == 'SELECT 1':
                o_Records = cur.fetchall()
                return True, o_Records
            else:
                s_ErrorMsg = cur.statusmessage
                return False, s_ErrorMsg
    else:
        return False, OK


def func_ReturnRows(n_MaxCount, s_Table, s_searchStr, s_SrchFld):
    OK = openConnection ()
    if OK == True:
        match s_Table:
            case 'projects':
                s_TableFields = "*"
            case 'environments':
                s_TableFields = "s_proj_id, s_env_id, s_env_data, s_env_tags"
            case 'flags':
                s_TableFields = "s_proj_id, s_env_id, s_flag_id, s_flag_data, s_flag_tags"


        str_SQL = "Select " + s_TableFields +" from " + s_Table
        if (len(s_searchStr) > 0):
            str_SQL = str_SQL + ' where ' + s_SrchFld + ' LIKE (\'%' + s_searchStr + '%\')'
        
        if (n_MaxCount>0):
            str_SQL = str_SQL + ' limit ' + str(n_MaxCount)

        psycopg2.extras.register_uuid()
        with conn.cursor() as cur:
            o_returnedData = cur.execute(str_SQL)
            logging.debug("ReturnRows: status message: %s",cur.statusmessage)
            if cur.rowcount > 0:
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
        s_Tags = JSONtoOBJ = json.loads(s_WriteRow)["tags"]     # extract the tags
        cur.execute("UPSERT INTO flags (s_flag_unique_id, s_proj_id, s_env_id, s_flag_id, s_flag_data,s_flag_tags) VALUES(%s, %s, %s, %s, %s,%s)", (s_ProjID+'_'+s_EnvID+'_'+s_FlagID, s_ProjID, s_EnvID, s_FlagID, s_WriteRow, s_Tags))
        logging.debug("InserFlags: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage

def func_InsterEnv(s_ProjID, s_EnvID, s_WriteRow):
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        s_Tags = JSONtoOBJ = json.loads(s_WriteRow)["tags"]     # extract the tags
        cur.execute("UPSERT INTO environments (s_proj_id_unique, s_env_id, s_env_data, s_proj_id, s_env_tags) VALUES(%s, %s, %s, %s, %s)", (s_ProjID+'_'+s_EnvID, s_EnvID, s_WriteRow, s_ProjID, s_Tags))
        logging.debug("InserEnv: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage

def func_InsterProject(s_ProjID,s_WriteRow):
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        s_Tags = JSONtoOBJ = json.loads(s_WriteRow)["tags"]     # extract the tags
        cur.execute("UPSERT INTO projects (s_Proj_ID, s_Proj_Data, s_proj_tags) VALUES(%s, %s, %s)", (s_ProjID, s_WriteRow, s_Tags))
        logging.debug("InsertProject: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage


#-----------------------------------------------------------------------------
#------------------------ Insert the Logs record ----------------------------
#-----------------------------------------------------------------------------
def func_WriteStatus(n_type, a_Inputs):
    
    try: 
        status = openConnection()
    except:
        return False, "func_WriteStatus: " + status +" @" + n_type
    
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        d_TheDate = date.today().strftime('%Y-%m-%d')
        cur.execute("INSERT INTO logs (i_op_type, i_projects, i_environments, i_flags, d_update_date) VALUES(%s, %s, %s, %s, %s)", (n_type, a_Inputs[0], a_Inputs[1], a_Inputs[2], d_TheDate))
        logging.debug("InsertProject: status message: %s",cur.statusmessage)
    conn.commit()
    return True, cur.statusmessage


#-----------------------------------------------------------------------------
#------------------------ Open the DB Connection ----------------------------
#-----------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------
#------------------------ Close the DB Connection ----------------------------
#-----------------------------------------------------------------------------

def closeConnection():
     # Close communication with the database.
    conn.close()

#------------------------------------------------------------------------------------------------------------------
#----------------------------------- Write the data to the CRDB ---------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
def main(tableID,state,s_ProjID,s_EnvID,s_FlagID, s_WriteRow ): #1=open + execute, 2=execute + close**, 0=execute only  **=close in now explicit
    if (state == 1 or state == 3):
        openConnection()
    match tableID:
        case 'projects':
            execStatus = func_InsterProject(s_ProjID,s_WriteRow)
        case 'environments':
            execStatus = func_InsterEnv(s_ProjID,s_EnvID,s_WriteRow)
        case 'flags':
            execStatus = func_InsterFlags(s_ProjID,s_EnvID,s_FlagID,s_WriteRow)

    print(tableID + ": " + execStatus)
    return execStatus


def parse_cmdline():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-v", "--verbose",
                        action="store_true", help="print debug info")

    parser.add_argument(
        "dsn",
        #default=os.environ.get("DATABASE_URL"),
        default=es_common.s_g_db_conn,
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
