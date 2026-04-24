#!/bin/bash

echo "--- STARTING: npm run train ---"
npm run train

echo "--- STARTING: routes.py (Flask) ---"
export FLASK_APP=routes.py
python3 -m flask run --host=0.0.0.0 --port=7860

echo "--- STEP 3: Starting Frontend ---"
npm run app