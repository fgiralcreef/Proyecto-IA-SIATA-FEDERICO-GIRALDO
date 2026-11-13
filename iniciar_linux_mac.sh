#!/usr/bin/env sh
set -e
python -m pip install -r requirements.txt
python -m streamlit run app.py
