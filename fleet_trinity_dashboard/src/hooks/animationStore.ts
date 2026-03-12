/**
 * Module-level mutable store for high-frequency animation data.
 * Written by useTelemetry and useFleetAPI, read inside useFrame by URDFRobot.
 * This bypasses React's render cycle entirely — no props, no state, no re-renders.
 */
export const animationStore = {
  robotY: 0.95,
  robots: {} as Record<string, { fsm: string; policy: string; position?: number[]; arm?: string | null }>,
};
