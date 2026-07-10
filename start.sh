#!/bin/bash
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 could not be found. Please install Python 3.8+"
    exit
fi

if [ ! -d "venv" ]; then
    echo "Creating an isolated Virtual Environment (venv)..."
    python3 -m venv venv
fi

echo "Activating environment..."
source venv/bin/activate

echo "Installing necessary dependencies..."
pip install -r requirements.txt

echo "Starting server..."
echo "-----------------------------------------------------"
echo "Go to http://127.0.0.1:5050/ in your web browser!"
echo "-----------------------------------------------------"
python3 app.py
