---
title: Minister
emoji: ✨
colorFrom: gray
colorTo: green
sdk: docker
app_port: 7860
pinned: true
license: apache-2.0
python_version: 3.10
app_file: routes.py
short_description: AI Model to predict text
---

## AI Character/Text Predictor
Questo spazio esegue un addestramento automatico all'avvio (EMNIST + HASYv2) e serve un'interfaccia via Flask.

**Sequenza di avvio:**
1. `npm run train`: Pre-elaborazione e training del modello.
2. `routes.py`: Esposizione delle API per la predizione.