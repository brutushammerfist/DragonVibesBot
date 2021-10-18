//const sqlite3 = require('sqlite3').verbose();
const mysql = require('mysql');
const fs = require('fs');

var secrets = require("../secrets.json");

class Database {
    constructor() {
        /*if (!Database.instance) {
            Database.instance = new Database();
        }*/

        /*this.db = new sqlite3.Database('hoard.db');

        this.db.run("CREATE TABLE IF NOT EXISTS viewers (username TEXT, coins INTEGER)");
        this.db.run("CREATE TABLE IF NOT EXISTS commands (trigger TEXT, response TEXT)");*/

        this.db = mysql.createConnection({
            host: secrets.dbHost,
            user: secrets.dbUser,
            password: secrets.dbPass,
            database: secrets.dbName,
            multipleStatements: true
        });

        //console.log(this.db.state);

        var creationCmds = [
            "CREATE DATABASE IF NOT EXISTS hoard",
            "CREATE TABLE IF NOT EXISTS `viewers` (username VARCHAR(25) NOT NULL PRIMARY KEY, coins INT)",
            "CREATE TABLE IF NOT EXISTS `commands` (trigger TEXT PRIMARY KEY, response TEXT)"
        ];

        this.db.connect(function (err) {
            if (err) throw err;
            console.log("Database Connected!");
        });

        for (var cmd in creationCmds) {
            this.db.query(creationCmds[cmd], function (err, result) {
                if (err) throw err;
            });
        }
    }

    ensureConnected() {
        if (this.db.state == "disconnected") {
            /*this.db = mysql.createConnection({
                host: secrets.dbHost,
                user: secrets.dbUser,
                password: secrets.dbPass,
                database: secrets.dbName,
                multipleStatements: true
            });*/
            this.db.connect(function (err) {
                if (err) throw err;
                console.log("Database Reconnected!");
            });
        }
    }

    addCommand(commandName, response) {

    }

    deleteCommand(commandName) {

    }

    distributeCoins(online, usernames) {
        this.ensureConnected();

        if (online) {

        } else {

        }
    }

    getCoins(username) {
        this.ensureConnected();

        let sql = `SELECT coins FROM viewers WHERE username = ${username}`;

        this.db.query(sql, function (err, result, fields) {
            if (err) throw err;
            return result;
            //return Number(result);
        });
    }
}

module.exports = new Database();