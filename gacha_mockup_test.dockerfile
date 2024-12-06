FROM python:3.12-slim

RUN apt-get update && apt-get install -y libssl-dev libsqlite3-dev
COPY ./certificates/gacha_cert.pem /run/secrets/gacha_cert
COPY ./certificates/gacha_key.pem /run/secrets/gacha_key
COPY ./poetry.txt /run/secrets/novel

WORKDIR /app
COPY ./services/gacha/requirements.txt /app/requirements.txt
RUN pip install -r ./requirements.txt
COPY ./mockup_test/gacha /app
COPY ./services/gacha /app
COPY ./shared /app

ENV MOCKUP="1"

# RUN apt-get update && apt-get install -y gcc && apt install libsqlite3-dev -y

# RUN pip install -r ./requirements.txt

EXPOSE 5000
# CMD ["flask","run", "--port=5000", "--host=0.0.0.0"]
ENV FLASK_APP=app_test.py
CMD ["flask","run", "--port=5000", "--host=0.0.0.0", "--cert=/run/secrets/gacha_cert", "--key=/run/secrets/gacha_key"]