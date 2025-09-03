'use client'

import React, { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  error?: string
}

export function DocumentUpload() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }
  }, [])

  const handleFiles = async (fileList: File[]) => {
    const newFiles: UploadedFile[] = fileList.map(file => ({
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0
    }))

    setFiles(prev => [...prev, ...newFiles])

    // Process each file
    for (const file of fileList) {
      const fileId = newFiles.find(f => f.name === file.name)?.id
      if (!fileId) continue

      try {
        await uploadFile(file, fileId)
      } catch (error) {
        console.error('Upload error:', error)
        updateFileStatus(fileId, 'error', 0, 'Upload failed')
      }
    }
  }

  const uploadFile = async (file: File, fileId: string) => {
    // Simulate upload progress
    updateFileStatus(fileId, 'uploading', 25)
    
    try {
      // Read file content
      const content = await readFileContent(file)
      updateFileStatus(fileId, 'processing', 50)

      // Upload to backend
      const response = await fetch('http://localhost:8000/rag/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.name,
          content: content,
          content_type: getContentType(file.type)
        }),
      })

      updateFileStatus(fileId, 'processing', 75)

      const data = await response.json()

      if (data.status === 'success') {
        updateFileStatus(fileId, 'completed', 100)
        toast.success(`${file.name} uploaded successfully`)
      } else {
        updateFileStatus(fileId, 'error', 0, data.error || 'Upload failed')
        toast.error(`Failed to upload ${file.name}`)
      }
    } catch (error) {
      updateFileStatus(fileId, 'error', 0, 'Upload failed')
      toast.error(`Failed to upload ${file.name}`)
    }
  }

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target?.result as string)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  const getContentType = (mimeType: string): string => {
    if (mimeType.includes('pdf')) return 'pdf'
    if (mimeType.includes('markdown')) return 'markdown'
    return 'text'
  }

  const updateFileStatus = (fileId: string, status: UploadedFile['status'], progress: number, error?: string) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, status, progress, error }
        : file
    ))
  }

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId))
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <FileText className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Upload className="h-5 w-5 mr-2 text-primary-600" />
        Document Upload
      </h3>

      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragOver 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p className="text-sm text-gray-600 mb-2">
          Drag and drop files here, or{' '}
          <label className="text-primary-600 hover:text-primary-700 cursor-pointer">
            browse
            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              accept=".txt,.md,.pdf"
            />
          </label>
        </p>
        <p className="text-xs text-gray-500">
          Supports: TXT, Markdown, PDF
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Uploaded Files</h4>
          {files.map((file) => (
            <motion.div
              key={file.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3 flex-1">
                {getStatusIcon(file.status)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <div className="flex items-center space-x-2">
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                    {file.status === 'error' && file.error && (
                      <p className="text-xs text-red-500">• {file.error}</p>
                    )}
                  </div>
                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <div className="mt-1">
                      <div className="w-full bg-gray-200 rounded-full h-1">
                        <div 
                          className="bg-primary-600 h-1 rounded-full transition-all duration-300"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => removeFile(file.id)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
} 