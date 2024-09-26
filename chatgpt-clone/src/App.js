import React, { useState } from 'react';
import Chat from './components/Chat';
import StateVisualizer from './components/StateVisualizer';
import StatusIndicator from './components/StatusIndicator';
import './App.css';

function App() {
  const [currentState, setCurrentState] = useState('');
  const [nextState, setNextState] = useState('');

  const updateStates = (current, next) => {
    setCurrentState(current);
    setNextState(next);
  };

  return (
    <div className="App">
      <StatusIndicator />
      <div className="left-side">
        <StateVisualizer currentState={currentState} nextState={nextState} />
      </div>
      <Chat updateStates={updateStates} />
    </div>
  );
}

export default App;
