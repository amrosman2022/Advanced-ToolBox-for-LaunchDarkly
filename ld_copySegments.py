import json
import sys
import requests
import os
import time

# Example usage:
error_list = []
#------------------------------------------------------------------------------------------------
#-----------------------------Support Function --------------------------------------------------
#------------------------------------------------------------------------------------------------
def isKeyExist(key_to_check, my_dict):
    if key_to_check in my_dict:
        return True
    else:
        return False


#------------------------------------------------------------------------------------------------
#-----------------------------Support Function --------------------------------------------------
#------------------------------------------------------------------------------------------------
def func_errors(mode=1, error_message=""):
    if mode == 1:
        error_list.append(error_message)
    else:
        # Print the list of errors
        print("\033[37mList of errors:\033[00m")
        for error in error_list:
            print("\033[33m" + error if (error != None) else " " + "!\033[0m")

#------------------------------------------------------------------------------------------------
#---------------Save the segments' data to the already created header ---------------------------
#------------------------------------------------------------------------------------------------
def func_saveSegmentDetails(key):
    
    url = "https://app.launchdarkly.com/api/v2/segments/" + g_o_loadedData.get('destProjID') + "/" + g_o_loadedData.get('destEnvID') + "/" + key['key']

    try:
        payload = {
        "patch": [
            {
            "op": "add",
            "path": "/included",
            "value": key["included"]
            },
            {
            "op": "add",
            "path": "/excluded",
            "value": key["excluded"]
            },
            {
            "op": "add",
            "path": "/includedContexts",
            "value": key["includedContexts"]
            },
            {
            "op": "add",
            "path": "/excludedContexts",
            "value": key["excludedContexts"]
            }
        ]
        }

        headers = {
        "Content-Type": "application/json",
        "Authorization": g_o_loadedData.get('destLDSub')
        }

        response = requests.patch(url, json=payload, headers=headers)

        data = response.json()
        func_errors(1, f"STATUS: Segment details {key['name']} was added to target LD subscription")
        return True
    except requests.exceptions as e:
        func_errors(1, f"ERROR: Segment details {key['name']} failed to write {e}")
        return True
    

#------------------------------------------------------------------------------------------------
#---------------------Save the segments' headers to the target LD subscription ------------------
#------------------------------------------------------------------------------------------------
def func_saveAllSegments(payload):
    url = "https://app.launchdarkly.com/api/v2/segments/" + g_o_loadedData.get('destProjID') + "/" + g_o_loadedData.get('destEnvID')

    for key in payload['items']:
        payload = {
        "name": key['name'],
        "key": key['key'],
        "description": key['description'] if isKeyExist('description', key) else "",
        "tags": key['tags'],
        "unbounded": False
        }

        headers = {
        "Content-Type": "application/json",
        "Authorization": g_o_loadedData.get('destLDSub')
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201 or response.status_code == 409:
                data = response.json()
                data = func_saveSegmentDetails(key)
                func_errors(1, f"STATUS: Segment header {key['name']} was saved or already exists @ target LD subscription")
            else:
                func_errors(1, f"ERROR: Error saving {key['name']} ||| {response.status_code}")
                
        except requests.exceptions as e:
            func_errors(1, f"ERROR: URL post error {e}")



#------------------------------------------------------------------------------------------------
#------------------------- Get all the Segments from the the Targer LD Subscription ------------
#------------------------------------------------------------------------------------------------
def func_getAllSegments():

    try:
        url = "https://app.launchdarkly.com/api/v2/segments/" + g_o_loadedData.get('sourceProjID') + "/" + g_o_loadedData.get('sourceEnvID')

        headers = {"Authorization": g_o_loadedData.get('sourceLDSub')} 

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            func_errors(1, f"ERROR: Error calling the LD API ||| {response.status_code}")
            return None
        
        s_segmentsData = response.json()
       
        #print(s_segmentsData)
        return s_segmentsData
    except json.JSONDecodeError as e:
        func_errors(1, f"ERROR: Error decoding JSON from API Call ||| {e}")
        return None



#------------------------------------------------------------------------------------------------
#------------------------- load the JSON attribs to a local global variable --------------------
#------------------------------------------------------------------------------------------------
def func_LoadJjsonFromFile(file_path):
    try:
        # Get the full path of the Python script
        script_path = os.path.abspath(__file__)

        # Extract the directory where the script is located
        script_directory = os.path.dirname(script_path)

        func_errors(1,f"STATUS: Directory of the Python script ||| {script_directory}")
        file_path = script_directory + "/" + file_path

        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        func_errors(1, f"ERROR: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        func_errors(1, f"ERROR: Error decoding JSON from file '{file_path}' ||| {e}")
        return None


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# -- example: 
#------------------------------------------------------------------------------------------------
def main():
    global g_s_SegmentsData
    global g_o_loadedData

    os.system('clear')
    os.system("echo '\033]11;#004400\007'")
    if len(sys.argv) != 2:
        func_errors(1, "ERROR: Script aborted for missing parameters JSON file. Usage= ld_copySegments.py <file_path>")
        #return False
    
    bContinue = input ("Segments' data will be overwritten on the target LD, continue(Y/N)?")
    if bContinue.upper() != "Y":
        func_errors(1, "Aborted by user input (N)")
        return False

    print(f"\033[36m{time.asctime()}: ld_copySegments.py started the copy process....\033[0m")
    #file_path = sys.argv[1]
    file_path = "supportfiles/ld_CS.json"

    g_o_loadedData = func_LoadJjsonFromFile(file_path)

    if g_o_loadedData:
        func_errors(1, "STATUS: Loaded JSON settings from [ld_CS.json]")
        #print(g_o_loadedData)
        s_segmentsData = func_getAllSegments()
        results = func_saveAllSegments(s_segmentsData)
        func_errors(1,results)

    func_errors(2,"")
    print(f"\033[36m{time.asctime()}: ld_copySegments.py finished the copy process....\033[0m")


if __name__ == "__main__":
    main()
    

