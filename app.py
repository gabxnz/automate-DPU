from flask import Flask, request, jsonify
import config
import requests as r
from get_data import get_user_data, get_course_data, format_data
from events import user_enrolment_updated, user_enrolment_created
import os
import time

app = Flask(__name__)
app.config['DEBUG'] = config.DEBUG

# Dicionário em memória para rastrear inscrições recentes: {(userid, courseid): timestamp}
recent_creations = {}

def cleanup_old_creations():
    """ Limpa registros de criação com mais de 60 segundos para liberar memória """
    now = time.time()
    to_delete = [key for key, timestamp in recent_creations.items() if now - timestamp > 60]
    for key in to_delete:
        del recent_creations[key]

@app.route('/', methods=['GET'])
def home():
    return "<h1>🚀 Servidor de Automação Moodle-DPU rodando!</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({'status': 'error', 'message': 'Unsupported Content-Type'}), 400

        data = request.get_json()
        eventname = str(data.get('eventname', ''))
        courseid = data.get('courseid')
        now = time.time()

        cleanup_old_creations()

        # 1. NOVA INSCRIÇÃO
        if eventname.endswith('user_enrolment_created'):
            userid = user_enrolment_created(data)
            if userid:
                # Marca o momento exato em que a inscrição foi criada
                recent_creations[(userid, courseid)] = now
                print(f"Nova inscrição detectada para usuário {userid} no curso {courseid}.")
                send_data_to_power_automate(userid, courseid)

        # 2. ATUALIZAÇÃO DE INSCRIÇÃO / PERFIL
        elif eventname.endswith('user_enrolment_updated'):
            studentid = user_enrolment_updated(data)
            if studentid:
                creation_time = recent_creations.get((studentid, courseid))

                # Se foi criado há menos de 30 segundos, é o disparo duplo inicial do Moodle -> IGNOURA
                if creation_time and (now - creation_time < 30):
                    print(f"Evento 'updated' simultâneo ignorado para o usuário {studentid}.")
                else:
                    print(f"Atualização legítima detectada para o usuário {studentid}.")
                    send_data_to_power_automate(studentid, courseid)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_data_to_power_automate(studentid, courseid):
    try:
        user_data = get_user_data(studentid)
        course_name = get_course_data(courseid)

        formatted_data = format_data(user_data)
        formatted_data['course_fullname'] = course_name

        print(f"Enviando dados para Power Automate: {formatted_data['username']} - {course_name}")

        url = config.POWER_AUTOMATE_URL
        headers = {"Content-Type": "application/json"}

        response = r.post(str(url), headers=headers, json=formatted_data, timeout=config.TIMEOUT)

        if response.status_code in [200, 202]:
            print("Dados enviados com sucesso para o Power Automate.")
        else:
            print(f"Erro no Power Automate: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Erro ao enviar dados para o Power Automate: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)git 