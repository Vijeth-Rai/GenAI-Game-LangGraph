const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(bodyParser.json());

app.post('/chat', (req, res) => {
  const { message } = req.body;
  
  const pythonProcess = spawn('python', ['../main.py']);
  
  pythonProcess.stdin.write(message);
  pythonProcess.stdin.end();

  let botResponse = '';

  pythonProcess.stdout.on('data', (data) => {
    botResponse += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python process exited with code ${code}`);
      res.status(500).json({ error: 'An error occurred while processing your request.' });
    } else {
      // Extract the ChatAgent response from the botResponse
      const chatAgentResponse = extractChatAgentResponse(botResponse);
      res.json({ message: chatAgentResponse });
    }
  });
});

function extractChatAgentResponse(output) {
  // Implement logic to extract the ChatAgent response from the output
  // This will depend on the exact format of your Python script's output
  // For now, we'll just return the entire output
  return output;
}

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));