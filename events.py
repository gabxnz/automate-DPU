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

        print(f"🔍 DEBUG CREATED: enrol={enrol_type} | status={status}")

        # 1. TRAVA DE STATUS: Se status for informado e diferente de 0 (0 = Ativo/Aceito | 1 = Pendente)
        if status is not None and int(status) != 0:
            print(f"⚠️ Solicitação ignorada por estar pendente/suspensa (Status: {status})")
            return None

        # 2. TIPOS PERMITIDOS: Permite manual, auto-inscrição e solicitações aprovadas
        if enrol_type in ['manual', 'self', 'apply']:
            return studentid
        else:
            print(f"ℹ️ Tipo de inscrição ignorado: {enrol_type}")
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

        print(f"🔍 DEBUG UPDATED: status={status}")

        # Trava também na atualização: Só envia se o status for 0 (Ativo/Aprovado)
        if status is not None and int(status) != 0:
            print(f"⚠️ Atualização ignorada pois status não é ativo (Status: {status})")
            return None

        return studentid

    except Exception as e:
        print(f"Erro em user_enrolment_updated: {str(e)}")
        return None