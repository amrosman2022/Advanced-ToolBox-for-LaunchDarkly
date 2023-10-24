import db_AccessLayer as db
import json
import es_common
import decimal

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
def saveLD (s_TargetEnvID, s_projID, s_envID):
    s_HTML = '<div class="card"><h5 class="card-header">Migration Results</h5><div class="table-responsive"><TABLE class="table table-striped"><THead><TR><TH>TYPE</TH><TH>Status</TH><TH>RECORDS SAVED/TOTAL</TH></TR></THead><TBODY>'
    n_Status = db.CopyLDtoNew(s_TargetEnvID,s_projID, s_envID)
    if n_Status[0] == True:
        s_HTML += "<TR><TD>Projects</TD><TD>%s</TD><TD>%s</TD></TR>" %(n_Status[1][0][1]['error message'],n_Status[1][0][1]['count'])
        s_HTML += "<TR><TD>Environment</TD><TD>%s</TD><TD>%s</TD></TR>" %(n_Status[1][1][1]['error message'],n_Status[1][1][1]['count'])
        s_HTML += "<TR><TD>Flags</TD><TD>%s</TD><TD>%s</TD></TR>" %(n_Status[1][2][1]['error message'],n_Status[1][2][1]['count'])
        s_HTML += "</TBODY></TABLE></DIV></DIV>"
        return {"status": "True", "data": s_HTML}
    else:
        return {"status" : "False", "data": '<div class="card"><h5 class="card-header">Migration Results</h5>Please check error logs table for more details...</div>', "error id":n_Status[1]['error id'], "error message": n_Status[1]['error message']}
                


#--------------------------------------------------------------------------------------------
#----------------------- Main: Search a table and return the Python List --------------------------
#---------------------------- Maximum rows as per global variable ---------------------------
#--------------------------------------------------------------------------------------------
def createHTMLTable_Srch (n_Max_Cnt, s_tblID, s_srchCol, s_srchCrit, n_startRowShow=1, b_Refresh='true'):
    try:
        if (b_Refresh == 'true'):     # go get a fresh data set ELSE use the data set from the Global Variable
            n_Status = db.func_SrchTables (n_Max_Cnt, s_tblID, s_srchCol, s_srchCrit)

            if n_Status[0] != True:
                return s_tblID + ": func_SrchTables: call error..." + "||| Source Error: " + n_Status[1]
            else:
                es_common.o_g_dataSetPagination = n_Status[1]
                n_totalRows = len(n_Status[1])
                if (n_totalRows > es_common.n_g_tablePageSize):
                    output_HTML =es_common.o_g_dataSetPagination[0:es_common.n_g_tablePageSize]
                else:
                    output_HTML =es_common.o_g_dataSetPagination

                es_common.func_Logging(output_HTML,True)

                return n_totalRows, output_HTML
        
    except:
        es_common.func_Logging(s_tblID + ": createHTMLTable_Srch: try-catch error...", True,1)
        return 0,s_tblID + ": createHTMLTable_Srch: try-catch error..."
    

#--------------------------------------------------------------------------------------------
#----------------------- Main: List/srch rows of a table and return the Python List --------------------
#---------------------------- Maximum rows as per global variable ---------------------------
#--------------------------------------------------------------------------------------------
def createHTMLTable (s_type, n_Max_Cnt, s_tblID, s_srchCol='', s_srchCrit='', n_startRowShow=1, b_Refresh='true'):   #changed
    try:
        if (b_Refresh == 'true'):     # go get a fresh data set ELSE use the data set from the Global Variable
            if (s_type == 'list'):
                n_Status = db.func_ReturnRows(n_Max_Cnt,s_tblID,'','')
            else:
                n_Status = db.func_SrchTables (n_Max_Cnt, s_tblID, s_srchCol, s_srchCrit)

            if n_Status[0] != True:
                return "db.func_ReturnRows-->" + s_tblID + ": call error..."
            else:
                es_common.o_g_dataSetPagination = n_Status[1]   # Save the full dataset to a Global Variable
                n_totalRows = len(es_common.o_g_dataSetPagination)
                if (len(es_common.o_g_dataSetPagination) > es_common.n_g_tablePageSize):
                    n_startRowShow = (int(n_startRowShow) * es_common.n_g_tablePageSize) - es_common.n_g_tablePageSize  # changed - added
                    output_Array =es_common.o_g_dataSetPagination[int(n_startRowShow):(es_common.n_g_tablePageSize+n_startRowShow)] #changed
                else:
                    output_Array =es_common.o_g_dataSetPagination

                es_common.func_Logging(output_Array,True)
                return n_totalRows, output_Array
        else:
            n_totalRows = len(es_common.o_g_dataSetPagination)
            if (len(es_common.o_g_dataSetPagination) > es_common.n_g_tablePageSize):
                n_startRowShow = (int(n_startRowShow) * es_common.n_g_tablePageSize) - es_common.n_g_tablePageSize  # changed - added
                output_Array =es_common.o_g_dataSetPagination[int(n_startRowShow):(es_common.n_g_tablePageSize+n_startRowShow)] #changed
            else:
                output_Array =es_common.o_g_dataSetPagination

            es_common.func_Logging(output_Array,True)
            return n_totalRows, output_Array

    except:
        es_common.func_Logging(s_tblID + ": createHTMLTable: try-catch error...", True,1)
        return 0,s_tblID + ": createHTMLTable: try-catch error..."    


#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
def getCountTxt (s_tblID):   
    try:
        match s_tblID:
            case 'projects':
                n_Status = db.func_RetunRowCount('projects')
            case 'environments':
                n_Status = db.func_RetunRowCount('environments')
            case 'flags':
                n_Status = db.func_RetunRowCount('flags')

        if n_Status[0] != True:
            return "getCountTxt: call error @" + s_tblID
        else:
            #output_Frames = pd.json_normalize(n_Status[1])
            output_Txt = n_Status[1][0]['count'] #pd.json_normalize(n_Status[1])
            return output_Txt
    except:
        return "getCountTxt: syntax error..."


#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
def setLogs (n_type, a_Inputs):  #s_Inputs = array of vars to be written to the DB depending on the n_type
    try:
        match n_type:
            case 1: #write the count of proj,env,flags after each update
                n_Status = db.func_WriteStatus(1, a_Inputs)
    except:
        return False, "setLogs: syntax error @" + n_type
    
    s_return = "setlogs: " + str(n_Status[1]) + " @" + str(n_type)
    return True, s_return

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
def getCost(s_type, s_dept_id, s_dep_name, s_user_id):
    s_return = db.func_GetCost(s_type,s_dept_id,s_dep_name, s_user_id)
    # convert to JSON
    if s_return[0] == True:
        data_dict = []
        match s_type:   #convert result to the UI Graph Library format
            case 'department':
                for idx, item in enumerate(s_return[1]):
                    data_dict.append({"x": item['department_name'], "y": float(item['total_cost'])})
            case 'user':
                for idx, item in enumerate(s_return[1]):
                    data_dict.append({"x": item['user_id'], "y": float(item['total_cost'])})
                for value in s_return[1]:
                    es_common.o_g_costRowQueryResults[value['user_id']] = value['department_name']

    return True, data_dict


#--------------------------------------------------------------------------------------------
#--------------------handle the deciaml error when using JSON.DUMPS--------------------------
#--------------------------------------------------------------------------------------------
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
def getCostSettings ():
    s_return = db.func_ReturnRows(0,'v_costview','','')
    if s_return[0] == True:
        data = [dict(row) for row in s_return[1]]
        data = json.dumps(data,cls=DecimalEncoder)
        data = json.loads(data)
        return True, data
    
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
def saveCostSetting(s_ID, s_UpdatedCost):
    s_return = db.updateCost(s_ID, float(s_UpdatedCost))
    es_common.func_Logging(s_return[1])
    return True, s_return