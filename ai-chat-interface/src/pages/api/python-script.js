import { spawn } from 'child_process';
import { join } from 'path';

export default function handler(req, res) {
  if (req.method === 'POST') {
    const { message } = req.body;
    const scriptPath = join(process.cwd(), '..', 'printer.py');
    const pythonProcess = spawn('python', [scriptPath]);

    pythonProcess.stdin.write(message + '\n');
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
      console.log(`Python output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      res.status(200).json({ message: 'Python script executed' });
    });
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}