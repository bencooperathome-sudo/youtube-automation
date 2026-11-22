import React from 'react';
import { Composition } from 'remotion';
import { ToolSmoke } from './tool-smoke';

export const Root: React.FC = () => (
  <Composition id="TrainAthleteToolSmoke" component={ToolSmoke} durationInFrames={90} fps={30} width={1280} height={720} />
);
