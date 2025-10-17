#!/bin/bash
# Cria o ambiente virtual (se não existir)
python3 -m venv venv

# Ativa o ambiente virtual
source venv/bin/activate

# Instala dependências
pip install --upgrade pip
pip install -r requirements.txt

# Executa o bot
python bot-cat.py
