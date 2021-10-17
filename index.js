#!/usr/bin/env node

const Bot = require("./src/Bot.js");
const Twitch = require("./src/Twitch.js");
const Discord = require("./src/Discord.js");
const WS = require("./src/WS.js");
//const Database = require("./Database.js");

var secrets = require("./secrets.json");

//var database = new Database();
//var bot = new Bot(database);
var bot = new Bot();
var twitch = new Twitch(secrets.oauth, bot);
var discord = new Discord(bot);

twitch.start();
discord.start(secrets.discToken);