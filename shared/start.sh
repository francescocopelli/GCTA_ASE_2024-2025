#!/usr/bin/sh
pip install -r "/app/shared/requirements.txt"
flask run --host=0.0.0.0 --port=5000 --cert=/run/secrets/cert --key=/run/secrets/key