#!/bin/bash
export DATABASE_USERNAME=${DATABASE_USERNAME}
export FLASK_APP_IP=${FLASK_APP_IP}
export DATABASE_PASSWORD=${DATABASE_PASSWORD}
envsubst < /docker-entrypoint-initdb.d/init.sql.template > /docker-entrypoint-initdb.d/init.sql
exec docker-entrypoint.sh mysqld