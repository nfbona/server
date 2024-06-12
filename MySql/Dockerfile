FROM biarms/mysql:5.7.30 as base
COPY ./my.cnf /etc/mysql/conf.d/

ADD init.sql /docker-entrypoint-initdb.d

WORKDIR /etc/mysql/