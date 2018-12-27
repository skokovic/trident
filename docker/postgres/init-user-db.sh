#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER trident WITH PASSWORD 'password' CREATEDB;
    CREATE DATABASE trident_dev;
    GRANT ALL PRIVILEGES ON DATABASE trident_dev TO trident;
EOSQL
