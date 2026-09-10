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

        enrol_type = other.get('enrol') if isinstance(other, dict) else None

        if enrol_type in ['manual', 'self', 'apply']:
            return studentid
        else:
            print(f"Tipo de inscrição ignorado: {enrol_type}")
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

        return studentid

    except Exception as e:
        print(f"Erro em user_enrolment_updated: {str(e)}")
        return None