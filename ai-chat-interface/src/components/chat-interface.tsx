'use client'

import { useState, useRef, useEffect } from 'react'
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

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return

    const newMessage: Message = { text: inputMessage, sender: 'user' }
    setMessages((prevMessages) => [...prevMessages, newMessage])
    setInputMessage('')
    setIsLoading(true)
    setCurrentState('Processing')

    // Simulating AI response
    setTimeout(() => {
      const aiResponse: Message = { text: 'This is a simulated AI response.', sender: 'ai' }
      setMessages((prevMessages) => [...prevMessages, aiResponse])
      setIsLoading(false)
      setCurrentState('Idle')
    }, 2000)
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