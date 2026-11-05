import requests
import config
import re

def clean_moodle_text(text):
    """ Remove etiquetas de idioma do Moodle (ex: {mlang pt_br}Texto{mlang}) """
    if not text or not isinstance(text, str):
        return text if text is not None else ""
    
    match = re.search(r'\{mlang\s+pt_br\}(.*?)(?:\{mlang\}|\{m|\{|\Z)', text, re.IGNORECASE | re.DOTALL)
    if match:
        text = match.group(1)
    
    cleaned = re.sub(r'\{[^\}]+\}', '', text)
    return cleaned.strip()

def normalize_uf(raw_uf):
    """ Converte o nome do estado ou variações para a sigla de 2 letras (ex: DF, SP, PR) """
    if not raw_uf or not isinstance(raw_uf, str):
        return ""
    clean = raw_uf.strip().upper()
    
    uf_map = {
        "ACRE": "AC", "ALAGOAS": "AL", "AMAPÁ": "AP", "AMAPA": "AP",
        "AMAZONAS": "AM", "BAHIA": "BA", "CEARÁ": "CE", "CEARA": "CE",
        "DISTRITO FEDERAL": "DF", "DISTRITO FE": "DF", "ESPÍRITO SANTO": "ES", "ESPIRITO SANTO": "ES",
        "GOIÁS": "GO", "GOIAS": "GO", "MARANHÃO": "MA", "MARANHAO": "MA",
        "MATO GROSSO": "MT", "MATO GROSSO DO SUL": "MS", "MINAS GERAIS": "MG",
        "PARÁ": "PA", "PARA": "PA", "PARAIBA": "PB", "PARAÍBA": "PB",
        "PARANÁ": "PR", "PARANA": "PR", "PERNAMBUCO": "PE", "PIAUÍ": "PI", "PIAUI": "PI",
        "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS",
        "RONDÔNIA": "RO", "RONDONIA": "RO", "RORAIMA": "RR", "SANTA CATARINA": "SC",
        "SÃO PAULO": "SP", "SAO PAULO": "SP", "SERGIPE": "SE", "TOCANTINS": "TO"
    }
    
    if clean in uf_map:
        return uf_map[clean]
    
    if len(clean) == 2 and clean.isalpha():
        return clean
        
    for name, sigla in uf_map.items():
        if clean in name or name in clean:
            return sigla
            
    return clean[:2]

def get_endpoint():
    base_url = config.MOODLE_URL.rstrip('/')
    if not base_url.endswith('/webservice/rest/server.php'):
        return f"{base_url}/webservice/rest/server.php"
    return base_url

def is_user_enrolment_active(userid, courseid):
    """ Consulta o Moodle com onlyactive=1 para garantir que a inscrição está APROVADA/ATIVA """
    if not userid or not courseid:
        return True

    endpoint = get_endpoint()
    params = {
        "wstoken": config.MOODLE_API_TOKEN,
        "wsfunction": "core_enrol_get_enrolled_users",
        "moodlewsrestformat": "json",
        "courseid": courseid,
        "options[0][name]": "userids",
        "options[0][value]": userid,
        "options[1][name]": "onlyactive",
        "options[1][value]": 1
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=config.TIMEOUT)
        if not response.text.strip().startswith(('{', '[')):
            print(f"!!! ERRO MOODLE (VERIFICAR ATIVO): Resposta nao e JSON", flush=True)
            return True
            
        data = response.json()

        if isinstance(data, list):
            # Se for retornado vazio [], significa que o usuário é pendente ou não ativo
            return len(data) > 0

        return True
    except Exception as e:
        print(f"!!! Erro ao verificar status ativo da inscrição no Moodle: {str(e)}", flush=True)
        return True

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
            "raca": "", "genero": "", "cargo": "", "perfil": "", "vinculo": ""
        }

    # 1. Nome Completo Limpo
    firstname = clean_moodle_text(user_data.get("firstname", ""))
    lastname = clean_moodle_text(user_data.get("lastname", ""))
    fullname = f"{firstname} {lastname}".strip()

    # 2. Extração de Campos Customizados
    custom_fields = {}
    if "customfields" in user_data and isinstance(user_data["customfields"], list):
        for field in user_data["customfields"]:
            shortname = field.get("shortname")
            value = clean_moodle_text(field.get("value", ""))
            if shortname:
                custom_fields[shortname] = value

    # 3. Formatação do CPF (Garante 11 dígitos com zeros à esquerda e pontuação 000.000.000-00)
    raw_username = str(user_data.get("username", "") or custom_fields.get("cpf", "")).strip()
    clean_cpf = "".join(filter(str.isdigit, raw_username)).zfill(11)
    
    if len(clean_cpf) == 11:
        formatted_cpf = f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}"
    else:
        formatted_cpf = raw_username

    # 4. Normalização do Gênero (Masculino -> M | Feminino -> F)
    raw_genero = (custom_fields.get("genero", "") or custom_fields.get("sexo", "")).strip()
    genero_lower = raw_genero.lower()
    if "masculino" in genero_lower or genero_lower == "m":
        genero_final = "M"
    elif "feminino" in genero_lower or genero_lower == "f":
        genero_final = "F"
    else:
        genero_final = raw_genero

    # 5. Normalização do Vínculo / Cargo / Perfil
    raw_cargo = (
        custom_fields.get("vinculo", "") or 
        custom_fields.get("vinc_funcional", "") or 
        custom_fields.get("perfil", "") or 
        custom_fields.get("cargo", "") or
        custom_fields.get("tipo", "")
    ).strip()
    
    cargo_lower = raw_cargo.lower()

    if "extern" in cargo_lower or "p/ext" in cargo_lower or "público" in cargo_lower or "publico" in cargo_lower:
        cargo_final = "P/Ext"
    elif "estagiár" in cargo_lower or "estagiari" in cargo_lower or cargo_lower == "e":
        cargo_final = "E"
    elif "servidor" in cargo_lower or cargo_lower == "s":
        cargo_final = "S"
    elif "membro" in cargo_lower or "defensor" in cargo_lower or cargo_lower == "m":
        cargo_final = "M"
    elif "terceirizad" in cargo_lower or cargo_lower == "t":
        cargo_final = "T"
    else:
        cargo_final = raw_cargo

    # 6. Normalização da UF (sigla de 2 letras)
    raw_uf = custom_fields.get("uf", "") or custom_fields.get("estado", "")
    uf_final = normalize_uf(raw_uf)

    city = clean_moodle_text(user_data.get("city", "")) or custom_fields.get("cidade", "") or custom_fields.get("city", "")
    regiao = custom_fields.get("regiao", "")
    raca = custom_fields.get("raca", "") or custom_fields.get("racacor", "")

    payload = {
        "nome": fullname,
        "firstname": firstname,
        "lastname": lastname,
        "username": formatted_cpf,
        "cpf": formatted_cpf,
        "email": user_data.get("email", ""),
        "cidade": city,
        "uf": uf_final,
        "regiao": regiao,
        "raca": raca,
        "genero": genero_final,
        "cargo": cargo_final,
        "perfil": cargo_final,
        "vinculo": cargo_final
    }

    payload.update(custom_fields)
    
    payload["cpf"] = formatted_cpf
    payload["username"] = formatted_cpf
    payload["uf"] = uf_final
    payload["genero"] = genero_final
    payload["cargo"] = cargo_final
    payload["perfil"] = cargo_final
    payload["vinculo"] = cargo_final

    return payload