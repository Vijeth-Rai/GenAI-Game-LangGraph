import { spawn } from 'child_process';
import { join } from 'path';

export default function handler(req, res) {
  if (req.method === 'POST') {
    const { message } = req.body;
    const scriptPath = join(process.cwd(), '..', 'printer.py');

    // Set up SSE
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    const pythonProcess = spawn('python', [scriptPath]);

    pythonProcess.stdin.write(message + '\n');
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
      // console.log("script",data.toString());
      res.write(data);
      res.flush();
      // console.log('Sending stdout data:', data.toString());

    });

    pythonProcess.stderr.on('data', (data) => {
      // console.log('Sending stderr data:', data.toString());
      res.write(`data: error: ${data}\n\n`);
      res.end(); // End the response after writing error
    });

    pythonProcess.on('close', (code) => {
      // console.log(`Sending process exit message with code ${code}`);
      // res.write(`data: Python process exited with code ${code}\n\n`);
      res.end();
    });
  } else if (req.method === 'GET') {
    // Handle GET request for SSE
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    // Send an initial message
    // console.log('Sending initial connection message');
    res.write(`data: Connected to SSE\n\n`);

    // Keep the connection alive
    const intervalId = setInterval(() => {
      //console.log('Sending heartbeat message');
      res.write(`data: heartbeat\n\n`);
    }, 15000);

    // Clean up on close
    res.on('close', () => {
      clearInterval(intervalId);
      res.end();
    });
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}