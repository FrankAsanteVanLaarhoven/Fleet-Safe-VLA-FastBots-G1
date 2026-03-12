import { useState, useEffect } from 'react';
import { animationStore } from './animationStore';

// Generates an SVG path string from an array of values (0-100)
function generateSVGPath(data: number[]) {
  if (data.length === 0) return '';
  const stepX = 100 / (data.length - 1);
  // Map data (0-100) to Y (0-40)
  const mapY = (val: number) => 40 - (val / 100) * 40;
  
  let path = `M0,${mapY(data[0])}`;
  
  for (let i = 0; i < data.length - 1; i++) {
    const x1 = i * stepX + stepX / 2;
    const y1 = mapY(data[i]);
    const x2 = i * stepX + stepX / 2;
    const y2 = mapY(data[i + 1]);
    const endX = (i + 1) * stepX;
    const endY = mapY(data[i + 1]);
    
    // Smooth bezier curve connecting points
    path += ` C${x1},${y1} ${x2},${y2} ${endX},${endY}`;
  }
  return path;
}

export function useTelemetry() {
  const [cbfInterventions, setCbfInterventions] = useState<number[]>(Array(10).fill(50));
  const [safetyViolations, setSafetyViolations] = useState<number[]>(Array(10).fill(10));
  const [adherence, setAdherence] = useState<number[]>(Array(10).fill(85));
  const [efficiency, setEfficiency] = useState<number[]>(Array(10).fill(90));
  const [robotY, setRobotY] = useState(0);

  useEffect(() => {
    let tick = 0;
    
    const interval = setInterval(() => {
      tick += 0.1;
      
      // Simulate High-Frequency telemetry streams
      setCbfInterventions(prev => {
        const next = [...prev.slice(1), 50 + Math.sin(tick) * 30 + Math.random() * 10];
        return next;
      });
      
      setSafetyViolations(prev => {
        // Keep violations near 0, occasionally spiking
        const val = Math.max(0, Math.sin(tick * 0.5) * 5 + (Math.random() > 0.9 ? 15 : 0));
        return [...prev.slice(1), val];
      });
      
      setAdherence(prev => {
        // High adherence (80-100%)
        return [...prev.slice(1), 85 + Math.sin(tick * 0.2) * 10 + Math.random() * 5];
      });
      
      setEfficiency(prev => {
         return [...prev.slice(1), 90 + Math.cos(tick * 0.3) * 8 + Math.random() * 2];
      });

      // Simple breathing/walking kinematic simulation for the 3D twin
      const y = Math.sin(tick * 2) * 0.03 + 0.95;
      setRobotY(y);
      animationStore.robotY = y;
      
    }, 200); // 5 FPS update for the UI graphs

    return () => clearInterval(interval);
  }, []);

  return {
    paths: {
      cbf: generateSVGPath(cbfInterventions.map(v => v * 0.4)), // Scale visual height
      violations: generateSVGPath(safetyViolations.map(v => v * 2)),
      adherence: generateSVGPath(adherence.map(v => v * 0.5)),
      efficiency: generateSVGPath(efficiency.map(v => v * 0.5))
    },
    metrics: {
      cbfCurrent: Math.round(cbfInterventions[cbfInterventions.length - 1]),
      violationsCurrent: Math.round(safetyViolations[safetyViolations.length - 1] / 10),
      adherenceCurrent: Math.round(adherence[adherence.length - 1]),
      efficiencyCurrent: Math.round(efficiency[efficiency.length - 1])
    },
    kinematics: {
      robotY
    }
  };
}
