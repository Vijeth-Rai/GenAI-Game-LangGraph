'use client'

import { useState, useRef } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { LoadingCircleComponent } from './loading-circle'
import './chat-interface.css'

type Message = {
  text: string
  sender: 'user' | 'ai'
}

type StateInfo = {
  current: string
  next: string
}

export function ChatInterfaceComponent() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentState, setCurrentState] = useState('Idle')
  const [stateInfo, setStateInfo] = useState<StateInfo>({ current: '', next: '' })
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return;

    const newMessage: Message = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentState('Thinking');

    try {
      const response = await fetch('/api/python-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        
        body: JSON.stringify({ message: inputMessage }),
      });

      console.log(response)
      
      if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let partialMessage = '';
        let lineCount = 0;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          partialMessage += decoder.decode(value, { stream: true });
          
          const responseLines = partialMessage.split('\n');
          while (responseLines.length >= 3) {
            const current = responseLines.shift();
            const next = responseLines.shift();
            const message = responseLines.shift();

            if (current && next) {
              setStateInfo({ current, next });
            }

            if (message && message !== 'wait') {
              setMessages((prevMessages) => [
                ...prevMessages,
                { text: message, sender: 'ai' }
              ]);
            }

            lineCount++;
            if (lineCount % 3 === 0) {
              partialMessage = responseLines.join('\n');
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "Sorry, there was an error processing your request.", sender: 'ai' }
      ]);
    }

    setIsLoading(false);
    setCurrentState('Idle');
  }

  return (
    <div className="chat-container">
      <div className="state-info">
        <h2>Current State: {stateInfo.current}</h2>
        <h2>Next State: {stateInfo.next}</h2>
      </div>
      <div className="chat-window">
        <div className="chat-messages">
          <ScrollArea className="h-full p-6" ref={scrollAreaRef}>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-container ${message.sender}`}
              >
                <div className={`message-bubble ${message.sender}`}>
                  {message.text}
                </div>
              </div>
            ))}
          </ScrollArea>
        </div>
        <div className="chat-input-area">
          <div className="chat-input-container">
            <div className="chat-input">
              {isLoading && (
                <div className="absolute left-3 top-1/2 transform -translate-y-1/2 z-10">
                  <LoadingCircleComponent state={currentState} />
                </div>
              )}
              <Input
                type="text"
                placeholder="Type message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={isLoading}
              />
            </div>
            <Button
              className="chat-send-button"
              onClick={handleSendMessage}
              disabled={isLoading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}