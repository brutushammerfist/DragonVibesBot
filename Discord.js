require("./Bot.js");

const { Client, Collection, Intents } = require('discord.js');

class Discord {
    constructor(bot) {
        this.client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });

        this.client.once('ready', () => {
            console.log('Discord Ready!');
        });

        this.client.on('message', message => {
            this.handleMessage(message);
        });

        this.bot = bot;
    }

    async handleMessage(message) {
        if (!message.content.startsWith("!")) return;

        message.reply(this.bot.handleCommand(message.content.split(' ')[0].substring(1), message.author.username));
    }

    start(token) {
        this.client.login(token);
    }
}

module.exports = Discord;