#!/usr/bin/env node

const Bot = require("./Bot.js");
const Twitch = require("./Twitch.js");
const Discord = require("./Discord.js");
//const Database = require("./Database.js");

var secrets = require("./secrets.json");

//var database = new Database();
//var bot = new Bot(database);
var bot = new Bot();
var twitch = new Twitch(secrets.oauth, bot);
var discord = new Discord(bot);

//twitch.start();
discord.start(secrets.discToken);