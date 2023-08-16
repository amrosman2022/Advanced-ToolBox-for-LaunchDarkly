import json
import es_common

def login_from_js(json_string):
    try:
        data = json.loads(json_string)
        user_id = data['userid']
        password = data['password']

        # Replace with your actual authentication logic
        if user_id == es_common.s_g_user_id and password == es_common.s_g_user_pass:
            return {"success": True, "message": "Login successful"}
        else:
            return {"success": False, "message": "Invalid credentials"}
    except json.JSONDecodeError:
        return {"success": False, "message": "Invalid JSON data"}


