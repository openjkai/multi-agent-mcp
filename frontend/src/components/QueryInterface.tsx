'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Loader2, Bot, User, AlertCircle, Copy, Check } from 'lucide-react'
import toast from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'agent'
  content: string
  timestamp: Date
  agentName?: string
  agentId?: string
  error?: boolean
  processingTime?: number
}

interface QueryResponse {
  status: string
  result?: {
    response: {
      response: string
    }
    agent_name: string
    agent_id: string
    processing_time: number
  }
  error?: string
}

export function QueryInterface() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentQuery = query
    setQuery('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: currentQuery }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: QueryResponse = await response.json()

      if (data.status === 'success' && data.result) {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: data.result.response.response,
          timestamp: new Date(),
          agentName: data.result.agent_name,
          agentId: data.result.agent_id,
          processingTime: data.result.processing_time
        }
        setMessages(prev => [...prev, agentMessage])
        toast.success(`Response from ${data.result.agent_name}`)
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: data.error || 'Failed to get response from agents',
          timestamp: new Date(),
          error: true
        }
        setMessages(prev => [...prev, errorMessage])
        toast.error(data.error || 'Failed to get response')
      }
    } catch (error) {
      console.error('Query error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'Failed to connect to backend. Please check if the server is running.',
        timestamp: new Date(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to connect to backend')
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedMessageId(messageId)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (error) {
      toast.error('Failed to copy to clipboard')
    }
  }

  const clearChat = () => {
    setMessages([])
    toast.success('Chat cleared')
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Chat with AI Agents</h3>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Clear Chat
          </button>
        )}
      </div>
      
      {/* Messages */}
      <div className="h-80 overflow-y-auto mb-4 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <Bot className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium mb-2">Start a conversation</p>
            <p className="text-sm">Ask our AI agents anything - they're specialized in documents, code, web search, and general chat.</p>
          </div>
        ) : (
          messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`p-2 rounded-full flex-shrink-0 ${
                  message.type === 'user' 
                    ? 'bg-primary-600' 
                    : message.error 
                      ? 'bg-red-100' 
                      : 'bg-gray-200'
                }`}>
                  {message.type === 'user' ? (
                    <User className="h-4 w-4 text-white" />
                  ) : message.error ? (
                    <AlertCircle className="h-4 w-4 text-red-600" />
                  ) : (
                    <Bot className="h-4 w-4 text-gray-600" />
                  )}
                </div>
                <div className={`rounded-lg px-3 py-2 relative group ${
                  message.type === 'user' 
                    ? 'bg-primary-600 text-white' 
                    : message.error
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {/* Message metadata */}
                  <div className="flex items-center justify-between mt-2 text-xs opacity-75">
                    <div className="flex items-center space-x-2">
                      <span>{formatTime(message.timestamp)}</span>
                      {message.agentName && (
                        <span>• {message.agentName}</span>
                      )}
                      {message.processingTime && (
                        <span>• {message.processingTime.toFixed(2)}s</span>
                      )}
                    </div>
                    
                    {/* Copy button */}
                    <button
                      onClick={() => copyToClipboard(message.content, message.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-black/10 rounded"
                    >
                      {copiedMessageId === message.id ? (
                        <Check className="h-3 w-3" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        )}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-2">
              <div className="p-2 rounded-full bg-gray-200">
                <Bot className="h-4 w-4 text-gray-600" />
              </div>
              <div className="rounded-lg px-3 py-2 bg-gray-100">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-gray-600">Agent is thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask our AI agents anything..."
          className="input-field flex-1"
          disabled={isLoading}
          maxLength={1000}
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed min-w-[44px]"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </form>
      
      {/* Character count */}
      <div className="mt-2 text-xs text-gray-500 text-right">
        {query.length}/1000 characters
      </div>
    </div>
  )
}
