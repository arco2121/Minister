#!/bin/bash

echo "--- 1. Inizio Addestramento (npm run train) ---"
# Questo comando deve generare il file 'modellino.pth' e 'class_map.json'
npm run train

if [ $? -eq 0 ]; then
    echo "--- 2. Addestramento completato con successo ---"
    echo "--- 3. Avvio Server Flask (routes.py) ---"
    # Avviamo il server. Usiamo python routes.py se hai il blocco app.run()
    # oppure flask run se configurato correttamente.
    python routes.py
else
    echo "Errore durante l'addestramento. Il server non verrà avviato."
    exit 1
fi