const Database = require('./Database.js');
const TwitchAPI = require('./TwitchAPI.js');
const WS = require('./WS.js');

class Bot {
    constructor() {
        this.commands = new Map();
        this.giveawayPool = [];
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

        return "There is not an active giveaway";
    }

    pullGiveaway() {
        var winner = this.giveawayPool[Math.floor(Math.random() * this.giveawayPool.length)];
        this.removeUsername(winner);
        return winner;
    }

    clearGiveaway() {
        this.giveawayPool = [];
    }

    removeUsername(username) {
        this.giveawayPool.splice(this.giveawayPool.indexOf(username), 1);
    }
}

module.exports = new Bot();