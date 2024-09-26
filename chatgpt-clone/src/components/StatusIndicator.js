import React, { useState, useEffect } from 'react';
import './StatusIndicator.css';

const StatusIndicator = () => {
  const [status, setStatus] = useState('Unknown');

  const checkStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/status');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setStatus(data.status);
    } catch (error) {
      console.error('Error checking status:', error);
      setStatus('Dead');
    }
  };

  const restartPython = async () => {
    try {
      const response = await fetch('http://localhost:5000/restart', { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        checkStatus();
      }
    } catch (error) {
      console.error('Error restarting Python process:', error);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 1000); // Check status every second
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-indicator">
      <span className={`status-dot ${status.toLowerCase()}`}></span>
      <span className="status-text">main.py: {status}</span>
      <button onClick={restartPython}>Restart</button>
    </div>
  );
};

export default StatusIndicator;