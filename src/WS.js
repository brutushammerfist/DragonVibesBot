const { readFileSync } = require('fs');
const { createServer } = require('https');
const { WebSocketServer } = require('ws');
const secrets = require('../secrets.json');
const Bot = require('./Bot.js');

class WS {
    constructor() {
        this.server = createServer({
            cert: readFileSync(secrets.certPath),
            key: readFileSync(secrets.keyPath)
        });

        this.wss = new WebSocketServer({ server: this.server });

        this.wss.on('connection', function connection(ws) {
            this.ws = ws;

            this.ws.on('message', function incoming(message) {
                console.log('received: %s', message);
                this.handleMessage(message);
            });

            this.ws.send('something');
        });

        this.wss.on('listening', function () {
            console.log("Websocket Server Started");
        });

        this.server.listen(8080);
    }

    broadcastMessage(message) {
        this.wss.clients.forEach(function each(client) {
            if (client !== this.ws && client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });
    }

    handleMessage(message) {
        switch (message) {
            case "clear-giveaway":
                Bot.clearGiveaway();
                break;
            case "clear-pool":
                Bot.clearPool();
                break;
            case "pull-giveaway":
                Bot.pullGiveaway();
                break;
            case "pull-pool":
                Bot.pullPool();
                break;
            default:
                var data = JSON.parse(message);

                if (data.removeGiveaway) {
                    Bot.removeGiveawayEntry(data.removeGiveaway);
                }

                if (data.removePool) {
                    Bot.removePoolEntry(data.removePool);
                }
        }
    }
}

module.exports = new WS();