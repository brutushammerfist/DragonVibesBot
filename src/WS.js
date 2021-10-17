//import WebSocket, { WebSocketServer } from "ws";
const { WebSocket, WebSocketServer } = require('ws');

/*const wss = new WebSocketServer({ port: 8888 });

wss.on('connection', function connection(ws) {
    ws.on('message', function incoming(message) {
        console.log('received: %s', message);
    });

    ws.send('Ping');
});

wss.on('listening', function () {
    console.log("Websocket Server Started");
});*/

class WS {
    constructor() {
        this.wss = new WebSocket.Server({ port: 8888 });

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