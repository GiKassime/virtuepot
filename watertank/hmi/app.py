from flask import Flask, render_template, request, session, jsonify
from pymodbus.client.sync import ModbusTcpClient
from datetime import datetime
import secrets
import subprocess
import os
import logging

# Adiciona logs para facilitar a depuração no 'docker logs'
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# CORREÇÃO: Usa o nome do serviço Docker para a conexão
PLC_HOST = 'openplc_sim_server'

def current_time():
    return datetime.now().isoformat()

@app.route('/api', methods=['POST', 'GET'])
def api():
    try:
        client = ModbusTcpClient(PLC_HOST, port=502, timeout=3)
        if not client.connect():
            logging.error(f"Falha ao conectar ao PLC em {PLC_HOST}")
            return jsonify({"error": f"Não foi possível conectar ao PLC"}), 500

        result = client.read_holding_registers(101, 10, unit=0)
        client.close()

        if result.isError():
            logging.error("Erro na leitura Modbus")
            return jsonify({"error": "Erro ao ler registradores Modbus"}), 500

        return jsonify({
            "datetime": current_time(),
            "data": result.registers
        })
    except Exception as e:
        logging.error(f"Exceção na API: {e}")
        return jsonify({"error": "Erro interno do servidor ao contatar o PLC"}), 500

@app.route('/toggle_valve', methods=['POST'])
def toggle_valve():
    valve = request.form.get('valve')
    if 'sequence' not in session:
        session['sequence'] = []
    
    sequence = session.get('sequence', [])
    sequence.append(valve)
    session['sequence'] = sequence

    correct_sequence = [
        'tank_input_valve', 'tank_input_valve', 'tank_input_valve',
        'tank_output_valve', 'tank_output_valve'
    ]
    
    # Lógica que verifica a sequência a cada clique
    if not correct_sequence[:len(sequence)] == sequence:
        session.pop('sequence', None) # Limpa a sessão
        return jsonify({"status": "Sequência incorreta. Reiniciando."})

    if sequence == correct_sequence:
        log_dir = "/attack-logs"
        log_file = os.path.join(log_dir, "log-ddos.log")
        script_path = "/bottlefactory/src/attacks/ddos.sh" # Caminho absoluto dentro do contêiner

        try:
            os.makedirs(log_dir, exist_ok=True)
            # Usando subprocess.run para melhor controle e feedback
            subprocess.run(
                ["bash", script_path, log_dir, log_file], 
                check=True, capture_output=True, text=True
            )
            session.pop('sequence', None)
            return jsonify({"status": "Ataque DDoS iniciado!", "flag": "FLAG{G3r4d0}"})
        except FileNotFoundError:
            logging.error(f"Script de ataque não encontrado em: {script_path}")
            return jsonify({"status": f"Erro: Script não encontrado."}), 500
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao executar script: {e.stderr}")
            return jsonify({"status": f"Erro ao executar o script."}), 500
        except Exception as e:
            logging.error(f"Erro inesperado no toggle_valve: {e}")
            return jsonify({"status": f"Erro inesperado."}), 500
    else:
        return jsonify({"status": "Botão pressionado."})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
