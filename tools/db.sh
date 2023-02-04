#!/bin/bash
set -e
echo $1
psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "$POSTGRES_DB" <<-EOSQL
    DROP DATABASE IF EXISTS $1;
    DROP USER IF EXISTS $1;
    CREATE ROLE $1 WITH LOGIN SUPERUSER PASSWORD '$1';
    CREATE DATABASE $1;
    GRANT ALL PRIVILEGES ON DATABASE $1 TO $1;
    \c $1

    CREATE TABLE users (
        id SERIAL,
        created_on TIMESTAMP,
        updated_on TIMESTAMP,
        username VARCHAR(255) UNIQUE NOT NULl,
        password VARCHAR NOT NULL,
        active BOOLEAN,
        email VARCHAR(120),
        slug VARCHAR(120),
        PRIMARY KEY (id)
    );

    CREATE TABLE content (
        path VARCHAR(255) NOT NULL,
        priority INT UNIQUE,
        type VARCHAR(4),
        PRIMARY KEY(path)
    );

EOSQL
