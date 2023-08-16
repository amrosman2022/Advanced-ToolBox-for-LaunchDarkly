import requests
import json
import ld_get_FF
import db_AccessLayer

n_totalEnvironments = 0
envSaved = 0
envFailed = 0

def get_all_environments(api_key,s_projKey, n_envCnt):
    if n_envCnt > 0:
        url = 'https://app.launchdarkly.com/api/v2/projects/' + s_projKey + "/environments?" + "limit=" + str(n_envCnt)
        n_totalEnvironments = n_envCnt
    else:
        url = 'https://app.launchdarkly.com/api/v2/projects/' + s_projKey + "/environments"

    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        Environments = response.json()
        n_totalEnvironments = Environments['totalCount']
        if n_envCnt == 0 and n_totalEnvironments > 19:
            url = 'https://app.launchdarkly.com/api/v2/projects/' + s_projKey + "/environments?" + "limit=" + str(n_totalEnvironments)
            headers = {'Authorization': api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                Environments = response.json()
                return Environments
            else:
                raise Exception(f'Error retrieving environments: {response.text}')
        else:
            return Environments
    else:
        raise Exception(f'Error retrieving Environments: {response.text}')


def main_all_environments(api_key, s_projKey, n_envCnt):
    # Replace 'YOUR_API_KEY' with your actual LaunchDarkly API key
    #api_key = 'api-21e8bc01-3972-4b3d-a5a3-92f381397c80' #ao-api-access
    global envSaved
    global envFailed
    Environments = get_all_environments(api_key, s_projKey, n_envCnt)

    flip_state = 1 #allow the DB to open the first time and closes the last time || #1=open+execute, 2=execute+close, 3=open+exec+close, 0=execute only
    # get the "items" in the Environments list
    for key, value in Environments.items():
        #print(key,'-->', value)
        if (key == 'items'):
            for environment in value:
                flip_state = 0    
                envResults = db_AccessLayer.main('environments',flip_state,s_projKey,environment["key"],'',json.dumps(environment))
                if (envResults == 'INSERT 0 1'):
                    envSaved += 1
                else:
                    envFailed = envFailed + 1
                #---  Now call the write-all function for the Flags for the above environment
                ffResults = ld_get_FF.main_all_FFs(api_key,str(s_projKey), str(environment['key']), -1)

    # ------ Return the result of writing the data CRDB
    if ('ffResults' in vars() or 'ffResults' in globals()):
        jsonResults = ffResults + ',"EnvironmentsSaved": ' + str(envSaved) + ',"EnvironmentsFailed": ' + str(envFailed)
    else:
        jsonResults = ffResults + '"EnvironmentsSaved": ' + str(envSaved) + ',"EnvironmentsFailed": ' + str(envFailed)

    return jsonResults




