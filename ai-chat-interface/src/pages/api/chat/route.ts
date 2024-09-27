import { NextResponse } from 'next/server';
import { spawn } from 'child_process';

export async function POST(request: Request) {
  const { message } = await request.json();
  
  return new Promise((resolve) => {
    const pythonProcess = spawn('python', ['../printer.py']);
    
    let currentState = '';
    let aiResponse = '';

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (!currentState) {
        currentState = output;
      } else if (!aiResponse) {
        // Ignore the second output
      } else {
        aiResponse += output + '\n';
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Error: ${data}`);
    });

    pythonProcess.stdin.write(message + '\n');
    pythonProcess.stdin.end();

    pythonProcess.on('close', (code) => {
      resolve(NextResponse.json({ currentState, aiResponse: aiResponse.trim() }));
    });
  });
}