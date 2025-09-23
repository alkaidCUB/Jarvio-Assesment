import React, { useCallback, useMemo, useEffect } from 'react'
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  Connection,
  NodeTypes,
  ConnectionMode,
} from 'reactflow'
import 'reactflow/dist/style.css'

import { GetBestSellingAsinsNode } from './nodes/GetBestSellingAsinsNode'
import { GetAsinByIndexNode } from './nodes/GetAsinByIndexNode'
import { GetAsinDetailsNode } from './nodes/GetAsinDetailsNode'
import { isValidConnection as isValidWorkflowConnection } from '@/utils/workflowUtils'
import type { WorkflowNode, WorkflowEdge } from '@/types'

interface WorkflowCanvasProps {
  initialNodes?: WorkflowNode[]
  initialEdges?: WorkflowEdge[]
  onNodesChange?: (nodes: WorkflowNode[]) => void
  onEdgesChange?: (edges: WorkflowEdge[]) => void
  readonly?: boolean
}

const nodeTypes: NodeTypes = {
  get_bestselling_asins: GetBestSellingAsinsNode,
  get_asin_by_index: GetAsinByIndexNode,
  get_asin_details: GetAsinDetailsNode,
}

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({
  initialNodes = [],
  initialEdges = [],
  onNodesChange,
  onEdgesChange,
  readonly = false,
}) => {
  const [nodes, setNodes, onNodesStateChange] = useNodesState(initialNodes as Node[])
  const [edges, setEdges, onEdgesStateChange] = useEdgesState(initialEdges as Edge[])

  // Sync nodes when initialNodes prop changes
  useEffect(() => {
    setNodes(initialNodes as Node[])
  }, [initialNodes, setNodes])

  // Sync edges when initialEdges prop changes
  useEffect(() => {
    setEdges(initialEdges as Edge[])
  }, [initialEdges, setEdges])

  const onConnect = useCallback(
    (params: Connection) => {
      if (!readonly) {
        const newEdge = addEdge({
          ...params,
          type: 'default',
          animated: true,
          style: { stroke: '#3b82f6', strokeWidth: 2 },
        }, edges)
        setEdges(newEdge)
        onEdgesChange?.(newEdge as WorkflowEdge[])
      }
    },
    [edges, readonly, onEdgesChange, setEdges]
  )

  const handleNodesChange = useCallback(
    (changes: any) => {
      onNodesStateChange(changes)
      if (!readonly && onNodesChange) {
        setTimeout(() => {
          setNodes((currentNodes) => {
            onNodesChange(currentNodes as WorkflowNode[])
            return currentNodes
          })
        }, 0)
      }
    },
    [onNodesStateChange, readonly, onNodesChange, setNodes]
  )

  const handleEdgesChange = useCallback(
    (changes: any) => {
      onEdgesStateChange(changes)
      if (!readonly && onEdgesChange) {
        setTimeout(() => {
          setEdges((currentEdges) => {
            onEdgesChange(currentEdges as WorkflowEdge[])
            return currentEdges
          })
        }, 0)
      }
    },
    [onEdgesStateChange, readonly, onEdgesChange, setEdges]
  )

  const proOptions = useMemo(() => ({ hideAttribution: true }), [])

  const isValidConnection = useCallback((connection: Connection) => {
    // Prevent self-connections
    if (connection.source === connection.target) {
      return false
    }
    
    // Only allow connections from source handles to target handles
    if (connection.sourceHandle !== 'output' || connection.targetHandle !== 'input') {
      return false
    }

    // Find source and target node types for workflow validation
    const sourceNode = nodes.find(n => n.id === connection.source)
    const targetNode = nodes.find(n => n.id === connection.target)

    if (!sourceNode || !targetNode) {
      return false
    }

    // Use workflow-specific validation
    return isValidWorkflowConnection(sourceNode.type || '', targetNode.type || '')
  }, [nodes])

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        isValidConnection={isValidConnection}
        nodeTypes={nodeTypes}
        proOptions={proOptions}
        fitView
        snapToGrid
        snapGrid={[15, 15]}
        connectionMode={ConnectionMode.Loose}
        deleteKeyCode="Delete"
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  )
}