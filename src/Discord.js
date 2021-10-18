const Bot = require("./Bot.js");

const { Client, Collection, Intents } = require('discord.js');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');

class Discord {
    constructor(bot) {
        this.client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });

        this.client.on('ready', () => {
            console.log('Discord Ready!');
        });

        this.client.on('messageCreate', message => {
            this.handleMessage(message);
        });
    }

    async handleMessage(message) {
        if (!message.content.startsWith("!")) return;

        message.reply(Bot.handleCommand(message.content.split(' ')[0].substring(1), message.author.username));
    }

    start(token) {
        this.client.login(token);
    }
}

module.exports = Discord;