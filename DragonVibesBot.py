from twitchio.ext import commands
from twitchio import *
import os
import json
import requests
import twitter
import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from random import randrange
from discord_webhook import DiscordWebhook
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from webhookHandler import SimpleHTTPRequestHandler
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import threading
import time

secretsFile = open("secrets.json", "r")
secrets = json.load(secretsFile)
secretsFile.close()

twitchIRCToken = secrets['twitchIRCToken']
twitchClientID = secrets['twitchClientID']
twitchUserID = secrets['twitchUserID']

ytAPI = secrets['ytAPI']
ytBaseURL = secrets['ytBaseURL']
ytChannelID = secrets['ytChannelID']

tweetConsumerKey = secrets['tweetConsumerKey']
tweetConsumerSecret = secrets['tweetConsumerSecret']
tweetAccessTokenKey = secrets['tweetAccessTokenKey']
tweetAccessTokenSecret = secrets['tweetAccessTokenSecret']

tweetAPI = twitter.Api(consumer_key=tweetConsumerKey,
    consumer_secret=tweetConsumerSecret,
    access_token_key=tweetAccessTokenKey,
    access_token_secret=tweetAccessTokenSecret
    )
    
locHost = secrets['local_host']
extHost = secrets['external_host']
Port = secrets['port']

clients = []

blacklist = []

if os.stat("blacklist.csv").st_size is not 0:
    with open("blacklist.csv", "r") as blacklistFile:
        words = blacklistFile.read()
    blacklist = words.split(",")

pid = str(os.getpid())
pidfile = "/tmp/dragonvibesbot.pid"

with open(pidfile, 'w') as tmpFile:
    tmpFile.write(pid)

class soundsServer(WebSocket):
    def handleMessage(self):
        global blacklist
        payload = self.data
        if payload.startswith("addblacklist"):
            payload = "," + payload[13:]
            with open("blacklist.csv", 'a') as blacklistFile:
                blacklistFile.write(payload)
        elif payload.startswith("delblacklist"):
            payload = payload[13:]
            payload = payload.split(",")
            if os.stat("blacklist.csv", "r").st_size is not 0:
                with open("blacklist.csv", 'r') as blacklistFile:
                    tempBlacklist = blacklistFile.read().split(",")
            for x in payload:
                print("Removing: " + str(x))
                if x in tempBlacklist:
                    tempBlacklist.remove(x)
            newBlacklist = ""
            for x in tempBlacklist:
                newBlacklist = newBlacklist + x + ","
            newBlacklist = newBlacklist[:-1]
            blacklist.clear()
            blacklist = newBlacklist.split(",")
            print(blacklist)
            with open("blacklist.csv", 'w') as blacklistFile:
                blacklistFile.write(newBlacklist)
        elif payload.startswith("addcommands"):
            payload = payload[12:]
            userCommand = {}
            with open("commands.json", "r") as userCommandFile:
                if os.stat("commands.json").st_size is not 0:
                    userCommand = json.load(userCommandFile)
            tempDict = payload.split(":")
            print("Adding command: " + tempDict[0])
            userCommand[tempDict[0]] = tempDict[1]
            with open("commands.json", "w") as userCommandFile:
                json.dump(userCommand, userCommandFile)
        elif payload.startswith("delcommands"):
            payload = payload[12:]
            userCommand = {}
            with open("commands.json", "r") as userCommandFile:
                if os.stat("commands.json").st_size is not 0:
                    userCommand = json.load(userCommandFile)
            if payload in userCommand:
                userCommand.pop(payload)
                with open("commands.json", "w") as userCommandFile:
                    json.dump(userCommand, userCommandFile)
        else:
            pass
    
    def handleConnected(self):
        global blacklist
        print(self.address, 'connected')
        clients.append(self)
        blacklist.clear()
        with open("blacklist.csv", "r") as blacklistFile:
            words = blacklistFile.read()
        blacklist = words.split(",")
        payload = "blacklist "
        for x in blacklist:
            payload = payload + f'{x},'
        payload = payload[:-1]
        payload = payload + ";commands "
        userCommand = {}
        with open("commands.json", "r") as userCommandFile:
            userCommand = json.load(userCommandFile)
        for x in userCommand:
            payload = payload + x + ":" + userCommand[x] + "\\"
        payload = payload[:-1]
        self.sendMessage(payload)
        
    def handleClose(self):
        print(self.address, 'closed')
        clients.remove(self)
        
    def sendSound(self, soundType):
        for client in clients:
            client.sendMessage(soundType)

class Bot(commands.Bot):
    
    commandSched = AsyncIOScheduler()
    
    coinsCheck = 0
    
    giveawayPool = []
    giveawayPrice = 0
    giveawayActive = False
    
    pool = []
    poolActive = False
    
    modList = ["dracoasier", "brutushammerfist"]
    
    socketServer = SimpleWebSocketServer('0.0.0.0', 8765, soundsServer)
    socketThread = threading.Thread(target=socketServer.serveforever)
    socketThread.start()
    
    reapThread = None
    ghostThread = None
    seaThread = None
    teleporterThread = None
    roarThread = None

    def __init__(self):
        super().__init__(irc_token=twitchIRCToken, client_id=twitchClientID, nick='DragonVibesBot', prefix='!',
                         initial_channels=['DracoAsier'])
        headers = {
            'Client-ID' : f'{twitchClientID}',
            'Content-Type' : 'application/json'
        }
        payload = {
            "hub.mode" : "subscribe",
            "hub.topic" : f'https://api.twitch.tv/helix/streams?user_id={twitchUserID}',
            "hub.callback" : f'http://{extHost}:{Port}',
            "hub.lease_seconds" : "864000"
        }
        subscribe = requests.post('https://api.twitch.tv/helix/webhooks/hub', headers=headers, data=json.dumps(payload))
        print(subscribe.content)
        def httpMain():
            httpd = HTTPServer(('0.0.0.0', 8004), SimpleHTTPRequestHandler)
            httpd.serve_forever()
        webhookThread = threading.Thread(target=httpMain)
        webhookThread.start()
        self.commandSched = AsyncIOScheduler()
        self.commandSched.add_job(self.distributeCoins, 'interval', seconds=900.0)
        print(self.commandSched.get_jobs())
    
    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def event_message(self, message):
        print(message.author.name + " : " + message.content)
        global blacklist
        
        for x in blacklist:
            if x in message.content.split(" "):
                try:
                    ctx = await self.get_context(message)
                except StopIteration:
                    pass
                await ctx.timeout(message.author.name, 1, "Your message contained a blacklisted word!")
        
        userCommand = []
        userCommandFile = open("commands.json", "r")
        if os.stat("commands.json").st_size is not 0:
            userCommand = json.load(userCommandFile)
        userCommandFile.close()
        
        if message.content[0] is "!":
            msg = message.content.split(" ", 1)
            cmd = msg[0][1:]
            print(cmd)
            if cmd in userCommand:
                try:
                    ctx = await self.get_context(message)
                except StopIteration:
                    pass
                await ctx.send(userCommand[cmd])
        
        await self.handle_commands(message)
        
    async def event_userstate(self, user):
        if user.is_mod:
            self.modList.append(user.name)
        
    @commands.command(name='test')
    async def testCommand(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')
        
    @commands.command(name='prime')
    async def primeCommand(self, ctx):
        await ctx.send(f'Do you like free?  Want to be a Dragon? If you like all this and have Amazon Prime, then I got a deal for you. Connect your Twitch to your Amazon Prime to get a free sub token that you can use anywhere on Twitch but you have to resub manually each time. https://twitch.amazon.com/prime')

    @commands.command(name='artist')
    async def artistCommand(self, ctx):
        await ctx.send(f'The various artists seen on my channel Ms. Cannibalistic-tendencies (Main artist of backgrounds and current emotes) Twitter: @CannibalDragon -- Seoxys (Sub Badge artist) Twitter: @SeoxysArt -- Zorryn (3D artist) Twitter: @zorryn_art -- LindseyVi (Notification animator) Twitter: @LindseyVi__')
        
    @commands.command(name='uptime')
    async def uptimeCommand(self, ctx):
        headers = {'Client-ID' : f'{twitchClientID}'}
        r = requests.get(f'https://api.twitch.tv/helix/streams?user_login=DracoAsier', headers=headers)
        r = r.json()
        
        if len(r['data']) == 0:
            await ctx.send(f'Shhh! The dragon is sleeping! Didn\'t anyone ever tell you to let sleeping dragons lie?!')
        else:
            startTime = r['data'][0]['started_at']
            startTime = datetime.datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%SZ')
            timeNow = datetime.datetime.now()
            timeLive = timeNow - startTime
            timeList = str(timeLive).split(':')
            print(f'Hours: {timeList[0]} | Minutes: {timeList[1]} | Seconds: {int(float(timeList[2]))}')
            await ctx.send(f'The Dragon has been awake for {timeList[0]} hours {timeList[1]} minutes {int(float(timeList[2]))} seconds!')
    
    @commands.command(name='youtube')
    async def ytCommand(self, ctx):
        plistName = ctx.content
        plistName = plistName[9:]
        
        plistURL = "https://www.youtube.com/playlist?list="
        
        r = requests.get(f'{ytBaseURL}/search?part=snippet&channelId={ytChannelID}&type=playlist&q={plistName}&key={ytAPI}')
        r = r.json()
        
        plistURL = plistURL + str(r['items'][0]['id']['playlistId'])
        
        await ctx.send(f'Here is the playlist you requested: {plistName} - {plistURL}')
        
    @commands.command(name="tweet")
    async def tweetCommand(self, ctx):
        r = tweetAPI.GetUserTimeline(screen_name="DracoAsier", count=20, include_rts=False)
        r = r[0].AsDict()
        
        tweetLink = r['urls'][0]['expanded_url']
        
        await ctx.send(f'Here is a link to DracoAsier\'s latest tweet: {tweetLink}')
        
    @commands.command(name="addcom")
    async def addCommand(self, ctx):
        if ctx.author.name in self.modList:
            cmd = ctx.content
            cmd = cmd[8:]
            
            params = cmd.split(" ", 1)
            
            userCommand = {}
            userCommandFile = open("commands.json", "r")
            if os.stat("commands.json").st_size is not 0:
                userCommand = json.load(userCommandFile)
            userCommandFile.close()
            
            if params[0] in userCommand:
                await ctx.send(f'This command already exists, please remove and readd it to edit!')
            else:
                userCommand[params[0]] = params[1]
                userCommandFile = open("commands.json", "w")
                json.dump(userCommand, userCommandFile)
                userCommandFile.close()
                await ctx.send(f'Command {params[0]} has been created!')
        else:
            await ctx.send(f'This command is for Moderators only!')
            
    @commands.command(name="delcom")
    async def delCommand(self, ctx):
        if ctx.author.name in self.modList:
            cmd = ctx.content
            cmd = cmd[8:]
            
            userCommand = {}
            userCommandFile = open("commands.json", "r")
            if os.stat("commands.json").st_size is not 0:
                userCommand = json.load(userCommandFile)
            userCommandFile.close()
            
            if cmd in userCommand:
                userCommand.pop(cmd)
                
                userCommandFile = open("commands.json", "w")
                json.dump(userCommand, userCommandFile)
                userCommandFile.close()
                
                await ctx.send(f'The command !{cmd} has been successfully removed!')
            else:
                await ctx.send(f'Command not found! Try again!')
        else:
            await ctx.send(f'This command is for Moderators only!')
    
    async def distributeCoins(self):
        r = requests.get('https://tmi.twitch.tv/group/user/dracoasier/chatters')
        r = r.json()
        
        headers = {'Client-ID' : f'{twitchClientID}'}
        r2 = requests.get(f'https://api.twitch.tv/helix/streams?user_login=DracoAsier', headers=headers)
        r2 = r2.json()
        
        tokenBank = {}
        tokenBankFile = open("tokenBank.json", "r")
        if os.stat("tokenBank.json").st_size is not 0:
            tokenBank = json.load(tokenBankFile)
        tokenBankFile.close()
        
        categories = ['vips', 'moderators', 'staff', 'admins', 'global_mods', 'viewers']
        
        def checkAndDist(tokenBank, category):
            for x in r['chatters'][category]:
                if len(r2['data']) != 0:
                    if x in tokenBank:
                        tokenBank[x] = tokenBank[x] + 1
                    else:
                        tokenBank[x] = 1
                else:
                    if self.coinsCheck == 3:
                        if x in tokenBank:
                            tokenBank[x] = tokenBank[x] + 1
                        else:
                            tokenBank[x] = 1
                        self.coinsCheck = 0
                    else:
                        self.coinsCheck = self.coinsCheck + 1
                        
        for x in categories:
            checkAndDist(tokenBank, x)
            
        tokenBankFile = open("tokenBank.json", "w")
        json.dump(tokenBank, tokenBankFile)
        tokenBankFile.close()
        
    @commands.command(name="coins")
    async def coinsCommand(self, ctx):
        tokenBank = {}
        tokenBankFile = open("tokenBank.json", "r")
        if os.stat("tokenBank.json").st_size is not 0:
            tokenBank = json.load(tokenBankFile)
        tokenBankFile.close()
        
        if ctx.author.name in tokenBank:
            await ctx.send(f'You have hoarded {tokenBank[ctx.author.name]} coins.')
        else:
            await ctx.send(f'You have not begun hoarding coins. Hang out in the stream to do so!')
    
    @commands.command(name="givecoins")
    async def payCommand(self, ctx):
        if ctx.author.name in self.modList:
            tokenBank = {}
            tokenBankFile = open("tokenBank.json", "r")
            if os.stat("tokenBank.json").st_size is not 0:
                tokenBank = json.load(tokenBankFile)
            tokenBankFile.close()
            
            params = ctx.content
            params = params[11:]
            params = params.split(" ")
            
            amount = int(params[0])
            name = params[1]
            
            if name in tokenBank:
                tokenBank[name] = tokenBank[name] + amount
            else:
                tokenBank[name] = amount
                    
            tokenBankFile = open("tokenBank.json", "w")
            json.dump(tokenBank, tokenBankFile)
            tokenBankFile.close()
            
    @commands.command(name="gastart")
    async def giveawayStartCommand(self, ctx):
        if ctx.author.name in self.modList:
            params = ctx.content
            params = params[6:]
            self.giveawayPrice = int(params)
            self.giveawayActive = True
            
            await ctx.send(f'A giveaway has started! The price for entry is {str(self.giveawayPrice)} coins!')
            
    @commands.command(name="gaend")
    async def giveawayEndCommand(self, ctx):
        if ctx.author.name in self.modList:
            self.giveawayPool.clear()
            self.giveawayPrice = 0
            self.giveawayActive = False
            
            await ctx.send(f'The giveaway has concluded!')
            
    @commands.command(name="gaenter")
    async def enterCommand(self, ctx):
        tokenBank = {}
        tokenBankFile = open("tokenBank.json", "r")
        if os.stat("tokenBank.json").st_size is not 0:
            tokenBank = json.load(tokenBankFile)
        tokenBankFile.close()
        
        if ctx.author.name in self.giveawayPool:
            pass
        else:
            if ctx.author.name in tokenBank:
                if tokenBank[ctx.author.name] >= self.giveawayPrice:
                    tokenBank[ctx.author.name] = tokenBank[ctx.author.name] - self.giveawayPrice
                    self.giveawayPool.append(ctx.author.name)
                
            tokenBankFile = open("tokenBank.json", "w")
            json.dump(tokenBank, tokenBankFile)
            tokenBankFile.close()
        
    @commands.command(name="gapull")
    async def giveawayPullCommand(self, ctx):
        if ctx.author.name in self.modList:
            upper = len(self.giveawayPool) - 1
            winner = randrange(0, upper)
            
            await ctx.send(f'The winner is... {self.giveawayPool[winner]}!!')
            
    @commands.command(name="poolstart")
    async def poolStartCommand(self, ctx):
        if ctx.author.name in self.modList:
            self.poolActive = True
            print("Pool party starting!")
            
            await ctx.send(f'A pool has been created! Everyone take a dip!')
            
    @commands.command(name="poolend")
    async def poolEndCommand(self, ctx):
        if ctx.author.name in self.modList:
            self.pool.clear()
            self.poolActive = False
            print("Pool party over!")
            
            await ctx.send(f'The pool has dried up!')
            
    @commands.command(name="enter")
    async def poolEnterCommand(self, ctx):
        if self.poolActive is True:
            if ctx.author.name in self.pool:
                print("Name already in pool!")
            else:
                print(f'Adding {ctx.author.name} to pool!')
                self.pool.append(ctx.author.name)
            
    @commands.command(name="pull")
    async def poolPullCommand(self, ctx):
        if ctx.author.name in self.modList:
            print("Picking winner...")
            upper = len(self.pool) - 1
            winner = randrange(0, upper)
            print(f'Winner is: {self.pool[winner]}')
            
            await ctx.send(f'The winner is... {self.pool[winner]}!!')
    
    @commands.command(name="comschedule")
    async def scheduleCommand(self, ctx):
        if ctx.author.name in self.modList:
            params = ctx.content
            params = params[13:]
            params = params.split(" ")
            
            if params[1] == "stop":
                currentJobs = self.commandSched.get_jobs()
                for x in range(0, len(currentJobs) - 1):
                    print(currentJobs[x].name)
                    if params[0] in currentJobs[x].name:
                        self.commandSched.remove_job(currentJobs[x].id)
            elif params[1] == "start":
                cmds = {
                    'prime' : self.primeCommand._callback,
                    'uptime' : self.uptimeCommand._callback,
                    'artist' : self.artistCommand._callback,
                    'tweet' : self.tweetCommand._callback
                }
                print(cmds[params[0]])
                self.commandSched.add_job(cmds[params[0]], 'interval', [self, ctx], seconds=int(params[2]))
                print("Command scheduled!")
            
            print(self.commandSched.get_jobs())
            
    @commands.command(name="reaper")
    async def reaperCommand(self, ctx):
        self.reapThread = threading.Thread(target=soundsServer.sendSound, args=(self.socketServer.websocketclass, "reaper", ))
        self.reapThread.start()
        
    @commands.command(name="ghost")
    async def ghostCommand(self, ctx):
        self.ghostThread = threading.Thread(target=soundsServer.sendSound, args=(self.socketServer.websocketclass, "ghost", ))
        self.ghostThread.start()
            
    @commands.command(name="sea")
    async def seaCommand(self, ctx):
        self.seaThread = threading.Thread(target=soundsServer.sendSound, args=(self.socketServer.websocketclass, "sea", ))
        self.seaThread.start()
            
    @commands.command(name="teleporter")
    async def teleporterCommand(self, ctx):
        self.teleporterThread = threading.Thread(target=soundsServer.sendSound, args=(self.socketServer.websocketclass, "teleporter", ))
        self.teleporterThread.start()
            
    @commands.command(name="roar")
    async def roarCommand(self, ctx):
        self.roarThread = threading.Thread(target=soundsServer.sendSound, args=(self.socketServer.websocketclass, "roar", ))
        self.roarThread.start()
        
    @commands.command(name="dvcannon")
    async def cannonCommand(self, ctx):
        params = ctx.content
        params = params[10:]
        
        if params is not "":
            await ctx.send(f'Locking onto {params}...Cannon loaded, firing in 10 seconds!!')
            time.sleep(10)
            await ctx.send(f'dracoaDV https://i.imgur.com/IU3fBKw.gif FIRE!!')
        else:
            await ctx.send(f'Cannon loaded, firing in 10 seconds!!')
            time.sleep(10)
            await ctx.send(f'dracoaDV https://i.imgur.com/IU3fBKw.gif FIRE!!')

try:    
    print("Starting bot!")
    bot = Bot()
    bot.run()
except:
    pass
finally:
    os.remove("/tmp/dragonvibesbot.pid")