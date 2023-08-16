import requests
import json
import math
import db_AccessLayer


n_totalFF = 0
ffSaved = 0
ffFailed = 0

def run_URL (api_key,s_projKey, s_envKey, n_ffCnt, n_startLoad):
    if n_ffCnt > 0:
        url = 'https://app.launchdarkly.com/api/v2/flags/' + s_projKey + "?env=" + s_envKey + "&limit=" + str(n_ffCnt) + "&offset=" + str(n_startLoad)
        n_totalFF = n_ffCnt
    else:
        url = 'https://app.launchdarkly.com/api/v2/flags/' + s_projKey + "?env=" + s_envKey
    
    headers = {'Authorization': api_key, 'env':'aosman'}
    response = requests.get(url, headers=headers)
    return response

def get_all_FF(api_key,s_projKey, s_envKey, n_ffCnt):
    
    ffSaved = 0
    response = run_URL(api_key,s_projKey, s_envKey, n_ffCnt,0)
    if response.status_code == 200:  #504 is LD timing out due to large dataset
        FFs = response.json()
        n_totalFF = FFs['totalCount']
        
        if n_ffCnt < n_totalFF and n_ffCnt != -1:   
            n_skipCount=math.ceil(n_totalFF/100)
            #print(n_skipCount)
            for x in range(int(n_skipCount)):
                n_startLoad=(x)*100
                #print(n_startLoad)
            response = run_URL(api_key,s_projKey, s_envKey, n_totalFF,n_startLoad)
            if response.status_code == 200:
                FFs = response.json()
                return FFs
            else:
                raise Exception(f'Error retrieving FFs: {response.text}')
        else:
            return FFs
    else:
        raise Exception(f'Error retrieving FFs: {response.text}')

def main_all_FFs(api_key, s_projKey, s_envKey, n_ffCnt):
    global ffSaved
    global ffFailed
    ffResults = ""
    
    # Replace 'YOUR_API_KEY' with your actual LaunchDarkly API key
    #api_key = 'api-21e8bc01-3972-4b3d-a5a3-92f381397c80' #ao-api-access
    FFs = get_all_FF(api_key, s_projKey, s_envKey, n_ffCnt)

    # get the "items" in the FFs list
    flip_state = 1 #allow the DB to open the first time and closes the last time || #1=open+execute, 2=execute+close, 3=open+exec+close, 0=execute only
    for key, value in FFs.items():
        if (key == 'items'):
            for FF in value:
                flip_state = 0
                ffResults = db_AccessLayer.main('flags',flip_state,s_projKey,s_envKey, FF["key"],json.dumps(FF))
                if (ffResults == 'INSERT 0 1'):
                    ffSaved = ffSaved + 1
                else:
                    ffFailed = ffFailed + 1

    #  ------------------------------------------------------------------------------------
    if ('jsonResults' in vars() or 'jsonResults' in globals()):
        jsonResults = ' ,"FlagsSaved": ' + str(ffSaved) + ', "FlagsFailed": ' + str(ffFailed)
    else:
        jsonResults = ' "FlagsSaved": ' + str(ffSaved) + ', "FlagsFailed": ' + str(ffFailed)
    return jsonResults
