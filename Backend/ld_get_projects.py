import requests
import json
import ld_get_environments
import db_AccessLayer
import es_common

n_totalProjects = 0
x=0

#-----------------------------------------------------------------
#---------- Get All Projects from LaunchDarkly API ------
#-----------------------------------------------------------------
def get_all_projects(api_key,s_Proj_Ids, n_projCnt):
    if n_projCnt > 0:
        url = 'https://app.launchdarkly.com/api/v2/projects' + '?limit=' + str(n_projCnt)
        n_totalProjects = n_projCnt
    else:
        url = 'https://app.launchdarkly.com/api/v2/projects'

    if (len(s_Proj_Ids) == 0):
        headers = {'Authorization': api_key}
    else:
        headers = {'Authorization': api_key, 'projectKey': s_Proj_Ids}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        Projects = response.json()
        if n_projCnt == 0:
            n_totalProjects = Projects['totalCount']
            url = 'https://app.launchdarkly.com/api/v2/projects' + '?limit=' + str(n_totalProjects)
            headers = {'Authorization': api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                Projects = response.json()
                return Projects
            else:
                raise Exception(f'Error retrieving projects: {response.text}')
        else:
            return Projects
    else:
        raise Exception(f'Error retrieving projects: {response.text}')
#-----------------------------------------------------------------


#----------------------------------------------------------------------------------
#------------- Main Entry for Get All Projects Function ---------------------------
#------------- this function is for updating CRDB with data from LD----------------
#----------------------------------------------------------------------------------
def func_main_get_all_projects(api_key, s_ProjID, n_ffCnt):     # n_ffCnt--> 0 = Max ||| s_ProjID --> not implemented yet
    # Replace 'YOUR_API_KEY' with your actual LaunchDarkly API key
    x = 0
    projSaved = 0
    projFailed = 0
    arrResults = [[]]
    projects = get_all_projects(api_key,s_ProjID, n_ffCnt)

    flip_state = 1 #allow the DB to open the first time and closes the last time || #1=open + execute, 2=execute + close, 0=execute only
    # get the "items" in the projects list
    for key, value in projects.items():
        #print(key,'-->', value)
        if (key == 'items'):
            for project in value:
                x=x+1
                es_common.func_Logging(str(x) + '-->' + str(project))

                # control the DB state ||  #1=open+execute, 2=execute+close, 3=open+exec+close, 0=execute only
                if (len(value)==1):
                    flip_state=3
                else:
                    if (x==1):
                        flip_state=1
                    else:
                        if (x<len(value)):
                            flip_state = 0
                        else:
                            flip_state = 2
                projResults = db_AccessLayer.main('projects',flip_state,project['key'],'','',project)
                if (projResults == 'INSERT 0 1'):
                    projSaved = projSaved + 1
                else:
                    projFailed = projFailed + 1

                #---  Now call the write-all function for the environments for the above project
                envResults = ld_get_environments.main_all_environments(api_key, str(project['key']),0)

    db_AccessLayer.closeConnection()

    #--------------------------------------------------------------------------------
    if ('envResults' in vars() or 'envResults' in globals()):
        jsonResults = envResults + ',"ProjectsSaved": ' + str(projSaved) +  ',"ProjectsFailed": ' + str(projFailed)
    else:
        jsonResults = envResults + '"ProjectsSaved": ' + str(projSaved) +  ',"ProjectsFailed": ' + str(projFailed)


    return jsonResults
#--------------------------------------------------------------------------------


