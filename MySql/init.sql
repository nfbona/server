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
    last_login DATETIME, 
    password_hash VARCHAR(128) NOT NULL, 
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

CREATE TABLE if not exists schedule (
    email VARCHAR(100), 
    start_time DATETIME, 
    end_time DATETIME, 
    FOREIGN KEY(email) REFERENCES users(email),
    PRIMARY KEY (email,start_time)
    );


INSERT INTO roles (id, date_added, name)
VALUES 
    (1, NOW(), 'administrator'),
    (2, NOW(), 'user')
ON DUPLICATE KEY UPDATE
    id = VALUES(id);


INSERT INTO users (email ,date_added ,last_login, password_hash,  role_id)
    VALUES ('admin@admin.admin', NOW(),NOW() ,'sha256$39uHUtGQLHwB6IRS$75457a9fe742bc2852fce204f1b8fba7a91a678a05efe2a9e723cf52f9a99d30',1)
ON DUPLICATE KEY UPDATE
    email = VALUES(email);

INSERT INTO relays (id,state,date_modified,name) 
VALUES 
    ( 1, 0, NOW(), 'Relay1'),
    ( 2, 0, NOW(), 'Relay2'),
    ( 3, 0, NOW(), 'Relay3'),
    ( 4, 0, NOW(), 'Relay4'),
    ( 5, 0, NOW(), 'Relay5'),
    ( 6, 0, NOW(), 'Relay6'),
    ( 7, 0, NOW(), 'Relay7'),
    ( 8, 0, NOW(), 'Relay8')
ON DUPLICATE KEY UPDATE
    id = VALUES(id);
    

