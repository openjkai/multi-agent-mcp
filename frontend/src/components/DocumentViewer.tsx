'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText, 
  Search, 
  Eye, 
  Download, 
  Trash2, 
  Clock,
  Hash,
  Filter,
  X,
  ChevronDown,
  ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'

interface DocumentChunk {
  chunk_id: string
  content: string
  score: number
  metadata: {
    filename: string
    chunk_index: number
    chunk_type?: string
    section_header?: string
  }
}

interface Document {
  id: string
  filename: string
  content_type: string
  chunk_count: number
  processing_status: string
  created_at: string
  metadata: {
    character_count: number
    word_count: number
    language?: string
    has_code?: boolean
    estimated_reading_time?: number
  }
}

interface SearchResult {
  chunk_id: string
  document_id: string
  content: string
  similarity_score: number
  metadata: any
  document_filename: string
}

export function DocumentViewer() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set())
  const [filterType, setFilterType] = useState<string>('all')

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/rag/status')
      const data = await response.json()
      
      if (data.status === 'success') {
        // Mock documents for now - in real implementation, this would come from the API
        const mockDocs: Document[] = [
          {
            id: 'doc1',
            filename: 'sample_document.txt',
            content_type: 'text',
            chunk_count: 5,
            processing_status: 'completed',
            created_at: new Date().toISOString(),
            metadata: {
              character_count: 2500,
              word_count: 450,
              language: 'english',
              has_code: false,
              estimated_reading_time: 2.25
            }
          }
        ]
        setDocuments(mockDocs)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    try {
      const response = await fetch('http://localhost:8000/rag/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 10
        }),
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        setSearchResults(data.results || [])
        toast.success(`Found ${data.results?.length || 0} relevant chunks`)
      } else {
        toast.error(data.error || 'Search failed')
      }
    } catch (error) {
      console.error('Search error:', error)
      toast.error('Search failed')
    } finally {
      setIsSearching(false)
    }
  }

  const toggleChunkExpansion = (chunkId: string) => {
    const newExpanded = new Set(expandedChunks)
    if (newExpanded.has(chunkId)) {
      newExpanded.delete(chunkId)
    } else {
      newExpanded.add(chunkId)
    }
    setExpandedChunks(newExpanded)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getContentTypeIcon = (contentType: string) => {
    switch (contentType) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-500" />
      case 'markdown':
        return <FileText className="h-5 w-5 text-blue-500" />
      default:
        return <FileText className="h-5 w-5 text-gray-500" />
    }
  }

  const filteredResults = searchResults.filter(result => {
    if (filterType === 'all') return true
    return result.metadata?.content_type === filterType
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <FileText className="h-6 w-6 mr-2 text-primary-600" />
          Document Library
        </h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Search Interface */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Search Documents</h3>
        
        <div className="flex space-x-2 mb-4">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search through your documents..."
              className="input-field"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={!searchQuery.trim() || isSearching}
            className="btn-primary disabled:opacity-50"
          >
            {isSearching ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </button>
        </div>

        {/* Filter Options */}
        {searchResults.length > 0 && (
          <div className="flex items-center space-x-4 mb-4">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="all">All Types</option>
              <option value="text">Text</option>
              <option value="markdown">Markdown</option>
              <option value="pdf">PDF</option>
            </select>
            <span className="text-sm text-gray-600">
              {filteredResults.length} result{filteredResults.length !== 1 ? 's' : ''}
            </span>
          </div>
        )}

        {/* Search Results */}
        <AnimatePresence>
          {filteredResults.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              {filteredResults.map((result, index) => (
                <motion.div
                  key={result.chunk_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getContentTypeIcon(result.metadata?.content_type)}
                      <span className="font-medium text-gray-900">
                        {result.document_filename}
                      </span>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        Score: {(result.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <button
                      onClick={() => toggleChunkExpansion(result.chunk_id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedChunks.has(result.chunk_id) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    {result.content.substring(0, 200)}
                    {result.content.length > 200 && '...'}
                  </div>
                  
                  <AnimatePresence>
                    {expandedChunks.has(result.chunk_id) && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 pt-3 border-t border-gray-200"
                      >
                        <div className="bg-gray-50 rounded p-3 text-sm">
                          <p className="whitespace-pre-wrap">{result.content}</p>
                        </div>
                        
                        {result.metadata && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {result.metadata.section_header && (
                              <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                                Section: {result.metadata.section_header}
                              </span>
                            )}
                            {result.metadata.chunk_index !== undefined && (
                              <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                                Chunk: {result.metadata.chunk_index + 1}
                              </span>
                            )}
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {searchQuery && searchResults.length === 0 && !isSearching && (
          <div className="text-center py-8 text-gray-500">
            <Search className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No results found for "{searchQuery}"</p>
            <p className="text-sm">Try different keywords or upload more documents</p>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Processed Documents</h3>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            <span className="ml-3 text-gray-600">Loading documents...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No documents uploaded yet</p>
            <p className="text-sm">Upload documents to start building your knowledge base</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc, index) => (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedDocument(doc)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getContentTypeIcon(doc.content_type)}
                    <div>
                      <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Hash className="h-3 w-3 mr-1" />
                          {doc.chunk_count} chunks
                        </span>
                        <span className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatDate(doc.created_at)}
                        </span>
                        {doc.metadata.estimated_reading_time && (
                          <span>{doc.metadata.estimated_reading_time.toFixed(1)} min read</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      doc.processing_status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {doc.processing_status}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        // Handle view action
                      }}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                <div className="mt-2 grid grid-cols-3 gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">{doc.metadata.word_count.toLocaleString()}</span> words
                  </div>
                  <div>
                    <span className="font-medium">{doc.metadata.character_count.toLocaleString()}</span> characters
                  </div>
                  <div>
                    <span className="font-medium">{doc.content_type}</span> format
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
} 