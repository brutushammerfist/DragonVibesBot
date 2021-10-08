const Database = require('./Database.js');

class Bot {
    constructor() {
        this.commands = new Map();
    }

    handleCommand(commandName, username) {
        switch (commandName) {
            case "test":
                return "I'm STILL being lobotomized!";
            case "uptime":
                break;
            case "coins":
                //return username + " has accumulated " + this.db.getCoins(username) + "coins in their hoard!";
                return username + " has accumulated " + Database.instance.getCoins(username) + "coins in their hoard!";
            default:
                return "";
        }
    }
}

module.exports = Bot;