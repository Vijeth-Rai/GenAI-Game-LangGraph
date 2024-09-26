const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(bodyParser.json());

let pythonProcess;

function startPythonProcess() {
  pythonProcess = spawn('python', ['../main.py']);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    // Restart the process if it closes unexpectedly
    startPythonProcess();
  });
}

// Start the Python process when the server starts
startPythonProcess();

app.get('/status', (req, res) => {
  res.json({ status: pythonProcess ? 'Alive' : 'Dead' });
});

app.post('/restart', (req, res) => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  startPythonProcess();
  res.json({ success: true });
});

app.post('/chat', (req, res) => {
  const { message } = req.body;
  
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });

  if (!pythonProcess) {
    res.write(JSON.stringify({ message: "Error: Python process is not running.", currentState: "Error", nextState: "Error" }));
    res.end();
    return;
  }

  pythonProcess.stdin.write(message + '\n');

  let buffer = '';

  const dataHandler = (data) => {
    buffer += data.toString();
    const lines = buffer.split('\n');
    
    while (lines.length > 3) {
      const message = lines.shift();
      const currentState = lines.shift();
      const nextState = lines.shift();
      
      const update = JSON.stringify({ message, currentState, nextState });
      res.write(update + '\n');
    }
    
    buffer = lines.join('\n');
  };

  pythonProcess.stdout.on('data', dataHandler);

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  req.on('close', () => {
    pythonProcess.stdout.removeListener('data', dataHandler);
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));