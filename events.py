import json

def user_enrolment_created(data):
    try:
        studentid = data.get('relateduserid')
        other = data.get('other', {})
        
        if isinstance(other, str):
            try:
                other = json.loads(other)
            except Exception:
                other = {}

        if not isinstance(other, dict):
            other = {}

        enrol_type = other.get('enrol')
        status = other.get('status', data.get('status'))

        print(f"🔍 EVENTO CREATED: enrol={enrol_type} | status={status} | user={studentid}")

        # 1. TRAVA DE STATUS: Se o status for informado e diferente de 0 (0 = Ativo)
        if status is not None and int(status) != 0:
            print(f"⚠️ Inscrição criada com status pendente/suspenso ({status}). Ignorado.")
            return None

        # 2. APENAS INSCRIÇÕES DIRETAS ('manual' e 'self')
        # 'apply' foi removido pois na criação ele é sempre uma solicitação pendente.
        if enrol_type in ['manual', 'self']:
            print(f"✅ Inscrição direta permitida ({enrol_type}) para usuário {studentid}")
            return studentid
        else:
            print(f"ℹ️ Solicitação de inscrição ignorada na criação (tipo: {enrol_type})")
            return None

    except Exception as e:
        print(f"Erro em user_enrolment_created: {str(e)}")
        return None


def user_enrolment_updated(data):
    try:
        studentid = data.get('relateduserid')
        courseid = data.get('courseid')

        if studentid is None or courseid is None:
            raise ValueError(f'Campos obrigatórios ausentes: studentid={studentid}, courseid={courseid}')

        other = data.get('other', {})
        if isinstance(other, str):
            try:
                other = json.loads(other)
            except Exception:
                other = {}

        if not isinstance(other, dict):
            other = {}

        status = other.get('status', data.get('status'))

        print(f"🔍 EVENTO UPDATED: status={status} | user={studentid} | course={courseid}")

        # Bloqueia apenas se o status for explicitamente diferente de 0
        if status is not None and int(status) != 0:
            print(f"⚠️ Atualização ignorada pois status não é ativo (Status: {status})")
            return None

        print(f"✅ Aprovação/Atualização válida enviada para o Excel (Usuário {studentid})")
        return studentid

    except Exception as e:
        print(f"Erro em user_enrolment_updated: {str(e)}")
        return None
    