'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Trash2, Eye, RefreshCw } from 'lucide-react'
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

type Document = {
  _id: string
  [key: string]: any
}

export function ChatInterfaceComponent() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentState, setCurrentState] = useState('Idle')
  const [stateInfo, setStateInfo] = useState<StateInfo>({ current: '', next: '' })
  const [documents, setDocuments] = useState<Document[]>([])
  const [showDocuments, setShowDocuments] = useState(false)
  const [showUnsavedDocuments, setShowUnsavedDocuments] = useState(false)
  const [showSavedDocuments, setShowSavedDocuments] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [isPythonRunning, setIsPythonRunning] = useState(false);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return;

    const newMessage: Message = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentState('Thinking');
    setIsPythonRunning(true); 

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
    setIsPythonRunning(false); // Set Python as not running when the response is complete
  }

  const handleDeleteCollection = async () => {
    if (confirm('Are you sure you want to delete all documents in the checkpoints collection?')) {
      try {
        const response = await fetch('/api/delete-collection', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ database: 'checkpoints', collection: 'checkpoints' }),
        });
        if (response.ok) {
          alert('Collection deleted successfully');
          setDocuments([]);
        } else {
          alert('Failed to delete collection');
        }
      } catch (error) {
        console.error('Error deleting collection:', error);
        alert('Error deleting collection');
      }
    }
  }

  const fetchDocuments = async (threadId: string) => {
    setIsLoadingDocuments(true)
    try {
      const response = await fetch('/api/get-documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          database: 'checkpoints', 
          collection: 'checkpoints',
          threadId: threadId
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      } else {
        alert('Failed to fetch documents');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      alert('Error fetching documents');
    } finally {
      setIsLoadingDocuments(false)
    }
  }

  const refreshDocuments = async () => {
    if (showUnsavedDocuments) {
      await fetchDocuments('1');
    } else if (showSavedDocuments) {
      await fetchDocuments('latest');
    }
  }

  useEffect(() => {
    if (showUnsavedDocuments) {
      fetchDocuments('1');
    } else if (showSavedDocuments) {
      fetchDocuments('latest');
    }
  }, [showUnsavedDocuments, showSavedDocuments]);

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  return (
    <div className="page-container">
      <div className="chat-container">
        <div className="left-panel">
          <div className="state-info">
            <div className="state-item">
              <span className="state-label">Current State:</span>
              <span className="state-value">{stateInfo.current}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Next State:</span>
              <span className="state-value">{stateInfo.next}</span>
            </div>
          </div>
          <div className="database-controls">
            <Button
              className="delete-button"
              onClick={handleDeleteCollection}
              variant="destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Collection
            </Button>
            <div className="view-buttons-container">
              <Button
                className={`view-checkpoints-button ${showUnsavedDocuments ? 'active' : ''}`}
                onClick={() => {
                  setShowUnsavedDocuments(!showUnsavedDocuments);
                  setShowSavedDocuments(false);
                }}
              >
                <Eye className="h-4 w-4 mr-2" />
                {showUnsavedDocuments ? 'Hide Checkpoints' : 'View Checkpoints'}
              </Button>
              <Button
                className={`view-documents-button ${showSavedDocuments ? 'active' : ''}`}
                onClick={() => {
                  setShowSavedDocuments(!showSavedDocuments);
                  setShowUnsavedDocuments(false);
                }}
              >
                <Eye className="h-4 w-4 mr-2" />
                {showSavedDocuments ? 'Hide Documents' : 'View Documents'}
              </Button>
            </div>
            {(showUnsavedDocuments || showSavedDocuments) && (
              <Button
                className="refresh-documents-button"
                onClick={refreshDocuments}
                disabled={isLoadingDocuments}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingDocuments ? 'animate-spin' : ''}`} />
                Refresh Documents
              </Button>
            )}
          </div>
          {(showUnsavedDocuments || showSavedDocuments) && (
            <div className="documents-view">
              <h3 className="text-lg font-semibold mb-2">
                {showUnsavedDocuments ? 'Checkpoints' : 'Documents'}
              </h3>
              <div className="documents-scroll-area">
                {isLoadingDocuments ? (
                  <div className="flex justify-center items-center h-full">
                    <LoadingCircleComponent state="Loading" />
                  </div>
                ) : documents.length > 0 ? (
                  documents.map((doc) => (
                    <div key={doc._id} className="document-item">
                      <pre className="document-content">
                        {JSON.stringify(doc, null, 2)}
                      </pre>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 dark:text-gray-400">No documents found</div>
                )}
              </div>
            </div>
          )}
        </div>
        <div className={`python-status-indicator ${isPythonRunning ? 'running' : ''}`}></div>
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
              <div ref={messagesEndRef} /> {/* Add this line */}
            </ScrollArea>
          </div>
          <div className="chat-input-area">
            <div className="chat-input-container">
              <div className="chat-input">
                {isLoading && (
                  <div className="loading-indicator">
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
    </div>
  )
}