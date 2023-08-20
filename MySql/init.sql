CREATE DATABASE IF NOT EXISTS mysql;

USE mysql;

CREATE TABLE if not exists roles (
    id INT,
    date_added DATETIME, 
    name VARCHAR(100) NOT NULL UNIQUE,
    PRIMARY KEY (id)
    );

CREATE TABLE if not exists users (
    email VARCHAR(100), 
    date_added DATETIME, 
    password_hash VARCHAR(128) NOT NULL, 
    active INT, 
    role_id INT NOT NULL,
    PRIMARY KEY (email),
    FOREIGN KEY(role_id) REFERENCES roles(id)
    );

CREATE TABLE if not exists relays (
    id INT NOT NULL, 
    state INT, 
    date_modified DATETIME, 
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
    );


SHOW TABLES