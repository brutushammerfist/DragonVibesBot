const { createServer } = require('https');
const Database = require('./Database.js');
const TwitchAPI = require('./TwitchAPI.js');
const secrets = require('../secrets.json');
const { readFileSync } = require('fs');
const { WebSocketServer, WebSocket } = require('ws');
//const WS = require('./WS.js');

class Bot {
    constructor() {
        /***
         * Websocket
         */

        this.wsServer = createServer({
            cert: readFileSync(secrets.certPath),
            key: readFileSync(secrets.keyPath)
        });

        this.wss = new WebSocketServer({ server: this.wsServer });
        this.wss.bot = this;

        this.wss.on('connection', function connection(ws) {
            ws.bot = this.bot;

            ws.on('message', function (message) {
                this.bot.handleWSMessage(message);
            });

            ws.send('Connected!');
        });

        this.wss.on('listening', function () {
            console.log("Websocket Server Started");
        });

        this.wsServer.listen(8080);

        /***
         * Commands
         */
        this.commands = new Map();

        /***
         * Giveaway/Pool
         */
        this.giveawayActive = false;
        this.poolActive = false;
        this.giveawayPool = [];
        this.poolPool = [];
    }

    /***
     * Bot Commands
     */

    handleCommand(commandName, username) {
        switch (commandName) {
            case "test":
                return "I'm STILL being lobotomized!";
            case "uptime":
                return TwitchAPI.uptime();
            case "coins":
                return username + " has accumulated " + Database.getCoins(username) + "coins in their hoard!";
            case "openga":
                return this.openGiveaway();
            case "closega":
                return this.clearGiveaway();
            case "openpool":
                return this.openPool();
            case "closepool":
                return this.clearPool();
            case "enter":
                //return Giveaway.enterGiveaway(username);
                var response = this.enterGiveaway(username);
                if (response.includes("successfully")) {
                    this.broadcastWSMessage(JSON.stringify({ giveawayEntries: this.giveawayPool }));
                }
                return response;
            case "pool":
                //return Giveaway.enterPool(username);
                var response = this.enterPool(username);
                if (response.includes("successfully")) {
                    this.broadcastWSMessage(JSON.stringify({ poolEntries: this.poolPool }));
                }
                return response;
            default:
                return "Invalid Command!";
        }
    }

    /***
     * Websocket Commands
     */

    handleWSMessage(message) {
        console.log('received: %s', message);

        switch (message) {
            case "clear-giveaway":
                this.clearGiveaway();
                this.broadcastWSMessage("clear-giveaway");
                break;
            case "clear-pool":
                this.clearPool();
                this.broadcastWSMessage("clear-pool");
                break;
            case "pull-giveaway":
                this.pullGiveaway();
                break;
            case "pull-pool":
                this.pullPool();
                break;
            default:
                try {
                    var data = JSON.parse(message);

                    if (data.removeGiveaway) {
                        this.removeGiveawayEntry(data.removeGiveaway);
                        this.broadcastWSMessage(JSON.stringify({ giveawayEntries: this.giveawayPool }));
                    }

                    if (data.removePool) {
                        this.removePoolEntry(data.removePool);
                        this.broadcastWSMessage(JSON.stringify({ giveawayEntries: this.poolPool }));
                    }
                } catch (err) {
                    console.log(err);
                }
        };
    }

    broadcastWSMessage(message) {
        this.wss.clients.forEach(function each(client) {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });
    }

    /***
     * Giveaway/Pool Commands
     */

    openGiveaway() {
        if (this.giveawayActive) {
            return "Giveaway is already active!";
        }

        this.giveawayActive = true;
        return "Giveaway started!";
    }

    openPool() {
        if (this.poolActive) {
            return "Pool is already open!";
        }

        this.poolActive = true;
        return "Pool opened!";
    }

    enterGiveaway(username) {
        if (this.giveawayActive) {
            if (!this.giveawayPool.includes(username)) {
                this.giveawayPool.push(username);

                return `@${username}, you've successfully been entered into the giveaway.`;
            }

            return `@${username}, you've already entered the giveaway.`;
        }

        return "There is not an active giveaway.";
    }

    enterPool(username) {
        if (this.poolActive) {
            if (!this.poolPool.includes(username)) {
                this.poolPool.push(username);


                return `@${username}, you've successfully been entered into the pool.`;
            }

            return `@${username}, you've already entered the pool.`;
        }

        return "There is not an active pool.";
    }

    pullGiveaway() {
        var winner = this.giveawayPool[Math.floor(Math.random() * this.giveawayPool.length)];
        this.removeGiveawayEntry(winner);
        return winner;
    }

    clearGiveaway() {
        this.giveawayPool = [];
        this.giveawayActive = false;
    }

    removeGiveawayEntry(username) {
        this.giveawayPool.splice(this.giveawayPool.indexOf(username), 1);
    }

    pullPool() {
        var winner = this.poolPool[Math.floor(Math.random() * this.poolPool.length)];
        this.removePoolEntry(winner);
        return winner;
    }

    clearPool() {
        this.poolPool = [];
        this.poolActive = false;
    }

    removePoolEntry(username) {
        this.poolPool.splice(this.poolPool.indexOf(username), 1);
    }
}

module.exports = new Bot();