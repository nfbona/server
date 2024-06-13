FROM biarms/mysql:5.7.30 as base
COPY ./my.cnf /etc/mysql/conf.d/

COPY ./init.sql /docker-entrypoint-initdb.d

WORKDIR /etc/mysql/