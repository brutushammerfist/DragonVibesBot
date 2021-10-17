require('./Bot.js');

const tmi = require('tmi.js');

class Twitch {
    constructor(oauth_token, bot) {
        // Configuration Options
        /*this.options = {
            identity: {
                username: 'DragonVibesBot',
                password: oauth_token
            },
            channels: [
                'DracoAsier'
            ]
        };*/

        this.bot = bot;

        //this.client = new tmi.Client(this.options);

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

            this.client.say(channel, this.bot.handleCommand(message.split(' ')[0].substring(1), message.author));
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