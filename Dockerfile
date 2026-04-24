FROM python:3.10-slim

# Installazione Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

# Dipendenze
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user package*.json ./
RUN npm install

# Copia tutto
COPY --chown=user . .
RUN chmod +x start.sh

# Porta richiesta da Hugging Face
EXPOSE 7860

CMD ["./start.sh"]