import React from 'react';
import Chat from './components/Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <div className="left-side">
        {/* You can add content for the left side here */}
      </div>
      <Chat />
    </div>
  );
}

export default App;
