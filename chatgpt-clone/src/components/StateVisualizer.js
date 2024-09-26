import React from 'react';
import './StateVisualizer.css';

const StateVisualizer = ({ currentState, nextState }) => {
  return (
    <div className="state-visualizer">
      <h2>Graph State</h2>
      <div className="state-container">
        <div className="state current-state">
          <h3>Current State</h3>
          <div className="state-box">{currentState || 'N/A'}</div>
        </div>
        <div className="arrow">→</div>
        <div className="state next-state">
          <h3>Next State</h3>
          <div className="state-box">{nextState || 'N/A'}</div>
        </div>
      </div>
    </div>
  );
};

export default StateVisualizer;
