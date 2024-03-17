CREATE DATABASE IF NOT EXISTS mysql;

USE mysql;

CREATE USER '${DATABASE_USERNAME}'@'${FLASK_APP_IP}' IDENTIFIED BY '${DATABASE_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${DATABASE_USERNAME}'@'${FLASK_APP_IP}';
FLUSH PRIVILEGES;

CREATE TABLE if not exists roles (
    id INT AUTO_INCREMENT,
    date_added DATETIME, 
    name VARCHAR(100) NOT NULL UNIQUE,
    PRIMARY KEY (id)
    );

CREATE TABLE if not exists users (
    email VARCHAR(100), 
    color VARCHAR(20),
    date_added DATETIME, 
    last_login DATETIME, 
    password_hash VARCHAR(128) NOT NULL, 
    role_id INT NOT NULL,
    session_id VARCHAR(254),
    PRIMARY KEY(email),
    FOREIGN KEY(role_id) REFERENCES roles(id)

    );

CREATE TABLE if not exists relays (
    id INT AUTO_INCREMENT, 
    state INT, 
    date_modified DATETIME, 
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY(id)
    );

CREATE TABLE if not exists schedule (
    user_email VARCHAR(100), 
    start_time DATETIME, 
    end_time DATETIME, 
    FOREIGN KEY(user_email) REFERENCES users(email),
    PRIMARY KEY(user_email,start_time)
    );

CREATE TABLE if not exists sessions (
    user_email VARCHAR(100), 
    date_created DATETIME NOT NULL, 
    date_expiry DATETIME NOT NULL, 
    FOREIGN KEY(user_email) REFERENCES users(email),
    PRIMARY KEY(user_email)
    );


INSERT INTO roles (id, date_added, name)
VALUES 
    (1, NOW(), 'administrator'),
    (2, NOW(), 'user')
ON DUPLICATE KEY UPDATE
    id = VALUES(id);


INSERT INTO users (email ,date_added ,last_login, password_hash,  role_id,color)
    VALUES ('admin@admin.admin', NOW(),NOW() ,'sha256$39uHUtGQLHwB6IRS$75457a9fe742bc2852fce204f1b8fba7a91a678a05efe2a9e723cf52f9a99d30',1,'176,176,0')
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

