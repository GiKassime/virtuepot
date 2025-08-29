from flask import Flask, render_template, current_app, request, session
from pymodbus.client.sync import ModbusTcpClient
from datetime import datetime
from flask import jsonify
import secrets
import subprocess
import os

app = Flask(__name__)

secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

def current_time():
    now = datetime.now().isoformat()
    return now

@app.route('/api', methods=['POST', 'GET'])
def api():
    host = '192.168.0.26'
    port = 502
    client = ModbusTcpClient(host, port)
    client.connect()
    result = client.read_holding_registers(101, 10, unit=0)
    data = {
        "datetime": current_time(),
        "data": result.registers
    }
    return jsonify(data)

@app.route('/toggle_valve', methods=['POST'])
def toggle_valve():
    valve = request.form.get('valve')
    if 'sequence' not in session:
        session['sequence'] = []
    sequence = session['sequence']

    sequence.append(valve)
    session['sequence'] = sequence

    correct_sequence = ['tank_input_valve', 'tank_input_valve', 'tank_input_valve', 'tank_output_valve', 'tank_output_valve']
    if sequence == correct_sequence:
        # --- AJUSTE PRINCIPAL ---
        # Utiliza caminhos absolutos, assumindo que a pasta 'bottlefactory' está na raiz do contentor.
        base_path = "/bottlefactory" 
        log_dir = os.path.join(base_path, "src/attacks/attack-logs")
        log_file = os.path.join(log_dir, "log-ddos.txt")
        script_path = os.path.join(base_path, "src/attacks/ddos.sh")

        # Verifica se o diretório de log existe, se não, cria-o
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Executa o ataque DDoS com os argumentos e caminhos absolutos
        try:
            subprocess.Popen(["bash", script_path, log_dir, log_file])
            session['sequence'] = []  # Reseta a sequência
            return jsonify({"status": "Ataque DDoS iniciado!", "flag": "FLAG{G3r4d0}"})
        except FileNotFoundError:
            # Esta mensagem de erro ajuda a depurar se o caminho do script estiver errado
            return jsonify({"status": f"Erro: Script não encontrado em {script_path}", "error": "FileNotFound"}), 500
        except Exception as e:
            return jsonify({"status": f"Erro ao executar o script: {str(e)}", "error": "ExecutionFailed"}), 500

    elif len(sequence) >= len(correct_sequence):
        session['sequence'] = []  # Reseta se a sequência estiver errada
        return jsonify({"status": "Sequência incorreta. A reiniciar."})
    else:
        return jsonify({"status": "Botão pressionado."})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
