const { readFileSync } = require('fs');
const { createServer } = require('https');
const { WebSocketServer } = require('ws');
const secrets = require('../secrets.json');

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
}

module.exports = new WS();