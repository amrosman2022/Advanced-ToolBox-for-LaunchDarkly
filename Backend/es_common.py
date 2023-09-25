import json
import os
import logging

global s_g_db_conn
global s_g_api_key
global s_g_user_id 
global s_g_user_pass
global s_g_err_log 
global b_g_is_logged_in
global o_g_dataSetPagination
global n_g_tablePageSize
global n_g_paginationCnt
global o_g_costRowQueryResults


#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
def func_getFldJSON (obj_JSON={}, s_fldName=''):
    try:
        s_theObj = obj_JSON.__str__()
        json_theObj = json.loads(s_theObj)
        any_returnVal = json_theObj[s_fldName]
        return any_returnVal
    except:
        return 'Error: Not a JSON'
    

#--------------------------------------------------------------------------------
#------------------- Write info to Console and OS if Global Logging is on -------
#--------------------------------------------------------------------------------
def func_Logging(s_Data,b_Console=True, b_OS=-1):    #b_os:-1=do not log, 0=info, 1=error
    if(s_g_err_log == True):
        if (b_Console == True):
            print(s_Data)

        if(b_OS == 1):
            logging.error(s_Data)
        else:
            if(b_OS == 0):
                logging.info(s_Data)
            

