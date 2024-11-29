FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=123456
ENV MYSQL_DATABASE=gacha
ENV MYSQL_PASSWORD=root


COPY ./gacha.sql /docker-entrypoint-initdb.d/

EXPOSE 3306
