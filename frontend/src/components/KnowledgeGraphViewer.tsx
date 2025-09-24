'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Network,
  Share2,
  Search,
  Filter,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Download,
  Eye,
  Brain,
  Users,
  Building,
  MapPin,
  Cpu,
  Settings,
  FileText,
  Bot,
  GitBranch,
  Lightbulb,
  TrendingUp,
  BarChart3
} from 'lucide-react'
import toast from 'react-hot-toast'

interface Entity {
  id: string
  name: string
  type: string
  confidence: number
  attributes: Record<string, any>
  created_at: string
}

interface Relationship {
  id: string
  source: string
  target: string
  type: string
  weight: number
  confidence: number
}

interface KnowledgeGraph {
  entities: Entity[]
  relationships: Relationship[]
  statistics: {
    total_entities: number
    total_relationships: number
    entity_types: Record<string, number>
    relationship_types: Record<string, number>
    graph_density: number
  }
}

interface GraphNode {
  id: string
  name: string
  type: string
  x: number
  y: number
  size: number
  color: string
  confidence: number
}

interface GraphEdge {
  source: string
  target: string
  type: string
  weight: number
  color: string
}

export function KnowledgeGraphViewer() {
  const [knowledgeGraph, setKnowledgeGraph] = useState<KnowledgeGraph | null>(null)
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [isLoading, setIsLoading] = useState(false)
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([])
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([])
  const [viewMode, setViewMode] = useState<'overview' | 'detailed' | 'clusters'>('overview')
  const [zoomLevel, setZoomLevel] = useState(1)
  
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()

  const entityTypeIcons = {
    concept: Brain,
    person: Users,
    organization: Building,
    location: MapPin,
    technology: Cpu,
    process: Settings,
    document: FileText,
    agent: Bot,
    workflow: GitBranch,
    reasoning_chain: Lightbulb
  }

  const entityTypeColors = {
    concept: '#3B82F6',      // Blue
    person: '#10B981',       // Green
    organization: '#8B5CF6', // Purple
    location: '#F59E0B',     // Amber
    technology: '#EF4444',   // Red
    process: '#06B6D4',      // Cyan
    document: '#84CC16',     // Lime
    agent: '#EC4899',        // Pink
    workflow: '#6366F1',     // Indigo
    reasoning_chain: '#F97316' // Orange
  }

  const loadKnowledgeGraph = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/knowledge/graph', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setKnowledgeGraph(data)
        generateGraphVisualization(data)
      }
    } catch (error) {
      console.error('Failed to load knowledge graph:', error)
      toast.error('Failed to load knowledge graph')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const generateGraphVisualization = (graph: KnowledgeGraph) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2

    // Create nodes with physics-based positioning
    const nodes: GraphNode[] = graph.entities.map((entity, index) => {
      const angle = (index / graph.entities.length) * 2 * Math.PI
      const radius = Math.min(width, height) * 0.3
      
      return {
        id: entity.id,
        name: entity.name,
        type: entity.type,
        x: centerX + Math.cos(angle) * radius + (Math.random() - 0.5) * 100,
        y: centerY + Math.sin(angle) * radius + (Math.random() - 0.5) * 100,
        size: Math.max(8, Math.min(20, entity.confidence * 20)),
        color: entityTypeColors[entity.type as keyof typeof entityTypeColors] || '#6B7280',
        confidence: entity.confidence
      }
    })

    // Create edges
    const edges: GraphEdge[] = graph.relationships.map(rel => ({
      source: rel.source,
      target: rel.target,
      type: rel.type,
      weight: rel.weight,
      color: `rgba(107, 114, 128, ${Math.max(0.1, rel.confidence)})`
    }))

    setGraphNodes(nodes)
    setGraphEdges(edges)
    
    // Start animation loop
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
    animateGraph()
  }

  const animateGraph = () => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw edges
    ctx.strokeStyle = '#E5E7EB'
    ctx.lineWidth = 1
    
    graphEdges.forEach(edge => {
      const sourceNode = graphNodes.find(n => n.id === edge.source)
      const targetNode = graphNodes.find(n => n.id === edge.target)
      
      if (sourceNode && targetNode) {
        ctx.beginPath()
        ctx.moveTo(sourceNode.x, sourceNode.y)
        ctx.lineTo(targetNode.x, targetNode.y)
        ctx.strokeStyle = edge.color
        ctx.lineWidth = Math.max(1, edge.weight * 2)
        ctx.stroke()
      }
    })

    // Draw nodes
    graphNodes.forEach(node => {
      if (filterType === 'all' || node.type === filterType) {
        // Node circle
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.size * zoomLevel, 0, 2 * Math.PI)
        ctx.fillStyle = node.color
        ctx.fill()
        
        // Node border
        ctx.strokeStyle = selectedEntity?.id === node.id ? '#F59E0B' : '#FFFFFF'
        ctx.lineWidth = selectedEntity?.id === node.id ? 3 : 1
        ctx.stroke()
        
        // Node label
        if (zoomLevel > 0.5) {
          ctx.fillStyle = '#1F2937'
          ctx.font = `${Math.max(10, 12 * zoomLevel)}px sans-serif`
          ctx.textAlign = 'center'
          ctx.fillText(
            node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name,
            node.x,
            node.y + node.size * zoomLevel + 15
          )
        }
      }
    })

    animationRef.current = requestAnimationFrame(animateGraph)
  }

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Find clicked node
    const clickedNode = graphNodes.find(node => {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
      return distance <= node.size * zoomLevel
    })

    if (clickedNode && knowledgeGraph) {
      const entity = knowledgeGraph.entities.find(e => e.id === clickedNode.id)
      setSelectedEntity(entity || null)
    } else {
      setSelectedEntity(null)
    }
  }

  const searchEntities = async () => {
    if (!searchQuery.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/knowledge/search?query=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const results = await response.json()
        // Highlight search results
        if (results.results.length > 0) {
          const firstResult = results.results[0]
          const entity = knowledgeGraph?.entities.find(e => e.id === firstResult.entity.id)
          setSelectedEntity(entity || null)
          toast.success(`Found ${results.total_matches} matching entities`)
        } else {
          toast.info('No matching entities found')
        }
      }
    } catch (error) {
      console.error('Search failed:', error)
      toast.error('Search failed')
    } finally {
      setIsLoading(false)
    }
  }

  const exportGraph = async () => {
    try {
      const response = await fetch('http://localhost:8000/knowledge/export', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `knowledge_graph_${new Date().toISOString().split('T')[0]}.json`
        a.click()
        URL.revokeObjectURL(url)
        toast.success('Knowledge graph exported successfully')
      }
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed')
    }
  }

  const resetView = () => {
    setZoomLevel(1)
    if (knowledgeGraph) {
      generateGraphVisualization(knowledgeGraph)
    }
  }

  useEffect(() => {
    loadKnowledgeGraph()
    
    // Cleanup animation on unmount
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [loadKnowledgeGraph])

  useEffect(() => {
    const canvas = canvasRef.current
    if (canvas) {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
    }
  }, [])

  const entityTypes = knowledgeGraph?.statistics.entity_types || {}
  const totalEntities = knowledgeGraph?.statistics.total_entities || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Network className="h-6 w-6 mr-2 text-primary-600" />
          Knowledge Graph
        </h2>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={resetView}
            className="btn-secondary text-sm"
            title="Reset View"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          
          <button
            onClick={exportGraph}
            className="btn-secondary text-sm"
            title="Export Graph"
          >
            <Download className="h-4 w-4" />
          </button>
          
          <button
            onClick={loadKnowledgeGraph}
            disabled={isLoading}
            className="btn-primary text-sm"
          >
            <TrendingUp className="h-4 w-4 mr-1" />
            Refresh
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchEntities()}
                placeholder="Search entities..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-full"
              />
            </div>
          </div>
          
          {/* Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="all">All Types</option>
              {Object.keys(entityTypes).map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)} ({entityTypes[type]})
                </option>
              ))}
            </select>
          </div>
          
          {/* View Mode */}
          <div className="flex items-center space-x-1">
            {['overview', 'detailed', 'clusters'].map(mode => (
              <button
                key={mode}
                onClick={() => setViewMode(mode as any)}
                className={`px-3 py-1 text-sm rounded ${
                  viewMode === mode 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          
          {/* Zoom Controls */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setZoomLevel(prev => Math.max(0.5, prev - 0.1))}
              className="p-1 text-gray-500 hover:text-gray-700"
              title="Zoom Out"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <span className="text-sm text-gray-600 min-w-12 text-center">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => setZoomLevel(prev => Math.min(2, prev + 0.1))}
              className="p-1 text-gray-500 hover:text-gray-700"
              title="Zoom In"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Graph Visualization */}
        <div className="lg:col-span-3">
          <div className="card p-0 relative">
            {isLoading && (
              <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
              </div>
            )}
            
            <canvas
              ref={canvasRef}
              onClick={handleCanvasClick}
              className="w-full h-96 cursor-pointer"
              style={{ height: '500px' }}
            />
            
            {totalEntities === 0 && !isLoading && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Network className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Knowledge Graph Yet</h3>
                  <p className="text-gray-600 mb-4">Start by uploading documents or having conversations</p>
                  <button
                    onClick={loadKnowledgeGraph}
                    className="btn-primary"
                  >
                    <Brain className="h-4 w-4 mr-2" />
                    Build Knowledge Graph
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Statistics */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Graph Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Entities:</span>
                <span className="text-sm font-medium text-gray-900">
                  {knowledgeGraph?.statistics.total_entities || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Relationships:</span>
                <span className="text-sm font-medium text-gray-900">
                  {knowledgeGraph?.statistics.total_relationships || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Density:</span>
                <span className="text-sm font-medium text-gray-900">
                  {((knowledgeGraph?.statistics.graph_density || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Entity Types */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Entity Types</h3>
            <div className="space-y-2">
              {Object.entries(entityTypes).map(([type, count]) => {
                const IconComponent = entityTypeIcons[type as keyof typeof entityTypeIcons] || Eye
                const color = entityTypeColors[type as keyof typeof entityTypeColors] || '#6B7280'
                
                return (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: color }}
                      />
                      <IconComponent className="h-4 w-4 text-gray-500" />
                      <span className="text-sm text-gray-700">
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Selected Entity */}
          {selectedEntity && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Selected Entity</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900">{selectedEntity.name}</h4>
                  <p className="text-sm text-gray-600">{selectedEntity.type}</p>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Confidence:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${selectedEntity.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {Math.round(selectedEntity.confidence * 100)}%
                  </span>
                </div>
                
                {Object.keys(selectedEntity.attributes).length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Attributes</h5>
                    <div className="space-y-1">
                      {Object.entries(selectedEntity.attributes).map(([key, value]) => (
                        <div key={key} className="text-xs">
                          <span className="text-gray-600">{key}:</span>
                          <span className="text-gray-900 ml-1">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-gray-500">
                  Created: {new Date(selectedEntity.created_at).toLocaleDateString()}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
} 