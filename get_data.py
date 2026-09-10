import re
import json
from requests import request
import config

def get_user_data(userid):
    try:
        url = config.MOODLE_API_URL
        params = {
            "wstoken": config.MOODLE_API_TOKEN,
            "wsfunction": "core_user_get_users_by_field",
            "field": "id",
            "values[0]": userid,
            "moodlewsrestformat": "json",
        }

        response = request("GET", str(url), params=params, timeout=config.TIMEOUT)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return extract_user_data(data[0])
        else:
            print(f"Usuário id={userid} não encontrado no Moodle. Resposta: {data}")
            return {}

    except Exception as e:
        print(f"Erro ao buscar usuário no Moodle: {str(e)}")
        return {}

def get_course_data(courseid):
    try:
        url = config.MOODLE_API_URL
        params = {
            "wstoken": config.MOODLE_API_TOKEN,
            "wsfunction": "core_course_get_courses",
            "moodlewsrestformat": "json",
            "options[ids][0]": courseid
        }

        response = request("GET", str(url), params=params, timeout=config.TIMEOUT)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0].get('fullname', 'Curso Desconhecido')
        elif isinstance(data, dict):
            return data.get('fullname', 'Curso Desconhecido')
        return 'Curso Desconhecido'

    except Exception as e:
        print(f"Erro ao buscar curso no Moodle: {str(e)}")
        return 'Curso Desconhecido'


def extract_user_data(user_data):
    if not isinstance(user_data, dict):
        return {}

    firstname = user_data.get('firstname', '').strip()
    lastname = user_data.get('lastname', '').strip()
    fullname_moodle = f"{firstname} {lastname}".strip()

    result = {
        'username': user_data.get('username', ''),
        'fullname': fullname_moodle if fullname_moodle else user_data.get('fullname', ''),
        'email': user_data.get('email', ''),
        'city': user_data.get('city', '')
    }

    custom_fields = user_data.get('customfields', [])
    interesting_fields = ['etinia', 'genero', 'vinculo', 'municipio', 'uf', 'nome_completo']

    for field in custom_fields:
        if field.get('shortname') in interesting_fields:
            value = field.get('value', '')

            if '{mlang pt_br}' in str(value):
                try:
                    value = str(value).split('{mlang pt_br}')[1].split('{mlang')[0]
                except IndexError:
                    pass
            
            result[field['shortname']] = str(value).strip()

    nome_custom = result.get('nome_completo', '').strip()
    if nome_custom and nome_custom != "Valor não encontrado":
        result['nome_completo'] = nome_custom
    else:
        result['nome_completo'] = result['fullname'] if result['fullname'] else 'Nome Não Encontrado'

    municipio_custom = result.get('municipio', '').strip()
    if not municipio_custom or municipio_custom == "Valor não encontrado":
        result['municipio'] = result['city'] if result['city'] else 'Município Não Encontrado'

    return result


def format_data(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            data = {}
    if not isinstance(data, dict):
        data = {}

    username = str(data.get('username', ''))
    cpf_digits = re.sub(r'\D', '', username)
    
    if 0 < len(cpf_digits) < 11:
        cpf_digits = cpf_digits.zfill(11)

    if len(cpf_digits) == 11:
        cpf = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
    else:
        cpf = username if username else "?"

    name = data.get('nome_completo') or data.get('fullname') or 'Nome Não Encontrado'
    name_parts = name.split()
    prepositions = ['de', 'da', 'do', 'das', 'dos', 'e']
    formatted_name = ' '.join([part.capitalize() if part.lower() not in prepositions else part.lower() for part in name_parts])
    
    municipio = data.get('municipio') or 'Município Não Encontrado'
    municipio_parts = municipio.split()
    formatted_municipio = ' '.join([part.capitalize() for part in municipio_parts])

    vinculo_map = {
        'Estagiário': 'E',
        'Voluntário': 'V',
        'Defensor Público': 'D',
        'Servidor / Empregado Público': 'S',
        'Terceirizado': 'T',
        'Público Externo': 'P/Ext'
    }
    vinculo = data.get('vinculo', 'P/Ext')
    vinculo_abbr = vinculo_map.get(vinculo, 'P/Ext')

    uf = data.get('uf', '')
    uf_parts = uf.split(' - ')
    uf_abbr = uf_parts[-1] if len(uf_parts) > 1 else uf

    genero_map = {
        'Masculino': 'M',
        'Feminino': 'F'
    }
    genero = data.get('genero', '')
    genero_abbr = genero_map.get(genero, '')

    formatted_data = {
        'username': cpf,
        'nome_completo': formatted_name if formatted_name else 'Nome Não Encontrado',
        'vinculo': vinculo_abbr,
        'uf': uf_abbr,
        'genero': genero_abbr,
        'etinia': data.get('etinia', ''),
        'email': data.get('email', ''),
        'municipio': formatted_municipio if formatted_municipio else 'Município Não Encontrado'
    }

    return formatted_data