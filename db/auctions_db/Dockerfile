FROM golang:latest AS builder
RUN go version

FROM mysql:latest
RUN rm -rf /usr/local/go || true

COPY --from=builder /usr/local/go /usr/local/go
ENV PATH=/usr/local/go/bin:$PATH

RUN go version
RUN go install std

ENV MYSQL_ROOT_PASSWORD=123456
ENV MYSQL_DATABASE=auctions


COPY ./backup/auctions_db.sql /docker-entrypoint-initdb.d/auctions_db.sql

COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

COPY ./backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/entrypoint.sh

EXPOSE 3306

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

