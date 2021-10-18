const Bot = require('./Bot.js');
const tmi = require('tmi.js');

class Twitch {
    constructor(oauth_token) {

        this.client = new tmi.Client({
            identity: {
                username: 'DragonVibesBot',
                password: oauth_token
            },
            channels: [
                'DracoAsier'
            ]
        });

        this.client.on('message', (channel, tags, message, self) => {
            if (self || !message.startsWith("!")) return;

            this.client.say(channel, Bot.handleCommand(message.split(' ')[0].substring(1), message.author));
        });

        this.client.on('connected', (addr, port) => {
            console.log(`* Connected to ${addr}:${port}`);
        });
    }

    start() {
        this.client.connect().catch(console.error);
    }
}

module.exports = Twitch;