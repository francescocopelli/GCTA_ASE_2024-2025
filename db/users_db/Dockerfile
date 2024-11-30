FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=123456
ENV MYSQL_DATABASE=users
ENV MYSQL_PASSWORD=root


COPY ./backup/users_db.sql /docker-entrypoint-initdb.d/users_db.sql
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

COPY ./backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
