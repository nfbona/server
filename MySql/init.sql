CREATE DATABASE IF NOT EXISTS mysql;

USE mysql;

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
    password_hash VARCHAR(256) NOT NULL, 
    role_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_session_active BOOLEAN DEFAULT FALSE,
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
    id VARCHAR(256) NOT NULL, 
    FOREIGN KEY(user_email) REFERENCES users(email),
    PRIMARY KEY(id)
    );

CREATE TABLE if not exists signup_request ( 
    date DATETIME, 
    id int AUTO_INCREMENT, 
    user_email VARCHAR(100),
    password VARCHAR(256) NOT NULL, 
    PRIMARY KEY(id)
    );

CREATE TABLE if not exists log_users (
    user_email VARCHAR(100), 
    action VARCHAR(100), 
    id INT AUTO_INCREMENT,  
    datetime DATETIME, 
    PRIMARY KEY(id)
    );

CREATE TABLE if not exists log_relays (
    user_email VARCHAR(100), 
    action VARCHAR(100), 
    id INT AUTO_INCREMENT,  
    relay_id INT ,  
    datetime DATETIME,  
    PRIMARY KEY(id)
    );


CREATE TABLE if not exists log_schedules (
    user_email VARCHAR(100), 
    action VARCHAR(100), 
    id INT AUTO_INCREMENT,  
    datetime DATETIME, 
    schedule_id VARCHAR(256) NOT NULL, 
    start_time DATETIME, 
    end_time DATETIME, 
    PRIMARY KEY(id)
    );

CREATE TABLE if not exists log_signup_request (
    user_accepter VARCHAR(100), 
    user_email VARCHAR(100), 
    action VARCHAR(100), 
    id INT AUTO_INCREMENT,  
    datetime DATETIME, 
    PRIMARY KEY(id)
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


-- CLEAN UP --
-- Delete all records older than 30 days
DELETE FROM signup_request WHERE date < NOW() - INTERVAL 30 DAY;

DELETE FROM users WHERE date_added < NOW() - INTERVAL 30 DAY AND is_active = false;

DELETE FROM schedule WHERE end_time < NOW() - INTERVAL 30 DAY;

-- Delete all logs older than 3 months
DELETE FROM log_signup_request WHERE datetime < NOW() - INTERVAL 3 MONTH;

DELETE FROM log_schedules WHERE datetime < NOW() - INTERVAL 3 MONTH;

DELETE FROM log_relays WHERE datetime < NOW() - INTERVAL 3 MONTH;

DELETE FROM log_users WHERE datetime < NOW() - INTERVAL 3 MONTH;
