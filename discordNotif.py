import json
from discord_webhook import DiscordWebhook

secretsFile = open("secrets.json", "r")
secrets = json.load(secretsFile)
secretsFile.close()

dataFile = open("/tmp/webRes.json", "r")
data = json.load(dataFile)
dataFile.close()

twitchClientID = secrets['twitchClientID']

discWebhookUrl = secrets['discWebhookUrl']

userName = data['data'][0]['user_name']
gameId = data['data'][0]['game_id']

headers = {'Client-ID' : f'{twitchClientID}'}
r = requests.get(f'https://api.twitch.tv/helix/games?id={gameId}')
r = r.json()

if(userName == "dracoasier"){
    hookContent = f'Your favorite Dragon Vibes provider DracoAsier has gone live at https://twitch.tv/dracoasier playing {game}. Show him your Dragon Vibe Support. @here'
} else {
    hookContent = f'Another ally to the Dragon Vibes Den, {name}, has gone live at https://twitch.tv/{userName} playing {game}. Show your Dragon Vibe Support @here!!'
}

webhook = DiscordWebhook(url=discWebhookUrl, content=hookContent)

webhook.execute()