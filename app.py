from flask import Flask, request, jsonify
import config
import requests as r
from get_data import get_user_data, get_course_data, format_data, is_user_enrolment_active
from events import user_enrolment_updated, user_enrolment_created
import os
import time

app = Flask(__name__)
app.config['DEBUG'] = config.DEBUG

recent_creations = {}

def cleanup_old_creations():
    now = time.time()
    to_delete = [key for key, timestamp in recent_creations.items() if now - timestamp > 60]
    for key in to_delete:
        del recent_creations[key]

def is_pending_request(data):
    """ Verifica se o payload recebido indica solicitação pendente de aprovação (status 1) """
    if not isinstance(data, dict):
        return False
        
    other = data.get('other', {})
    if isinstance(other, dict):
        userenrolment = other.get('userenrolment', {})
        if isinstance(userenrolment, dict):
            if str(userenrolment.get('status', '')) == '1':
                return True
        if str(other.get('status', '')) == '1':
            return True
            
    if str(data.get('status', '')) == '1':
        return True
        
    return False

@app.route('/', methods=['GET'])
def home():
    return "<h1>🚀 Servidor de Automação Moodle-DPU rodando!</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json() or {}
    print("========================================", flush=True)
    print(f">>> RECEBIDO DO MOODLE: {data}", flush=True)
    print("========================================", flush=True)

    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            print("--> Erro: Content-Type invalido", flush=True)
            return jsonify({'status': 'error', 'message': 'Unsupported Content-Type'}), 400

        eventname = str(data.get('eventname', ''))
        courseid = str(data.get('courseid')) if data.get('courseid') else None
        now = time.time()

        cleanup_old_creations()

        # 1. Se o payload indicar solicitação pendente (status 1), descarta
        if is_pending_request(data):
            print("--> Evento ignorado: Solicitação de inscrição pendente de aprovação.", flush=True)
            return jsonify({'status': 'ignored', 'reason': 'Solicitacao pendente'}), 200

        # 2. NOVA INSCRIÇÃO
        if eventname.endswith('user_enrolment_created'):
            userid = user_enrolment_created(data)
            if userid:
                userid_str = str(userid)
                
                # Valida se a inscrição já está ativa no Moodle
                if not is_user_enrolment_active(userid_str, courseid):
                    print(f"--> Inscrição criada para {userid_str} no curso {courseid}, mas ainda pendente de aprovação. Ignorado.", flush=True)
                    return jsonify({'status': 'ignored', 'reason': 'Inscricao pendente'}), 200

                recent_creations[(userid_str, courseid)] = now
                print(f"--> Nova inscrição ativa detectada para usuário {userid_str} no curso {courseid}.", flush=True)
                send_data_to_power_automate(userid_str, courseid)
            else:
                print("--> Evento 'created' recebido, mas nenhum userid foi extraído.", flush=True)

        # 3. ATUALIZAÇÃO / APROVAÇÃO DE INSCRIÇÃO
        elif eventname.endswith('user_enrolment_updated'):
            studentid = user_enrolment_updated(data)
            if studentid:
                studentid_str = str(studentid)
                creation_time = recent_creations.get((studentid_str, courseid))

                if creation_time and (now - creation_time < 30):
                    print(f"--> Evento 'updated' simultâneo ignorado para o usuário {studentid_str}.", flush=True)
                else:
                    # Confirma que a atualização tornou a inscrição ativa (aprovação)
                    if not is_user_enrolment_active(studentid_str, courseid):
                        print(f"--> Atualização recebida para {studentid_str}, mas o status da inscrição ainda não é ativo. Ignorado.", flush=True)
                        return jsonify({'status': 'ignored', 'reason': 'Inscricao nao ativa'}), 200

                    print(f"--> Aprovação/Atualização legítima detectada para o usuário {studentid_str}.", flush=True)
                    send_data_to_power_automate(studentid_str, courseid)
            else:
                print("--> Evento 'updated' recebido, mas nenhum studentid foi extraído por events.py.", flush=True)
        else:
            print(f"--> Evento não tratado: {eventname}", flush=True)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"!!! Erro ao processar webhook: {str(e)}", flush=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_data_to_power_automate(studentid, courseid):
    try:
        print(f"--> Buscando dados no Moodle para o usuário {studentid} e curso {courseid}...", flush=True)
        user_data = get_user_data(studentid)
        course_name = get_course_data(courseid)

        formatted_data = format_data(user_data)
        formatted_data['course_fullname'] = course_name

        print(f"--> Enviando para Power Automate: {formatted_data.get('username', studentid)} - {course_name}", flush=True)

        url = config.POWER_AUTOMATE_URL
        headers = {"Content-Type": "application/json"}

        response = r.post(str(url), headers=headers, json=formatted_data, timeout=config.TIMEOUT)

        if response.status_code in [200, 202]:
            print("--> Dados enviados COM SUCESSO para o Power Automate!", flush=True)
        else:
            print(f"!!! Erro no Power Automate. Status: {response.status_code} | Resposta: {response.text}", flush=True)

    except Exception as e:
        print(f"!!! Erro na função send_data_to_power_automate: {str(e)}", flush=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)