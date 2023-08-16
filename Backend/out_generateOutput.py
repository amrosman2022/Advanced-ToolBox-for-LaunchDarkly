import db_AccessLayer as db
import json

def createHTMLTable_Srch (n_Max_Cnt, s_tblID, s_srchCol, s_srchCrit):
    try:
        n_Status = db.func_SrchTables (n_Max_Cnt, s_tblID, s_srchCol, s_srchCrit)

        if n_Status[0] != True:
            return s_tblID + ": func_SrchTables: call error..." + "||| Source Error: " + n_Status[1]
        else:
            output_Frames = n_Status[1] #pd.json_normalize(n_Status[1])
            output_HTML =output_Frames  #pd.DataFrame.to_html(output_Frames)
            #print (output_HTML)
            #------
            #output_HTML = n_Status[1]
            #------
            return output_HTML
    except:
        print(s_tblID + ": createHTMLTable_Srch: try-catch error...")
        return s_tblID + ": createHTMLTable_Srch: try-catch error..."
    

def createHTMLTable (n_Max_Cnt, s_Type):   
    try:
        n_Status = db.func_ReturnRows(n_Max_Cnt,s_Type,'','')
        if n_Status[0] != True:
            return "db.func_ReturnRows-->" + s_Type + ": call error..."
        else:
            output_Frames = n_Status[1] #pd.json_normalize(n_Status[1])
            output_HTML =output_Frames  #pd.DataFrame.to_html(output_Frames)
            #output_Frames = pd.json_normalize(n_Status[1])
            #output_HTML = pd.DataFrame.to_html(output_Frames)
            #print (output_HTML)
            return output_HTML
    except:
        return "createHTMLTable: syntax error..."    
#-----------------------------------------------------------------

def getCountTxt (s_Type):   
    try:
        match s_Type:
            case 'projects':
                n_Status = db.func_RetunRowCount('projects')
            case 'environments':
                n_Status = db.func_RetunRowCount('environments')
            case 'flags':
                n_Status = db.func_RetunRowCount('flags')

        if n_Status[0] != True:
            return "getCountTxt: call error @" + s_Type
        else:
            #output_Frames = pd.json_normalize(n_Status[1])
            output_Txt = n_Status[1][0]['count'] #pd.json_normalize(n_Status[1])
            return output_Txt
    except:
        return "getCountTxt: syntax error..."
#-----------------------------------------------------------------

def setLogs (n_type, a_Inputs):  #s_Inputs = array of vars to be written to the DB depending on the n_type
    try:
        match n_type:
            case 1: #write the count of proj,env,flags after each update
                n_Status = db.func_WriteStatus(1, a_Inputs)
    except:
        return False, "setLogs: syntax error @" + n_type
    
    s_return = "setlogs: " + str(n_Status[1]) + " @" + str(n_type)
    return True, s_return