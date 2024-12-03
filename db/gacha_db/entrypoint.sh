#!/bin/bash

#call the original entrypoint script
MYSQL_ROOT_PASSWORD=$(cat /run/secrets/db_password)
/usr/local/bin/docker-entrypoint.sh mysqld \
  --ssl-ca=/run/secrets/ca.pem \
  --ssl-cert=/run/secrets/server-cert.pem \
  --ssl-key=/run/secrets/server-key.pem \
  --require_secure_transport=ON \
  --port=3306 &
MYSQL_PID=$!

handle_exit() {
  echo "Esecuzione script"
  /usr/local/bin/backup.sh
  echo "Backup completato"

  kill -TERM $MYSQL_PID
  wait $MYSQL_PID
  exit 0
}

trap handle_exit SIGTERM SIGINT

wait $MYSQL_PID

