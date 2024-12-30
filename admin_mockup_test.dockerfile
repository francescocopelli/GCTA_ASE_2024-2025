FROM python:3.14.0a3-slim

RUN apt-get update && apt-get install -y libssl-dev libsqlite3-dev
COPY ./certificates/users_cert.pem /run/secrets/users_cert
COPY ./certificates/users_key.pem /run/secrets/users_key
COPY ./poetry.txt /run/secrets/novel

WORKDIR /app
COPY ./services/admin/requirements.txt /app/requirements.txt
RUN pip install -r ./requirements.txt
COPY ./services/admin /app
COPY ./mockup_test/admin /app
COPY ./shared /app

ENV MOCKUP="1"

# RUN apt-get update && apt-get install -y gcc && apt install libsqlite3-dev -y

# RUN pip install -r ./requirements.txt

EXPOSE 5000
# CMD ["flask","run", "--port=5000", "--host=0.0.0.0"]
ENV FLASK_APP=app_test.py
CMD ["flask","run", "--port=5000", "--host=0.0.0.0", "--cert=/run/secrets/users_cert", "--key=/run/secrets/users_key"]