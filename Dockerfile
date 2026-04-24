# Usa un'immagine base con Python (versione 3.10 o 3.11 è consigliata per PyTorch)
FROM python:3.10-slim

# Installiamo Node.js e le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file delle dipendenze per sfruttare il caching dei layer di Docker
COPY package*.json ./
COPY requirements.txt ./

# Installa le dipendenze Node e Python
RUN npm install
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice nel container
COPY . .

# Rendiamo eseguibile lo script di avvio (lo creiamo nel prossimo passaggio)
RUN chmod +x start.sh

# Esponi la porta del server Flask (pyPort 3000 come da tuo JS)
EXPOSE 3000
EXPOSE 7860

# Avvia lo script che gestisce la sequenza: train -> app
CMD ["./start.sh"]