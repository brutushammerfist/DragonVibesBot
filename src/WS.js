const { WebSocketServer } = require('ws');

class WS {
    constructor() {
        this.wss = new WebSocketServer({ port: 8080, host: "brutus.dev" });

        this.wss.on('connection', function connection(ws) {
            ws.on('message', function incoming(message) {
                console.log('received: %s', message);
            });

            ws.send('Ping');
        });

        this.wss.on('listening', function () {
            console.log("Websocket Server Started");
        });
    }
}

module.exports = new WS();