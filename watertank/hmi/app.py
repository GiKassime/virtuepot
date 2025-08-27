from flask import Flask, render_template, current_app, request, session
from pymodbus.client.sync import ModbusTcpClient
from datetime import datetime
from flask import jsonify
import secrets
import subprocess


app = Flask(__name__)


secret_key = secrets.token_hex(16)
# example output, secret_key = 000d88cd9d90036ebdd237eb6b0db000
app.config['SECRET_KEY'] = secret_key

# datetime object containing current date and time
def current_time():
    now = datetime.now().isoformat()
    return now

@app.route('/api',methods=['POST','GET'])
def api():
    host = '192.168.0.26'
    port = 502
    client = ModbusTcpClient(host, port)
    client.connect()
    result = client.read_holding_registers(101,10,unit=0)
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

    # Adiciona o clique à sequência
    sequence.append(valve)
    session['sequence'] = sequence

    # Sequência correta: ['tank_input_valve', 'tank_output_valve']
    if sequence == ['tank_input_valve', 'tank_output_valve']:
        # Executa o ataque DDoS
        subprocess.Popen(["bash", "bottlefactory/src/attacks/ddos.sh"])
        session['sequence'] = []  # Reseta a sequência
        return jsonify({"status": "...", "flag": "FLAG{G3r4d0}"})
    elif len(sequence) >= 2:
        session['sequence'] = []  # Reseta se a sequência estiver errada
        return jsonify({"status": "...."})
    else:
        return jsonify({"status": f"Botão pressionado."})

@app.route('/')
def index():
    return (render_template('index.html'))

if __name__ == '__main__':
    
    # port = int(os.environ.get('PORT', 7000))
    app.run()