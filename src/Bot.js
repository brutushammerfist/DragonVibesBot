const Database = require('./Database.js');
const TwitchAPI = require('./TwitchAPI.js');
const WS = require('./WS.js');

class Bot {
    constructor() { }

    handleCommand(commandName, username) {
        switch (commandName) {
            case "test":
                return "I'm STILL being lobotomized!";
            case "uptime":
                return TwitchAPI.uptime();
            case "coins":
                return username + " has accumulated " + Database.getCoins(username) + "coins in their hoard!";
            case "openga":
                return Giveaway.openGiveaway();
            case "openpool":
                return Giveaway.openPool();
            case "enter":
                //return Giveaway.enterGiveaway(username);
                var response = Giveaway.enterGiveaway(username);
                if (response.includes("successfully")) {
                    WS.broadcastMessage(JSON.stringify({ giveawayEntries: Giveaway.giveawayPool }));
                }
                return response;
            case "pool":
                //return Giveaway.enterPool(username);
                var response = Giveaway.enterPool(username);
                if (response.includes("successfully")) {
                    WS.broadcastMessage(JSON.stringify({ poolEntries: Giveaway.poolPool }));
                }
                return response;
            default:
                return "Invalid Command!";
        }
    }
}

module.exports = new Bot();