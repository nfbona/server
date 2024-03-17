FROM mysql:8.1.0 as base
COPY ./my.cnf /etc/mysql/conf.d/
COPY ./init.sh /etc/mysql/init.sh
RUN chmod +x /etc/mysql/init.sh
WORKDIR /etc/mysql/