const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8765');
ws.on('open', () => console.log('Connected'));
ws.on('message', data => console.log('Msg:', data.slice(0, 100).toString()));
ws.on('error', err => console.log('Err:', err.message));
ws.on('close', () => console.log('Closed'));
