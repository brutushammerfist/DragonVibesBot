from twitchio.ext import commands
from twitchio import WebhookMode
from twitchio import StreamChanged
import os
import json
import requests
import twitter
import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from random import randrange
from discord_webhook import DiscordWebhook

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
 
modList = ["dracoasier"]
blackList = []

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token=twitchIRCToken, client_id=twitchClientID, nick='DragonVibesBot', prefix='!',
                         initial_channels=['DracoAsier'])
        headers = {
            'Client-ID' : f'{twitchClientID}',
            'Content-Type' : 'application/json'
        }
        payload = {
            "hub.topic" : f'https://api.twitch.tv/helix/streams?user_id=59881217',#{twitchUserID}',
            "hub.callback" : f'{extHost}:{Port}/webhookHandler.php',
            "hub.lease_seconds" : "864000"
        }
        subscribe = requests.post('https://api.twitch.tv/helix/webhooks/hub', headers, payload)
        sched = AsyncIOScheduler()
        sched.start()
        job = sched.add_job(self.distributeTokens, 'interval', seconds=300.0)

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')

    async def event_message(self, message):
        print(message.author.name + " : " + message.content)
        
        for x in blackList:
            if x in message.content:
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
            modList.append(user.name)
            
    # NEED TO COMPLETE       
    #        
    #async def event_webhook(self, data):
        

    # Commands use a decorator...
    @commands.command(name='test')
    async def testCommand(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')
        
    @commands.command(name='prime')
    async def primeCommand(self, ctx):
        await ctx.send(f'Do you like free?  Want to be a Dragon? If you like all this and have Amazon Prime, then I got a deal for you. Connect your Twitch to your Amazon Prime to get a free sub token that you can use anywhere on Twitch but you have to resub manually each time. https://twitch.amazon.com/prime')

    @commands.command(name='artist')
    async def artistCommand(self, ctx):
        await ctx.send(f'The various artists seen on my channel Ms. Cannibalistic-tendencies (Main artist of backgrounds and current emotes) Twitter: @CannibalDragon -- Seoxys (Sub Badge artist) Twitter: @SeoxysArt -- Zorryn (3D artist) Twitter: @zorryn_art -- LindseyVi (Notification animator) Twitter: @LindseyVi__')
    
    @commands.command(name='echo')
    async def echoCommand(self, ctx):
        msg = ctx.content
        msg = msg[6:]
        
        await ctx.send(msg)
        
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
        if ctx.author.name in modList:
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
        if ctx.author.name in modList:
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
    
    async def distributeTokens(self):
        r = requests.get('https://tmi.twitch.tv/group/user/dracoasier/chatters')
        r = r.json()
        print(r)
        
        headers = {'Client-ID' : f'{twitchClientID}'}
        r2 = requests.get(f'https://api.twitch.tv/helix/streams?user_login=DracoAsier', headers=headers)
        r2 = r2.json()
        print(r2)
        
        tokenBank = {}
        tokenBankFile = open("tokenBank.json", "r")
        if os.stat("tokenBank.json").st_size is not 0:
            tokenBank = json.load(tokenBankFile)
        tokenBankFile.close()
        
        for x in r['chatters']['vips']:
            if len(r2['data']) == 0:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 300
                else:
                    tokenBank[x] = 300
            else:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 150
                else:
                    tokenBank[x] = 150
                
        for x in r['chatters']['moderators']:
            if len(r2['data']) == 0:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 300
                else:
                    tokenBank[x] = 300
            else:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 150
                else:
                    tokenBank[x] = 150
                
        for x in r['chatters']['staff']:
            if len(r2['data']) == 0:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 300
                else:
                    tokenBank[x] = 300
            else:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 150
                else:
                    tokenBank[x] = 150
        
        for x in r['chatters']['admins']:
            if len(r2['data']) == 0:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 300
                else:
                    tokenBank[x] = 300
            else:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 150
                else:
                    tokenBank[x] = 150
                
        for x in r['chatters']['global_mods']:
            if len(r2['data']) == 0:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 300
                else:
                    tokenBank[x] = 300
            else:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 150
                else:
                    tokenBank[x] = 150
                
        for x in r['chatters']['viewers']:
            if len(r2['data']) == 0:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 300
                else:
                    tokenBank[x] = 300
            else:
                if x in tokenBank:
                    tokenBank[x] = tokenBank[x] + 150
                else:
                    tokenBank[x] = 150
                
        tokenBankFile = open("tokenBank.json", "w")
        json.dump(tokenBank, tokenBankFile)
        tokenBankFile.close()
        
    @commands.command(name="tokens")
    async def tokensCommand(self, ctx):
        
        tokenBank = {}
        tokenBankFile = open("tokenBank.json", "r")
        if os.stat("tokenBank.json").st_size is not 0:
            tokenBank = json.load(tokenBankFile)
        tokenBankFile.close()
        
        if ctx.author.name in tokenBank:
            await ctx.send(f'You have hoarded {tokenBank[ctx.author.name]} coins.')
        else:
            await ctx.send(f'You have not begun hoarding coins. Hang out in the stream to do so!')
    
    @commands.command(name="raid")
    async def raidCommand(self, ctx):
        bet = ctx.content
        bet = bet[6:]
        bet = int(bet)
        
        tokenBank = {}
        tokenBankFile = open("tokenBank.json", "r")
        if os.stat("tokenBank.json").st_size is not 0:
            tokenBank = json.load(tokenBankFile)
        tokenBankFile.close()
        
        tokenBank[ctx.author.name] = tokenBank[ctx.author.name] - bet
        
        upper = (bet * 2) + 1
        rtn = randrange(0, upper)
        
        tokenBank[ctx.author.name] = tokenBank[ctx.author.name] + rtn
        
        tokenBankFile = open("tokenBank.json", "w")
        json.dump(tokenBank, tokenBankFile)
        tokenBankFile.close()
        
        if rtn == 0:
            await ctx.send(f'The entire raiding party wiped. You have lost all of your coin and barely escaped!')
        elif rtn < bet:
            await ctx.send(f'Several of your party fell during the raid, but you were able to mitigate your losses with {rtn} coins.')
        elif rtn == bet:
            await ctx.send(f'Your raiding party fell through and you were unable to raid the stash. You keep your {rtn} coins.')
        else:
            await ctx.send(f'You manage to sneak in and out of the Dragon\'s lair undetected, returning with {rtn} coins!')
    
bot = Bot()
bot.run()