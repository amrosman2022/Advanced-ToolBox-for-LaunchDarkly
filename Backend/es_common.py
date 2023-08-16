import json
import os

global s_g_db_conn
global s_g_api_key
global s_g_user_id 
global s_g_user_pass
global s_g_err_log 
global b_g_is_logged_in

def func_getFldJSON (obj_JSON={}, s_fldName=''):
    try:
        s_theObj = obj_JSON.__str__()
        json_theObj = json.loads(s_theObj)
        any_returnVal = json_theObj[s_fldName]
        return any_returnVal
    except:
        return 'Error: Not a JSON'