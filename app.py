from flask import Flask, request, jsonify
import config
import requests as r
from get_data import get_user_data, get_course_data, format_data
from events import user_enrolment_updated, user_enrolment_created
import os

app = Flask(__name__)
app.config['DEBUG'] = config.DEBUG

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({'status': 'error', 'message': 'Unsupported Content-Type'}), 400

        data = request.get_json()
        eventname = data.get('eventname')

        if eventname == '\\core\\event\\user_enrolment_updated':
            studentid = user_enrolment_updated(data)
            if studentid:
                print("Enviando dados para o Power Automate (Inscrição Atualizada)...")
                send_data_to_power_automate(studentid, data.get('courseid'))

        elif eventname == '\\core\\event\\user_enrolment_created':
            userid = user_enrolment_created(data)
            if userid:
                print("Enviando dados para o Power Automate (Nova Inscrição)...")
                send_data_to_power_automate(userid, data.get('courseid'))

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

        print(f"Dados formatados para envio: {formatted_data}")

        url = config.POWER_AUTOMATE_URL
        headers = {"Content-Type": "application/json"}

        response = r.post(str(url), headers=headers, json=formatted_data, timeout=config.TIMEOUT)

        if response.status_code in [200, 202]:
            print("Dados enviados com sucesso para o Power Automate.")
        else:
            print(f"Erro ao enviar dados para Power Automate: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Erro ao enviar dados para o Power Automate: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)