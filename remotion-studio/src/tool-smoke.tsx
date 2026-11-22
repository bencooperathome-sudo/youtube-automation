import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

// A neutral render check. Replace with approved footage, branding and audio for production work.
export const ToolSmoke: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15, 72, 89], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const rise = interpolate(frame, [0, 24], [28, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <AbsoluteFill style={{ background: '#0b1425', color: '#ffffff', fontFamily: 'Arial, sans-serif', justifyContent: 'center', alignItems: 'center' }}>
    <div style={{ opacity, transform: `translateY(${rise}px)`, textAlign: 'center' }}>
      <div style={{ fontSize: 21, letterSpacing: 6, color: '#94b7ff' }}>TRAIN ATHLETE</div>
      <div style={{ fontSize: 68, fontWeight: 700, marginTop: 20 }}>Video pipeline check</div>
      <div style={{ fontSize: 24, color: '#b5c4d8', marginTop: 20 }}>Remotion render test · 3 seconds</div>
    </div>
  </AbsoluteFill>;
};
