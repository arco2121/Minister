#!/bin/bash

echo "--- STARTING: npm run train ---"
npm run train

echo "--- STARTING: routes.py (Flask) ---"
export FLASK_APP=routes.py
npm run routes &

echo "--- STEP 3: Starting Frontend ---"
npm run app
