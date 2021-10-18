const Bot = require('./Bot.js');

class WSMsgHandler {
    constructor() { }

    handleMessage(message) {
        console.log('received: %s', message);

        switch (message) {
            case "clear-giveaway":
                Bot.clearGiveaway();
                break;
            case "clear-pool":
                Bot.clearPool();
                break;
            case "pull-giveaway":
                Bot.pullGiveaway();
                break;
            case "pull-pool":
                Bot.pullPool();
                break;
            default:
                var data = JSON.parse(message);

                console.log(data);

                if (data.removeGiveaway) {
                    Bot.removeGiveawayEntry(data.removeGiveaway);
                }

                if (data.removePool) {
                    Bot.removePoolEntry(data.removePool);
                }
        };
    }
}

module.exports = WSMsgHandler;