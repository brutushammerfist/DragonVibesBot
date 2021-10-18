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
            ws.on('message', function incoming(message) {
                console.log('received: %s', message);
            });

            ws.send('something');
        });

        this.wss.on('listening', function () {
            console.log("Websocket Server Started");
        });

        this.server.listen(8080);
    }

    broadcastMessage() {

    }
}

module.exports = new WS();