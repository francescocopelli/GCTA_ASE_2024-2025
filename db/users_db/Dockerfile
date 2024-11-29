FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=123456
ENV MYSQL_DATABASE=users
ENV MYSQL_PASSWORD=root


COPY ./users.sql /docker-entrypoint-initdb.d/

EXPOSE 3306
