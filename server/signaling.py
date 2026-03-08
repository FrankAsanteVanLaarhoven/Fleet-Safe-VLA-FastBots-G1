#!/usr/bin/env python3
"""
server/signaling.py — WebRTC Signaling Server

WebSocket-based signaling for:
  - Isaac Sim WebRTC stream relay
  - Robot camera feed negotiation
  - WebRTX DataChannel establishment (3D state sync)

Room-based: each robot is a room. Peers join rooms to exchange
SDP offers/answers and ICE candidates.

Usage:
    python server/signaling.py              # default port 8765
    python server/signaling.py --port 9000  # custom port

Protocol messages (JSON over WebSocket):
    → { type: "join-room", room: "robot_0" }
    → { type: "offer", room: "robot_0", sdp: {...} }
    ← { type: "answer", room: "robot_0", sdp: {...} }
    ↔ { type: "ice-candidate", room: "robot_0", candidate: {...} }
    → { type: "leave-room", room: "robot_0" }
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from typing import Dict, Set

try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("Install: pip install websockets")
    raise

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger('signaling')

# ═══════════════════════════════════════════════════════════════════
#  Room Manager
# ═══════════════════════════════════════════════════════════════════

class RoomManager:
    """Manages WebRTC signaling rooms (one per robot)."""

    def __init__(self):
        self.rooms: Dict[str, Set] = defaultdict(set)  # room_id → set of websockets
        self.peer_rooms: Dict[int, str] = {}  # ws_id → room_id
        self.stats = {
            'total_connections': 0,
            'total_messages': 0,
            'rooms_active': 0,
            'start_time': time.time(),
        }

    def join(self, ws, room_id: str):
        ws_id = id(ws)
        # Leave previous room if any
        if ws_id in self.peer_rooms:
            self.leave(ws)
        self.rooms[room_id].add(ws)
        self.peer_rooms[ws_id] = room_id
        self.stats['rooms_active'] = len([r for r in self.rooms.values() if r])
        log.info(f"  [{room_id}] +peer (total: {len(self.rooms[room_id])})")

    def leave(self, ws):
        ws_id = id(ws)
        room_id = self.peer_rooms.pop(ws_id, None)
        if room_id and ws in self.rooms[room_id]:
            self.rooms[room_id].discard(ws)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            self.stats['rooms_active'] = len([r for r in self.rooms.values() if r])
            log.info(f"  [{room_id}] -peer (total: {len(self.rooms.get(room_id, set()))})")

    def get_peers(self, ws, room_id: str):
        """Get all other peers in the room (excluding sender)."""
        return [peer for peer in self.rooms.get(room_id, set()) if peer != ws]

    async def broadcast(self, ws, room_id: str, message: dict):
        """Send message to all other peers in the room."""
        peers = self.get_peers(ws, room_id)
        self.stats['total_messages'] += 1
        if peers:
            await asyncio.gather(
                *[peer.send(json.dumps(message)) for peer in peers],
                return_exceptions=True
            )


# ═══════════════════════════════════════════════════════════════════
#  WebSocket Handler
# ═══════════════════════════════════════════════════════════════════

rooms = RoomManager()

# Optional: simple token auth from environment
AUTH_TOKEN = os.environ.get('SIGNALING_TOKEN', '')


async def handler(ws):
    """Handle a single WebSocket connection."""
    rooms.stats['total_connections'] += 1
    client_ip = ws.remote_address[0] if ws.remote_address else 'unknown'
    log.info(f"[CONNECT] {client_ip} (total: {rooms.stats['total_connections']})")

    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send(json.dumps({'error': 'invalid JSON'}))
                continue

            msg_type = msg.get('type', '')
            room_id = msg.get('room', '')

            # Auth check (if token set)
            if AUTH_TOKEN and msg.get('token') != AUTH_TOKEN:
                if msg_type not in ('ping',):
                    await ws.send(json.dumps({'error': 'unauthorized'}))
                    continue

            if msg_type == 'join-room':
                if not room_id:
                    await ws.send(json.dumps({'error': 'room required'}))
                    continue
                rooms.join(ws, room_id)
                await ws.send(json.dumps({
                    'type': 'joined',
                    'room': room_id,
                    'peers': len(rooms.rooms.get(room_id, set()))
                }))

            elif msg_type == 'leave-room':
                rooms.leave(ws)
                await ws.send(json.dumps({'type': 'left', 'room': room_id}))

            elif msg_type in ('offer', 'answer', 'ice-candidate'):
                if not room_id:
                    continue
                # Forward to other peers in the room
                await rooms.broadcast(ws, room_id, msg)

            elif msg_type == 'ping':
                await ws.send(json.dumps({
                    'type': 'pong',
                    'timestamp': time.time(),
                    'rooms': rooms.stats['rooms_active'],
                    'uptime': int(time.time() - rooms.stats['start_time']),
                }))

            else:
                await ws.send(json.dumps({'error': f'unknown type: {msg_type}'}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        rooms.leave(ws)
        log.info(f"[DISCONNECT] {client_ip}")


# ═══════════════════════════════════════════════════════════════════
#  CORS HTTP Handler (for health check)
# ═══════════════════════════════════════════════════════════════════

async def health_check(path, headers):
    """Respond to HTTP GET /health with server stats."""
    if path == '/health':
        body = json.dumps({
            'status': 'ok',
            'rooms_active': rooms.stats['rooms_active'],
            'total_connections': rooms.stats['total_connections'],
            'total_messages': rooms.stats['total_messages'],
            'uptime': int(time.time() - rooms.stats['start_time']),
        })
        return (200, [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')], body)
    return None


# ═══════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════

async def main(host: str, port: int):
    log.info(f"═══ SAFER-VLA WebRTC Signaling Server ═══")
    log.info(f"  Listening on ws://{host}:{port}")
    log.info(f"  Health check: http://{host}:{port}/health")
    if AUTH_TOKEN:
        log.info(f"  Token auth: enabled")
    else:
        log.info(f"  Token auth: disabled (set SIGNALING_TOKEN env)")

    async with serve(handler, host, port, process_request=health_check):
        await asyncio.Future()  # Run forever


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SAFER-VLA WebRTC Signaling Server')
    parser.add_argument('--host', default='0.0.0.0', help='Bind host')
    parser.add_argument('--port', type=int, default=8765, help='Bind port')
    args = parser.parse_args()

    asyncio.run(main(args.host, args.port))
