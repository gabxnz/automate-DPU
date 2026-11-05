import requests
import config

def get_user_data(userid):
    endpoint = f"{config.MOODLE_URL.rstrip('/')}/webservice/rest/server.php"
    params = {
        "wstoken": config.MOODLE_API_TOKEN,
        "wsfunction": "core_user_get_users_by_field",
        "moodlewsrestformat": "json",
        "field": "id",
        "values[0]": userid
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=config.TIMEOUT)
        
        if not response.text.strip().startswith(('{', '[')):
            print(f"!!! ERRO MOODLE (USUARIO {userid}): Resposta nao e JSON. Conteudo: {response.text[:200]}", flush=True)
            return None
            
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data
    except Exception as e:
        print(f"!!! Erro ao buscar usuário no Moodle: {str(e)}", flush=True)
        return None

def get_course_data(courseid):
    endpoint = f"{config.MOODLE_URL.rstrip('/')}/webservice/rest/server.php"
    params = {
        "wstoken": config.MOODLE_API_TOKEN,
        "wsfunction": "core_course_get_courses",
        "moodlewsrestformat": "json",
        "options[ids][0]": courseid
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=config.TIMEOUT)
        
        if not response.text.strip().startswith(('{', '[')):
            print(f"!!! ERRO MOODLE (CURSO {courseid}): Resposta nao e JSON. Conteudo: {response.text[:200]}", flush=True)
            return "Curso Desconhecido"
            
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("fullname", "Curso Desconhecido")
        return "Curso Desconhecido"
    except Exception as e:
        print(f"!!! Erro ao buscar curso no Moodle: {str(e)}", flush=True)
        return "Curso Desconhecido"

def format_data(user_data):
    if not user_data or not isinstance(user_data, dict):
        return {"username": "", "firstname": "", "lastname": "", "email": ""}
    return {
        "username": user_data.get("username", ""),
        "firstname": user_data.get("firstname", ""),
        "lastname": user_data.get("lastname", ""),
        "email": user_data.get("email", "")
    }