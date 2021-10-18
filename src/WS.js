const { readFileSync } = require('fs');
const { createServer } = require('https');
const { WebSocketServer } = require('ws');

class WS {
    constructor() {
        this.server = createServer({
            cert: readFileSync("/etc/letsencrypt/live/brutus.dev/fullchain.pem"),
            key: readFileSync("/etc/letsencrypt/live/brutus.dev/privkey.pem")
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
}

module.exports = new WS();