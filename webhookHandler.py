from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from discord_webhook import DiscordWebhook
import json
import requests

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        query_parameters = dict(qc.split("=") for qc in query.split("&") if "=" in qc)
        
        print(self.path)
        
        if (query_parameters["hub.challenge"]) != None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(query_parameters["hub.challenge"].encode("UTF-8"))
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(("OK").encode("UTF-8"))
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("UTF-8")
        body = json.loads(body)
        
        print(body)
        print("-------------------------------")
        
        secretsFile = open("secrets.json", "r")
        secrets = json.load(secretsFile)
        secretsFile.close()
        
        twitchClientID = secrets['twitchClientID']
        discWebhookUrl = secrets['discWebhookUrl']
        
        if body['data'] > 0:
            userName = body['data'][0]['user_name']
            gameId = body['data'][0]['game_id']
            
            headers = {'Client-ID' : f'{twitchClientID}'}
            r = requests.get(f'https://api.twitch.tv/helix/games?id={gameId}', headers=headers)
            r = r.json()
            
            print(r)
            print("-------------------------------")
            
            game = r['data'][0]['game_id']
            
            if(userName == "dracoasier"):
                hookContent = f'Your favorite Dragon Vibes provider DracoAsier has gone live at https://twitch.tv/dracoasier playing {game}. Show him your Dragon Vibe Support. @here'
            else:
                hookContent = f'Another ally to the Dragon Vibes Den, {userName}, has gone live at https://twitch.tv/{userName} playing {game}. Show your Dragon Vibe Support @here!!'
                
            webhook = DiscordWebhook(url=discWebhookUrl, content=hookContent)
            webhook.execute()