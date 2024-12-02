#!/bin/bash

#call the original entrypoint script
/usr/local/bin/docker-entrypoint.sh mysqld &
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

