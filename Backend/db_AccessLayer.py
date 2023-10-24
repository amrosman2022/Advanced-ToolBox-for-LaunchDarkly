import logging
import os
import random
import time
import uuid
from argparse import ArgumentParser, RawTextHelpFormatter
import json 
from datetime import date
import requests

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras
import es_common

global cur

#----------------------------------------------------------------------------------------------------------------
#------------------------------------------Internal Function-----------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def func_writeFFRecordsToLD(o_Records, TargetEnvID): 

    RecsWritten = 0

    for record in o_Records:
        url = "https://app.launchdarkly.com/api/v2/flags/" + record['s_proj_id']
        payload = json.loads(record['s_flag_data'])
        payload.__delitem__('includeInSnippet')    # deleted to prevent error, cannot exist with other parameters.
        headers = {
        "Content-Type": "application/json",
        "Authorization": TargetEnvID
        }

        # write to destination LD Subscription
        # sleep than repeat API call if rate_limit is reached 
        retries = 0
        while retries < 2: 
            response = requests.post(url, json=payload, headers=headers)
            # if the record not written to LD
            if response.ok == False:    #if failed
                if response.status_code == 429: #if rate reached
                    sleep_time = 3 ** retries
                    time.sleep(sleep_time)
                    retries += 1
                else:
                    retries = 3
                # write error to logs
                es_common.func_Logging(response.text)
                s_Status = payload['key'] + "|||" + str(response.elapsed) + "|||" + response.text + "|||retries:" + str(retries)
                # Write the error to the DB that prevented from adding new record to LD
                response = func_WriteStatus(2,s_Status)
            else:
                RecsWritten += 1
                retries = 3

    if RecsWritten > 0 and RecsWritten < len(o_Records):
        return True, {"function":"func_writeFFRecordsToLD", "error message": "Partial records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    elif RecsWritten == 0:
        return False, {"function":"func_writeFFRecordsToLD", "error message": "No records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    else:
        return True, {"function":"func_writeFFRecordsToLD", "error message": "All records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    



#----------------------------------------------------------------------------------------------------------------
#------------------------------------------Internal Function-----------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def func_writeEnvRecordsToLD(o_Records, TargetEnvID): 

    RecsWritten = 0

    for record in o_Records:
        url = "https://app.launchdarkly.com/api/v2/projects/" + record['s_proj_id'] + "/environments"
        payload = json.loads(record['s_env_data'])
        #payload.__delitem__('includeInSnippetByDefault')    # deleted to prevent error, cannot exist with other parameters.
        headers = {
        "Content-Type": "application/json",
        "Authorization": TargetEnvID
        }

        # write to destination LD Subscription
        response = requests.post(url, json=payload, headers=headers)
        # if the record not written to LD
        if response.ok == False:
            es_common.func_Logging(response.text)
            s_Status = payload['key'] + "|||" + str(response.elapsed) + "|||" + response.text
            # Write the error to the DB that prevented from adding new record to LD
            response = func_WriteStatus(2,s_Status)
        else:
            RecsWritten += 1

    if RecsWritten > 0 and RecsWritten < len(o_Records):
        return True, {"function":"func_writeEnvRecordsToLD", "error message": "Partial records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    elif RecsWritten == 0:
        return False, {"function":"func_writeEnvRecordsToLD", "error message": "No records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    else:
        return True, {"function":"func_writeEnvRecordsToLD", "error message": "All records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    

#----------------------------------------------------------------------------------------------------------------
#------------------------------------------Internal Function-----------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def func_writeProjectRecordsToLD(o_Records, TargetEnvID): 

    url = "https://app.launchdarkly.com/api/v2/projects"
    RecsWritten = 0

    for record in o_Records:
        payload = json.loads(record['s_proj_data'])
        payload.__delitem__('includeInSnippetByDefault')    # deleted to prevent error, cannot exist with other parameters.
        headers = {
        "Content-Type": "application/json",
        "Authorization": TargetEnvID
        }

        # write to destination LD Subscription
        response = requests.post(url, json=payload, headers=headers)
        # if the record not written to LD
        if response.ok == False:
            es_common.func_Logging(response.text)
            s_Status = payload['key'] + "|||" + str(response.elapsed) + "|||" + response.text
            # Write the error to the DB that prevented from adding new record to LD
            response = func_WriteStatus(2,s_Status)
        else:
            RecsWritten += 1

    if RecsWritten > 0 and RecsWritten < len(o_Records):
        return True, {"function":"func_writeProjectRecordsToLD", "error message": "Partial records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    elif RecsWritten == 0:
        return False, {"function":"func_writeProjectRecordsToLD", "error message": "No records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    else:
        return True, {"function":"func_writeProjectRecordsToLD", "error message": "All records written", "system message": "", "count": str(RecsWritten) + "/" + str(len(o_Records))}
    
         

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def CopyLDtoNew (s_TargetEnvID, s_projID, s_envID):    #s_projID=thee project to use in the SELECT, s_TargetEnvID=the LD subscription to use as target for writing data
    str_SQL = []
    o_a_Statuses = []
    x=0
    s_subSQLe = ""
    s_subSQLf = ""
    if (len(s_projID) > 0):
        s_subSQLe +=  "WHERE environments.s_proj_id like '%" + s_projID.lower() + "%'"
        s_subSQLf +=  "WHERE flags.s_proj_id = '" + s_projID.lower() + "'"
        if (len(s_envID) > 0):
            s_subSQLe += " and environments.s_env_id like '%" + s_envID.lower() + "%'"
            s_subSQLf += " and flags.s_env_id = '" + s_envID.lower() + "'"

        str_SQL.append ("SELECT projects.s_proj_id, projects.s_proj_data from projects WHERE projects.s_proj_id like '%" + s_projID.lower() + "%'")
        str_SQL.append ("SELECT environments.s_env_id, environments.s_proj_id, environments.s_env_data from environments " + s_subSQLe)
        str_SQL.append ("SELECT flags.s_flag_id, flags.s_proj_id, flags.s_flag_data from flags " + s_subSQLf)
        #str_SQL.append ("SELECT environments.s_env_id, environments.s_proj_id, environments.s_env_data from environments WHERE environments.s_proj_id like '%" + s_projID.lower() + "%'")
        #str_SQL.append ("SELECT flags.s_flag_id, flags.s_proj_id, flags.s_flag_data from flags WHERE flags.s_proj_id like '%"+ s_projID.lower() + "%'")
    else:
        str_SQL.append ("SELECT projects.s_proj_id, projects.s_proj_data from projects")
        str_SQL.append ("SELECT environments.s_env_id, environments.s_proj_id, environments.s_env_data from environments")
        str_SQL.append ("SELECT flags.s_flag_id, flags.s_proj_id, flags.s_flag_data from flags")
        
    OK = openConnection ()
    if OK == True:
        psycopg2.extras.register_uuid()
        for SQLLine in str_SQL: 
            with conn.cursor() as cur:
                o_returnedData = cur.execute(SQLLine)
                es_common.func_Logging("ReturnRows: status message: " + cur.statusmessage)
                if cur.rowcount > 0:
                    o_Records = cur.fetchall()
                    if x==0:
                        o_StatusP = func_writeProjectRecordsToLD(o_Records, s_TargetEnvID)
                        o_a_Statuses.append(o_StatusP)
                    elif x==1:
                        o_StatusE = func_writeEnvRecordsToLD(o_Records, s_TargetEnvID)
                        o_a_Statuses.append(o_StatusE)
                    else:
                        o_StatusF = func_writeFFRecordsToLD(o_Records, s_TargetEnvID)
                        o_a_Statuses.append(o_StatusF)
                else:
                    s_ErrorMsg = cur.statusmessage
                    s_Status = {"function":"CopyLDtoNew", "error message": "no DB rows returned...", "system message": s_ErrorMsg, "error id": "-100"} #-100 is SQL error
                    response = func_WriteStatus(2,s_Status)
                    return False, s_Status
            x+=1
    else:
        s_Status = {"function":"CopyLDtoNew", "error message": "DB Connection failed to open...", "system message": "NA" , "error id": "-101"} #-101 is DB error
        response = func_WriteStatus(2,s_Status)
        return False, s_Status
    
    return True, o_a_Statuses

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
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
    es_common.func_Logging(str_SQL)
    str_SQL = "".join(str_SQL)
    es_common.func_Logging(str_SQL)

    OK = openConnection ()
    if OK == True:
        psycopg2.extras.register_uuid()
        with conn.cursor() as cur:
            o_returnedData = cur.execute(str_SQL)
            es_common.func_Logging("ReturnRows: status message: " + cur.statusmessage)
            if cur.rowcount > 0:
                o_Records = cur.fetchall()
                return True, o_Records
            else:
                s_ErrorMsg = cur.statusmessage
                return False, s_ErrorMsg
    else:
        return False, OK


# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
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
            case 'v_costview':
                s_TableFields = "*"


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

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
def func_InsterFlags(s_ProjID, s_EnvID, s_FlagID, j_WriteRow):
    s_WriteRow = json.dumps(j_WriteRow)
    s_CreateDate = j_WriteRow['creationDate']
    s_Creator = j_WriteRow['_maintainer']['email']
    b_Archived = j_WriteRow['archived']
    s_LastModified = j_WriteRow['environments'][s_EnvID]['lastModified']
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        s_Tags = JSONtoOBJ = json.loads(s_WriteRow)["tags"]     # extract the tags
        cur.execute("UPSERT INTO flags (s_flag_unique_id, s_proj_id, s_env_id, s_flag_id, s_flag_data,s_flag_tags, s_createdate, s_creator, b_archived, s_lastmodified) VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s,%s)", (s_ProjID+'_'+s_EnvID+'_'+s_FlagID, s_ProjID, s_EnvID, s_FlagID, s_WriteRow, s_Tags, s_CreateDate, s_Creator, b_Archived, s_LastModified))
        logging.debug("InserFlags: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage


# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
def func_InsterEnv(s_ProjID, s_EnvID, s_WriteRow):
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        s_Tags = JSONtoOBJ = json.loads(s_WriteRow)["tags"]     # extract the tags
        cur.execute("UPSERT INTO environments (s_proj_id_unique, s_env_id, s_env_data, s_proj_id, s_env_tags) VALUES(%s, %s, %s, %s, %s)", (s_ProjID+'_'+s_EnvID, s_EnvID, s_WriteRow, s_ProjID, s_Tags))
        logging.debug("InserEnv: status message: %s",cur.statusmessage)
    conn.commit()
    return cur.statusmessage

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
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
    a_Inputs = str(a_Inputs)
    with conn.cursor() as cur:
        d_TheDate = date.today().strftime('%Y-%m-%d')
        match n_type:
            case 1:
                s_SQLStr = "INSERT INTO logs (i_op_type, i_projects, i_environments, i_flags, d_update_date, s_general_log) VALUES(%s, %s, %s, %s, '%s', '')" %(n_type, a_Inputs[0], a_Inputs[1], a_Inputs[2], d_TheDate)
            case 2:
                a_Inputs = a_Inputs.replace('\'','')
                a_Inputs = a_Inputs.replace('}','')
                a_Inputs = a_Inputs.replace('{','')
                a_Inputs = a_Inputs.replace('\\','')
                a_Inputs = a_Inputs.replace('"','')
                s_SQLStr = "INSERT INTO logs (i_op_type, i_projects, i_environments, i_flags, d_update_date, s_general_log) VALUES(%s, 0, 0, 0, '%s', '%s')" %(n_type, d_TheDate, a_Inputs)
                
        try:
            o_response = cur.execute(s_SQLStr)
        except: 
            es_common.func_Logging(o_response)

        es_common.func_Logging("InsertProject: status message:" + cur.statusmessage,True, 0)
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
        es_common.func_Logging("database connection failed")
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
def main(tableID,state,s_ProjID,s_EnvID,s_FlagID, j_WriteRow ): #1=open + execute, 2=execute + close**, 0=execute only  **=close in now explicit
    s_WriteRow = json.dumps(j_WriteRow)
    if (state == 1 or state == 3):
        openConnection()
    match tableID:
        case 'projects':
            execStatus = func_InsterProject(s_ProjID,s_WriteRow)
        case 'environments':
            execStatus = func_InsterEnv(s_ProjID,s_EnvID,s_WriteRow)
        case 'flags':
            execStatus = func_InsterFlags(s_ProjID,s_EnvID,s_FlagID,j_WriteRow)

    es_common.func_Logging(tableID + ": " + execStatus)
    return execStatus


def parse_cmdline():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-v", "--verbose",
                        action="store_true", help="print debug info")

    parser.add_argument(
        "dsn",
        #default=os.environ.get("DATABASE_URL"),
        #default="postgresql://john:FxXm44tjf2BSG1GQywmKGQ@solid-sphinx-11729.7tt.cockroachlabs.cloud:26257/LD_Search?sslmode=verify-full",
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


#----------------------------------------------------------------------------------------------------------------
#------------------ CRDB have a dedicated Tag field but UI not allowing yet to search for them ------------------
#------------------ Version 2 planned for search tags in all tables ---------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def func_GetCost (s_type, s_dep_id='', s_dep_name='', s_user_id=''):   #type = cost for per user or per department, id= either user id or department id or empty = all
    str_SQL = []
    match s_type:
        case 'department':
            str_SQL = 'SELECT u.department_id, d.department_name, SUM(c.cost_per_ff) AS total_cost FROM flags f  JOIN users u ON upper(f.s_creator) = upper(u.user_id)  JOIN cost c ON upper(u.department_id) = upper(c.department_id) LEFT JOIN departments d ON d.department_id = u.department_id'
            
            if len(s_dep_name+s_dep_id) >0:
                if len(s_dep_id)>0: # can only have either dept ID or Name but not both
                    str_SQL += ' where upper(u.department_id) = ' + s_dep_id.upper()
                else:# can only have either dept ID or Name but not both
                    str_SQL += " where upper(d.department_name) LIKE '%" + s_dep_name.upper() + "%'"

            str_SQL += ' GROUP BY u.department_id, d.department_name ORDER BY d.department_name;'

        case 'user':
            str_SQL = 'SELECT u.user_id, u.department_id, d.department_name, SUM(c.cost_per_ff) AS total_cost FROM users u LEFT JOIN flags f ON u.user_id = f.s_creator JOIN cost c ON u.department_id = c.department_id JOIN departments d ON u.department_id = d.department_id'
            if len(s_dep_name+s_user_id) >0:
                if len(s_dep_id)>0: # can only have either dept ID or Name but not both
                    str_SQL += " where u.department_id LIKE %'%s'% OR upper(u.user_id) = upper('%s')", (s_dep_id, s_user_id)
                else: # can only have either dept ID or Name but not both
                    str_SQL += " where upper(d.department_name) LIKE '%" + s_dep_name.upper() + "%' AND upper(u.user_id) LIKE upper('%" +s_user_id + "%')"

            str_SQL += ' GROUP BY u.user_id, u.department_id, d.department_name ORDER BY u.user_id;'
        
    es_common.func_Logging(str_SQL)

    OK = openConnection ()
    if OK == True:
        psycopg2.extras.register_uuid()
        with conn.cursor() as cur:
            o_returnedData = cur.execute(str_SQL)
            es_common.func_Logging("func_GetCost: status message: %s",(cur.statusmessage),True)
            if cur.rowcount > 0:
                o_Records = cur.fetchall()
                return True, o_Records
            else:
                s_ErrorMsg = cur.statusmessage
                return False, s_ErrorMsg
    else:
        return False, OK
    

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
def updateCost(s_DeptID, s_NewCost):
    try:
        OK = openConnection ()
        if OK == True:
            psycopg2.extras.register_uuid()
            with conn.cursor() as cur:
                cur.execute("UPSERT INTO cost (department_id, cost_per_ff) VALUES(%s, %s)", (s_DeptID, s_NewCost))
                logging.debug("updateCost: status message: %s",cur.statusmessage)
            conn.commit()
            return True, cur.statusmessage
    except Exception as e:
            logging.fatal("database connection failed")
            logging.fatal(e)
            es_common.func_Logging("database connection failed")
            return False, e



#if __name__ == "__main__":
#    main()