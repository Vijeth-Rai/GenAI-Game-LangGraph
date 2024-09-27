'use client'
import React from 'react'

import { ChatInterfaceComponent } from './chat-interface'

export function AppComponent() {
  return (
    <div className="min-h-screen bg-black flex flex-col">
      <header className="bg-gray-900 text-gray-300 p-4 shadow-md">
        <h1 className="text-2xl font-bold">AI Chat Interface</h1>
      </header>
      <main className="flex-grow">
        <ChatInterfaceComponent />
      </main>
    </div>
  )
}