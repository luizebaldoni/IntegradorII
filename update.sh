#!/bin/bash

echo "🔄 Iniciando atualização do projeto Django..."

# Ativar o ambiente virtual
source /home/piec1/venv/bin/activate

# Ir para o diretório do projeto
cd /home/piec1/IntegradorII || { echo "❌ Diretório do projeto não encontrado"; exit 1; }
# Atualizar o código via git
echo "📥 Executando git pull..."
git pull

# Aplicar migrações do Django
echo "🛠️ Rodando migrações..."
python manage.py makemigrations
python manage.py migrate

# Reiniciar o serviço systemd (sem senha, configurado via sudoers)
echo "🔁 Reiniciando serviço django.service..."
sudo /bin/systemctl restart django.service

echo "✅ Projeto atualizado e serviço reiniciado com sucesso!"



