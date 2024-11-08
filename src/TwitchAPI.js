const { ClientCredentialsAuthProvider } = require('@twurple/auth');
const { ApiClient } = require('@twurple/api');
const bent = require('bent');
const getJSON = bent('json');

const secrets = require('../secrets.json');


class TwitchAPI {
    constructor() {
        this.appAuthProvider = new ClientCredentialsAuthProvider(secrets.clientID, secrets.clientSecret);

        this.api = new ApiClient({ authProvider: this.appAuthProvider });
    }

    isOnline() {
        var stream = this.api.streams.getStreamByUserId(secrets.userID);

        return (stream.type == "live");
    }

    getViewers() {
        return getJSON('https://tmi.twitch.tv/group/user/dracoasier/chatters');
    }

    uptime() {
        if (this.isOnline()) {
            var timeElapsed = Date.now() - stream.startDate();

            return `The Dragon has been live for: ${timeElapsed.getHours()} hours, ${timeElapsed.getMinutes()} minutes, and ${timeElapsed.getSeconds()} seconds`;
        } else {
            return `The Dragon is offline!`;
        }
    }
}

module.exports = new TwitchAPI();