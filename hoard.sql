CREATE DATABASE IF NOT EXISTS hoard;

CREATE TABLE IF NOT EXISTS "viewers" (
    username VARCHAR(25) NOT NULL PRIMARY KEY,
    coins INT
);

CREATE TABLE IF NOT EXISTS "commands" (
    trigger TEXT PRIMARY KEY,
    response TEXT
);