FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências de sistema (gcc e sqlite3 são necessários para o tgcrypto/sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas o arquivo de requisitos primeiro para usar cache do Docker
COPY requirements.txt .

# Instalar pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY main.py .

# Criar pasta para o banco de dados e sessão (embora o script já crie, é boa prática)
RUN mkdir -p data

# Variável de ambiente padrão para evitar output buffering do Python
ENV PYTHONUNBUFFERED=1

# Executa o bot
CMD ["python", "main.py"]
