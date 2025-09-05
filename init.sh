
#!/bin/bash

# Limpeza de redes Docker que podem conflitar com o Virtuepot
echo "Removendo redes Docker conflitantes (icsnet, phynet)..."
for net in icsnet phynet; do
  if docker network inspect "$net" >/dev/null 2>&1; then
    docker network rm "$net"
  fi
done

# Remover bridges customizadas se existirem (br_icsnet, br_phynet)
for br in br_icsnet br_phynet; do
  if ip link show "$br" >/dev/null 2>&1; then
    ip link delete "$br" type bridge || true
  fi
done

cwd=$(pwd)
version=$(lsb_release -rs )

# Wrong version warning
if [ "$version" != "22.04" ] && [ "$version" != "20.04" ] && [ "$version" != "18.04" ];
then
  printf "Warning! This installation script has only been tested on Ubuntu 20.04, 22.04 LTS and 18.04 LTS and will likely not work on your Ubuntu version.\n\n"
fi

#install  docker and docker-compose
echo "Install Docker on your Ubuntu system."
read -p "Do you want to proceed with the installation? (y/n): " choice

if [ "$choice" != "y" ]; then
    echo "Installation aborted."
    exit 1
fi

echo "Updating package index..."
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "Installing dependencies..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

echo "Adding Docker's official GPG key..."

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 

echo "Updating package index again..."
sudo chmod a+r /etc/apt/keyrings/docker.gpg
sudo apt-get update

echo "Installing Docker..."
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose

echo "Docker installation completed!"
#FOr permission denied while trying to connect to the Docker daemon socket
sudo chmod 666 /var/run/docker.sock


sleep 3

# Update apt
sudo apt update
#Disable the firewall
sudo ufw disable 
#set the vm.max_map_count for elasticsearch

sysctl -w vm.max_map_count=262144

# Criação das redes Docker necessárias (idempotente)
echo "Criando redes Docker customizadas..."
docker network inspect icsnet >/dev/null 2>&1 || \
  docker network create \
    --driver=bridge \
    --subnet=192.168.0.0/24 \
    --gateway=192.168.0.1 \
    --opt com.docker.network.bridge.name=br_icsnet \
    icsnet

docker network inspect phynet >/dev/null 2>&1 || \
  docker network create \
    --driver=bridge \
    --subnet=192.168.1.0/24 \
    --gateway=192.168.1.1 \
    --opt com.docker.network.bridge.name=br_phynet \
    phynet


# RUN Bottle Factory 
docker-compose -f bottlefactory/docker-compose.yml up -d

# RUN Water tank Openplc
docker-compose -f watertank/docker-compose.yml up -d


# RUN SCADA LTS
docker-compose -f scada/docker-compose.yml up -d


#Run the zeek
docker-compose -f zeek/docker-compose.yml up -d


#Run the honeyd
docker-compose -f honeyd/docker-compose.yml up -d


#Check the running containers 
docker ps