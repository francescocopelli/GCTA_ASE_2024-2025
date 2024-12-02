FROM ubuntu/mysql:latest

ENV MYSQL_ROOT_PASSWORD=/run/secrets/db_password
ENV MYSQL_DATABASE=transactions


COPY ./backup/transactions_db.sql /docker-entrypoint-initdb.d/transactions_db.sql

COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

COPY ./backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
