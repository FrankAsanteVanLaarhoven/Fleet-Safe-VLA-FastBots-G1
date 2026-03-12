import { useState, useEffect, useCallback, useRef } from 'react';
import { animationStore } from './animationStore';

// Mirroring the Python API definitions
export interface RobotState {
  fsm: string;
  policy: string;
  position: [number, number, number];
  arm: string | null;
}

export interface PipelineStatus {
  record: string;
  hdf5: string;
  lerobot: string;
  train: string;
  deploy: string;
}

export interface FleetState {
  robots: Record<string, RobotState>;
  pipeline?: PipelineStatus;
  wsConnected: boolean;
}

const API_BASE_URL = 'http://localhost:8000/api';
const WS_BASE_URL = 'ws://localhost:8000/ws';

export function useFleetAPI() {
  const [fleetState, setFleetState] = useState<FleetState>({
    robots: {
      'robot_0': { fsm: 'Passive', policy: 'HospitalPatrol', position: [0,0,0], arm: null },
      'robot_1': { fsm: 'Passive', policy: 'HospitalPatrol', position: [0,0,0], arm: null }
    },
    wsConnected: false
  });

  const wsRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket Connection
  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWS = () => {
      try {
        ws = new WebSocket(`${WS_BASE_URL}/fleet`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('[Fleet API] WebSocket Connected');
          setFleetState(prev => ({ ...prev, wsConnected: true }));
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'init') {
              setFleetState(prev => ({ 
                ...prev, 
                robots: data.robots || prev.robots,
                pipeline: data.pipeline
              }));
            } else if (data.type === 'fsm') {
              setFleetState(prev => ({
                ...prev,
                robots: {
                  ...prev.robots,
                  [data.robot_id]: { ...prev.robots[data.robot_id], fsm: data.new }
                }
              }));
            } else if (data.type === 'policy') {
              setFleetState(prev => ({
                ...prev,
                robots: {
                  ...prev.robots,
                  [data.robot_id]: { ...prev.robots[data.robot_id], policy: data.policy }
                }
              }));
            }
          } catch (e) {
            console.error('[Fleet API] Error parsing WS message:', e);
          }
        };

        ws.onclose = () => {
          console.log('[Fleet API] WebSocket Disconnected. Reconnecting...');
          setFleetState(prev => ({ ...prev, wsConnected: false }));
          reconnectTimeout = setTimeout(connectWS, 3000); // 3s backoff
        };
        
        ws.onerror = (err) => {
            console.error('[Fleet API] WebSocket Error:', err);
        };
      } catch (e) {
        console.error('[Fleet API] Failed to connect WebSocket', e);
      }
    };

    connectWS();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, []);

  // Sync robot states into the animation store for the 3D viewer
  useEffect(() => {
    animationStore.robots = fleetState.robots;
  }, [fleetState.robots]);

  // REST API Mutations
  const setFSMState = useCallback(async (robotId: string, state: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/fleet/${robotId}/fsm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (e) {
      console.error(`[Fleet API] Failed to set FSM for ${robotId}:`, e);
      return null;
    }
  }, []);

  const setPolicy = useCallback(async (robotId: string, policy: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/fleet/${robotId}/policy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (e) {
      console.error(`[Fleet API] Failed to set policy for ${robotId}:`, e);
      return null;
    }
  }, []);

  return {
    ...fleetState,
    setFSMState,
    setPolicy
  };
}
