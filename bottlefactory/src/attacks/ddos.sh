#!/bin/bash
log_dir=$1
log_file=$2

# --- PARTE 1: Gerar o Log com a Flag (a parte que já funciona) ---
mkdir -p "$log_dir"
current_time=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$current_time] FLAG{C7F_0T_5UC3SS}" >> "$log_file"
chmod 777 "$log_file"

# --- PARTE 2: Iniciar o Ataque DDoS ---
# Obtém o diretório do próprio script para poder navegar para a pasta 'src'
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR/../"

# Executa os agentes DDoS em background
# O Agente 'J' é executado em primeiro plano para manter o script ativo
# enquanto os outros rodam.
echo "Iniciando agentes DDoS..."
python3 DDosAgent.py 'A' &
python3 DDosAgent.py 'B' &
python3 DDosAgent.py 'C' &
python3 DDosAgent.py 'D' &
python3 DDosAgent.py 'J'

echo "Ataque DDoS finalizado."
