import json
import os
from cryptography.fernet import Fernet
import es_common 

# Generate a new encryption key (keep this key safe)
# This key should be generated once and kept secure for both encryption and decryption.
# You can use Fernet.generate_key() to create a new key and then encode it in base64.
encryption_key_base64 = b'ANgvGFIEyaIk4w_sKqg5z7qeO5M9vnTsx4U6jPajnOg='
# Generate a Fernet key and encode it in URL-safe base64 format
#fernet_key = Fernet.generate_key()
#encryption_key_base64 = Fernet.generate_key().decode('utf-8')

# -----------------------------------------------
# ------------- Read the settings ---------------
# -----------------------------------------------
def read_settings(file_path, encryption_key):
    """
    Read and decrypt application settings from an encrypted JSON file.

    Args:
        file_path (str): Path to the encrypted JSON file.
        encryption_key (bytes): Base64 encoded encryption key for decryption.

    Returns:
        dict: Dictionary containing the decrypted application settings.
    """
    return_info = []
    settings = {}
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
            fernet = Fernet(encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            settings = json.loads(decrypted_data)
            return_info.append ('{"ErrorCode": 0, "Message": "Data Read", "function": "se_Settings.read_settings"}')
            return_info.append (settings)
            print(f"Setting file opened successfuly")
    else:
        
        return_info.append ('{"ErrorCode": -1000, "Message": "File Not Found", "function": "se_Settings.read_settings"}')
        return_info.append (settings)
        print(f"Setting file was not found")

    return return_info

# -----------------------------------------------
# ------------- Write the settings ---------------
# -----------------------------------------------
def write_settings(file_path, settings_input, encryption_key):
    """
    Encrypt and write application settings to an encrypted JSON file.

    Args:
        file_path (str): Path to the encrypted JSON file.
        settings_input (str): Comma-separated string of settings in format "key1:value1,key2:value2,...".
        encryption_key (bytes): Base64 encoded encryption key for encryption.

    Returns:
        dict: Dictionary containing the updated application settings.
    """
    return_info = []
    settings = {}
    settings_list = settings_input.split(",")
    
    for setting in settings_list:
        key, value = setting.split(":",1)
        settings[key.strip()] = value.strip()
    
    with open(file_path, 'wb') as file:
        fernet = Fernet(encryption_key)
        encrypted_data = fernet.encrypt(json.dumps(settings).encode())
        file.write(encrypted_data)
    
    return_info.append ('{"ErrorCode": 0, "Message": "Data Saved", "function": "se_Settings.read_settings"}')
    return_info.append (settings)
    return return_info


def func_selector (n_state, new_settings_input):
    settings_file = "app_settings_encrypted.json"

    if n_state == '1':
        updated_settings = write_settings(settings_file, new_settings_input, encryption_key_base64)
    else:
        updated_settings = read_settings(settings_file, encryption_key_base64)
        #n_Error = es_common.func_getFldJSON(updated_settings[0],'ErrorCode')

    return updated_settings
    

    # Update settings using comma-separated input
    #new_settings_input = "api_key:api-21e8bc01-3972-4b3d-a5a3-92f381397c80,key_name:ao-api-access,logging:0,user_fname:Amr,user_lname:Osman, loginid:amrosman,loginpass:qwerty1"


