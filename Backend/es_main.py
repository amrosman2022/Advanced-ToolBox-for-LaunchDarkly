#import atexit
import time
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_restful import reqparse, abort, Api, Resource
# Import the local files
import ld_get_projects
import ld_get_environments
import ld_get_FF
import out_generateOutput
import es_Settings
import json
import base64
import es_common
import es_login

#-------------------------------------------------------
# ------------------------- Global --------------------
#--------------------------------------------------------

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task')

#------ Decode the INPUT text
def Decode_Text(s):
    try:
        replacement_string = s.replace("*|*", "/")
        replacement_string = replacement_string.replace("_-|x|-_", "?")
        # If decoding is successful, it's likely Base64 encoded
        return replacement_string
    except:
        # Decoding failed, not Base64 encoded
        return s

#---------------------------------------------------------------------------
#------------------------- Advanced Search Function -----------------------
# ----- -------------- Example: http://192.168.2.18:8080/refresh|||projects|||20
# ----- Example 2: http://192.168.2.18:8080/list|||projects|||0
# -- params = 1=function name (list, count, search, refresh), 2=which table to target (FF,Env,Prj), 3=Max count(applies for refresh), 4=Refresh CRDB for the "LD project name"
# -- params = 4=Search field, 5=Search Criteria
#---------------------------------------------------------------------------
class Adv_Srch(Resource):
    def get(self,inputs):
        global s_g_api_key
        global es_common

        a_n_Count = []
        s_OutputTxt = ''
        #--------- Get the SETTINGS and the URL paramters --------
        if inputs == 'favicon.ico'.lower():
            return 200
        #inputs = inputs.lower()
        decoded_string = Decode_Text(inputs)

        inputs_list = decoded_string.split('|||')
        #inputs_list[0] = n_Func
        #inputs_list[1] = s_Table
        # int(inputs_list[2])   # Max Count for Refresh(only for refresh)
        # inputs_list[3]=  s_RfrshPrjNm
        # in case of search 
            #inputs_list[4] = s_srchCol
            #inputs_list[5] = s_srchCrit

        # --------------- Load the settings and set the global variables ----------------------------
        if (inputs_list[0] != 'settings'):
            j_settings = es_Settings.func_selector (2,'')    # get the setting from the setting file and set a Variable
            if (json.loads(j_settings[0])['ErrorCode'] == 0):
                es_common.s_g_api_key = j_settings[1]['incl_LDkey']
                es_common.s_g_db_conn = j_settings[1]['incl_DBconnection']
                es_common.s_g_user_id = j_settings[1]['incl_ASuser_nameAS']
                es_common.s_g_user_pass = j_settings[1]['incl_ASpassword_1']
                es_common.s_g_err_log = j_settings[1]['incl_ASlogging']
                
            else:
                return ('{"Error" : "Cannot read API Key"}')
            
        #------------------Select which function will run ----------------------------------------
        match inputs_list[0]:
            case 'list':        # get the list of items from any DB-table formated in a HTML table |||  input = Table Name
                s_OutputTxt = out_generateOutput.createHTMLTable(int(inputs_list[2]), inputs_list[1])    #
            case 'cnt':     # get count of any DB-Table and return a text ||| input = Table Name
                s_OutputTxt = out_generateOutput.getCountTxt(inputs_list[1])    # 
            case 'search':     #search the CRDB for the existance of a word in all tables ||| input = Table Name, Search Column, Search Criteria
                s_OutputTxt = out_generateOutput.createHTMLTable_Srch(int(inputs_list[2]), inputs_list[1],inputs_list[3], inputs_list[4])         
            # http://192.168.2.18:8080/refresh|||CALL|||20
            case 'refresh':     #Refresh the CRDB from the LD sources using API |||  input = API Key for LD, Only for LD Project Name, how many projects to refresh from top
                try:
                    s_OutputTxt = ld_get_projects.func_main_get_all_projects(es_common.s_g_api_key, inputs_list[1],int(inputs_list[2]))     # nested calls (3 separate .py files) from project to Environments to Flags....
                    s_OutputTxt = '{' + s_OutputTxt + '}'
                    a_n_Count.append( out_generateOutput.getCountTxt('projects'))
                    a_n_Count.append (out_generateOutput.getCountTxt('environments'))
                    a_n_Count.append(out_generateOutput.getCountTxt('flags'))
                    results = out_generateOutput.setLogs (1, a_n_Count)
                except:
                    return ('{"Error" : "Adv_Srch"}')
            # http://192.168.2.18:8080/settings|||1=  or 2= |||data
            case 'settings':     #save /retrieve the system settings
                s_OutputTxt = es_Settings.func_selector(inputs_list[1],inputs_list[2])
            # http://192.168.2.18:8080/login|||1=login or 2=logout|||data
            case 'login':     #return login from the system settings
                if (inputs_list[1] == '1'):
                    s_OutputTxt = es_login.login_from_js(inputs_list[2])
                    if (s_OutputTxt['success'] == True):
                        es_common.b_g_is_logged_in = True
                    else:
                        es_common.b_g_is_logged_in = False
                else:
                    s_OutputTxt = '{"success": true, "message": "Loging status is cleared....ready for new login..."}'
                    es_common.b_g_is_logged_in = False
                    print(f"Loging status is cleared....ready for new login...")
            case 'validlogin': #validate if the user is logged or not
                if (es_common.b_g_is_logged_in == False):
                    s_OutputTxt = '{"success": true, "message": "User is logged out...Ready for login now... "}'
                    es_common.b_g_is_logged_in = False
                else:
                    s_OutputTxt = '{"success": false, "message": "User Already Logged-in...", "userid": "' + es_common.s_g_user_id + '"}'

        return s_OutputTxt
#-----------------------------------------------------------------------------------------------------------------------------



#-----------------------------------------------------------------
#------------------------- Setup the API -------------------------
#----- example: http://10.0.7.107:8080/search|||flags|||usingMobileKey :,maintainerId :|||false,%226125573d3e2a682621c1ba5f%22
#-----------------------------------------------------------------
api.add_resource(Adv_Srch, '/<inputs>')
#atexit.register(ld_init.Kill_LD_Connection) 
if __name__ == '__main__':
    es_common.b_g_is_logged_in = False
    app.run(debug=False, port=8080, host='0.0.0.0')