import requests
import config
import re

def clean_moodle_text(text):
    """ Remove etiquetas de idioma do Moodle (ex: {mlang pt_br}Texto{mlang}) """
    if not text or not isinstance(text, str):
        return text if text is not None else ""
    
    # 1. Extrai preferencialmente o texto dentro da tag pt_br
    match = re.search(r'\{mlang\s+pt_br\}(.*?)(?:\{mlang\}|\{m|\{|\Z)', text, re.IGNORECASE | re.DOTALL)
    if match:
        text = match.group(1)
    
    # 2. Remove qualquer outra etiqueta {mlang ...} residual
    cleaned = re.sub(r'\{[^\}]+\}', '', text)
    return cleaned.strip()

def get_endpoint():
    """ Garante que a URL do Web Service do Moodle esteja com o caminho correto """
    base_url = config.MOODLE_URL.rstrip('/')
    if not base_url.endswith('/webservice/rest/server.php'):
        return f"{base_url}/webservice/rest/server.php"
    return base_url

def get_user_data(userid):
    endpoint = get_endpoint()
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

        if isinstance(data, dict) and "exception" in data:
            print(f"!!! ERRO DE API DO MOODLE (USUARIO {userid}): {data.get('message')}", flush=True)
            return None

        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data if isinstance(data, dict) else None

    except Exception as e:
        print(f"!!! Erro ao buscar usuário no Moodle: {str(e)}", flush=True)
        return None

def get_course_data(courseid):
    endpoint = get_endpoint()
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

        if isinstance(data, dict) and "exception" in data:
            print(f"!!! ERRO DE API DO MOODLE (CURSO {courseid}): {data.get('message')}", flush=True)
            return "Curso Desconhecido"

        if isinstance(data, list) and len(data) > 0:
            raw_title = data[0].get("fullname", "Curso Desconhecido")
            return clean_moodle_text(raw_title)
        return "Curso Desconhecido"

    except Exception as e:
        print(f"!!! Erro ao buscar curso no Moodle: {str(e)}", flush=True)
        return "Curso Desconhecido"

def format_data(user_data):
    if not user_data or not isinstance(user_data, dict):
        return {
            "nome": "", "firstname": "", "lastname": "", "username": "",
            "cpf": "", "email": "", "cidade": "", "uf": "", "regiao": "",
            "raca": "", "genero": "", "cargo": "", "perfil": ""
        }

    # 1. Nome Completo Limpo
    firstname = clean_moodle_text(user_data.get("firstname", ""))
    lastname = clean_moodle_text(user_data.get("lastname", ""))
    fullname = f"{firstname} {lastname}".strip()

    # 2. Extração de Campos Customizados Limpos
    custom_fields = {}
    if "customfields" in user_data and isinstance(user_data["customfields"], list):
        for field in user_data["customfields"]:
            shortname = field.get("shortname")
            value = clean_moodle_text(field.get("value", ""))
            if shortname:
                custom_fields[shortname] = value

    # 3. Formatação do CPF (Garante 11 dígitos com máscara 000.000.000-00)
    raw_username = str(user_data.get("username", "") or custom_fields.get("cpf", "")).strip()
    clean_cpf = "".join(filter(str.isdigit, raw_username)).zfill(11)
    
    if len(clean_cpf) == 11:
        formatted_cpf = f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}"
    else:
        formatted_cpf = raw_username

    # 4. Mapeamento dos campos tratados
    city = clean_moodle_text(user_data.get("city", "")) or custom_fields.get("cidade", "") or custom_fields.get("city", "")
    uf = custom_fields.get("uf", "") or custom_fields.get("estado", "")
    regiao = custom_fields.get("regiao", "")
    raca = custom_fields.get("raca", "") or custom_fields.get("racacor", "")
    genero = custom_fields.get("genero", "") or custom_fields.get("sexo", "")
    cargo = custom_fields.get("cargo", "") or custom_fields.get("perfil", "")

    payload = {
        "nome": fullname,
        "firstname": firstname,
        "lastname": lastname,
        "username": user_data.get("username", ""),
        "cpf": formatted_cpf,
        "email": user_data.get("email", ""),
        "cidade": city,
        "uf": uf,
        "regiao": regiao,
        "raca": raca,
        "genero": genero,
        "cargo": cargo,
        "perfil": cargo
    }

    payload.update(custom_fields)
    return payload