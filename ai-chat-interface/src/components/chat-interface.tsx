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

export function ChatInterfaceComponent() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentState, setCurrentState] = useState('Idle')
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return;

    console.log('Sending message:', inputMessage);
    const newMessage: Message = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentState('Thinking');

    try {
      console.log('Sending POST request to /api/python-script');
      const response = await fetch('/api/python-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });
      console.log('API response status:', response.status);
      
      const responseBody = await response.text();
      console.log('API response body:', responseBody);

      // Process the response as sets of 3
      const responseLines = responseBody.split('\n');
      for (let i = 0; i < responseLines.length; i += 3) {
        const message = responseLines[i + 2];
        if (message && message !== 'wait') {
          setMessages((prevMessages) => [
            ...prevMessages,
            { text: message, sender: 'ai' }
          ]);
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
              onClick={handleSendMessage}
              className="chat-send-button"
              disabled={isLoading}
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}