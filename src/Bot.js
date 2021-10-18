const Database = require('./Database.js');
const TwitchAPI = require('./TwitchAPI.js');

class Bot {
    constructor() {
        this.commands = new Map();
    }

    handleCommand(commandName, username) {
        switch (commandName) {
            case "test":
                return "I'm STILL being lobotomized!";
            case "uptime":
                return TwitchAPI.uptime();
            case "coins":
                return username + " has accumulated " + Database.getCoins(username) + "coins in their hoard!";
            default:
                return "Invalid Command!";
        }
    }
}

module.exports = new Bot();