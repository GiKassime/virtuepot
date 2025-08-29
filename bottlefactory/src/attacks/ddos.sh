#!/bin/bash
log_dir=$1
log_file=$2

# --- AJUSTE PRINCIPAL ---
# Obtém o diretório do próprio script e muda para o diretório /bottlefactory/src
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR/../" # Navega de 'attacks' para 'src'

# Agora que estamos no diretório certo, os caminhos funcionarão.
# Garante que o diretório de log exista (usando o caminho absoluto do argumento).
mkdir -p "$log_dir"
# Cria o ficheiro de log.
echo "" > "$log_file"
# Adiciona a flag no log.
echo "FLAG{C7F_0T_5UC3SS}" >> "$log_file"

# Chama os agentes. O Python agora será executado a partir de /bottlefactory/src/,
# e encontrará os seus próprios módulos e caminhos de log corretamente.
python3 DDosAgent.py 'A' &
python3 DDosAgent.py 'B' &
python3 DDosAgent.py 'C' &
python3 DDosAgent.py 'D' &
python3 DDosAgent.py 'J'

chmod 777 "$log_file"
