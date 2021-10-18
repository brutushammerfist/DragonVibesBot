//const sqlite3 = require('sqlite3').verbose();
const TwitchAPI = require('./TwitchAPI.js');
const mysql = require('mysql');
const fs = require('fs');

var secrets = require("../secrets.json");

class Database {
    constructor() {
        this.db = mysql.createConnection({
            host: secrets.dbHost,
            user: secrets.dbUser,
            password: secrets.dbPass,
            database: secrets.dbName,
            multipleStatements: true
        });

        var creationCmds = [
            "CREATE DATABASE IF NOT EXISTS hoard",
            "CREATE TABLE IF NOT EXISTS `viewers` (username VARCHAR(25) NOT NULL PRIMARY KEY, coins INT)",
            "CREATE TABLE IF NOT EXISTS `commands` (`trigger` VARCHAR(50) NOT NULL PRIMARY KEY, response TEXT)"
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

    loadCommands() {
        this.ensureConnected()

        var sql = "SELECT * FROM `commands`";

        var cmds = new Map();

        this.db.query(sql, function (err, result, fields) {
            for (var cmd in result) {
                cmds.set(result[cmd].trigger, result[cmd].response);
            }
        });

        return cmds;
    }

    ensureConnected() {
        if (this.db.state == "disconnected") {
            this.db.connect(function (err) {
                if (err) throw err;
                console.log("Database Reconnected!");
            });
        }
    }

    addCommand(commandName, response) {
        var sql = `INSERT INTO \`commands\` (\`trigger\`, response) VALUES (${commandName}, ${response})`;

        this.db.query(sql, function (err, result) {
            if (err) throw err;
        });
    }

    deleteCommand(commandName) {
        var sql = `DELETE FROM \`commands\` WHERE \`trigger\`=${commandName}`;

        this.db.query(sql, function (err, result) {
            if (err) throw err;
        });
    }

    distributeCoins(online, usernames) {
        this.ensureConnected();

        var viewers = TwitchAPI.getViewers();
        var coins = 1;

        if (TwitchAPI.isOnline()) {
            coins = 4;
        }

        var sql = 'INSERT INTO `viewers` (username, coins) VALUES (%s, %d) ON DUPLICATE KEY UPDATE coins = coins + %d';

        for (i in viewers.chatters.vips) {
            this.db.query(util.format(sql, viewers.chatters.vips[i], coins, coins), function (err, result) {
                if (err) throw err;
            });
        }

        for (i in viewers.chatters.moderators) {
            this.db.query(util.format(sql, viewers.chatters.moderators[i], coins, coins), function (err, result) {
                if (err) throw err;
            });
        }

        for (i in viewers.chatters.viewers) {
            this.db.query(util.format(sql, viewers.chatters.viewers[i], coins, coins), function (err, result) {
                if (err) throw err;
            });
        }
    }

    getCoins(username) {
        this.ensureConnected();

        let sql = `SELECT coins FROM viewers WHERE username = ${username}`;

        this.db.query(sql, function (err, result, fields) {
            if (err) throw err;
            return result;
        });
    }
}

module.exports = new Database();