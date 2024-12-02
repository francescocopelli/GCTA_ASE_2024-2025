FROM ubuntu/mysql:latest


ENV MYSQL_DATABASE=gacha


COPY ./backup/gacha_db.sql /docker-entrypoint-initdb.d/gacha_db.sql
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

COPY ./backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

