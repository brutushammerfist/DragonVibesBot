const Database = require('./Database.js');
const TwitchAPI = require('./TwitchAPI.js');
const WS = require('./WS.js');

class Bot {
    constructor() {
        this.commands = new Map();
        this.giveawayActive = false;
        this.poolActive = false;
        this.giveawayPool = [];
        this.poolPool = [];
    }

    handleCommand(commandName, username) {
        switch (commandName) {
            case "test":
                return "I'm STILL being lobotomized!";
            case "uptime":
                return TwitchAPI.uptime();
            case "coins":
                return username + " has accumulated " + Database.getCoins(username) + "coins in their hoard!";
            case "enter":
                return this.enterGiveaway(username);
            case "pool":
                return this.enterPool(username);
            default:
                return "Invalid Command!";
        }
    }

    /****
     * Giveaway Functions
     */

    enterGiveaway(username) {
        if (this.giveawayActive) {
            if (!this.giveawayPool.includes(username)) {
                this.giveawayPool.push(username);

                WS.broadcastMessage(JSON.stringify({ giveawayEntries: this.giveawayPool }));

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

                WS.broadcastMessage(JSON.stringify({ poolEntries: this.poolPool }));

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
        WS.broadcastMessage("clear-giveaway");
    }

    removeGiveawayEntry(username) {
        this.giveawayPool.splice(this.giveawayPool.indexOf(username), 1);
        WS.broadcastMessage(JSON.stringify({ giveawayEntries: this.giveawayPool }));
    }

    pullPool() {
        var winner = this.poolPool[Math.floor(Math.random() * this.poolPool.length)];
        this.removePoolEntry(winner);
        return winner;
    }

    clearPool() {
        this.poolPool = [];
        WS.broadcastMessage("clear-pool");
    }

    removePoolEntry() {
        this.poolPool.splice(this.poolPool.indexOf(username), 1);
        WS.broadcastMessage(JSON.stringify({ poolEntries: this.poolPool }));
    }
}

module.exports = new Bot();