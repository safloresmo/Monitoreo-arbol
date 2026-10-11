-- Base de datos del monitoreo. Los nombres de las tablas y de las columnas
-- son los que usaba el proyecto original.
CREATE DATABASE IF NOT EXISTS limon CHARACTER SET utf8mb4;
USE limon;

-- Aire: temperatura en °C y humedad relativa en %.
CREATE TABLE IF NOT EXISTS Temperatura (
    time DATETIME NOT NULL,
    HumedadA FLOAT NOT NULL,
    Temperatura FLOAT NOT NULL,
    INDEX (time)
);

-- Riego: litros que pasaron desde la lectura anterior.
CREATE TABLE IF NOT EXISTS Flujo (
    time DATETIME NOT NULL,
    Litros FLOAT NOT NULL,
    INDEX (time)
);

-- Humedad del suelo en %, una tabla por sensor.
CREATE TABLE IF NOT EXISTS Suelo (
    time DATETIME NOT NULL,
    Humedad FLOAT NOT NULL,
    INDEX (time)
);

CREATE TABLE IF NOT EXISTS Suelo2 LIKE Suelo;
CREATE TABLE IF NOT EXISTS Suelo3 LIKE Suelo;
