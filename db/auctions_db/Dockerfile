FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=123456
ENV MYSQL_DATABASE=auctions
ENV MYSQL_PASSWORD=root


COPY ./auction_db.sql /docker-entrypoint-initdb.d/

EXPOSE 3306
