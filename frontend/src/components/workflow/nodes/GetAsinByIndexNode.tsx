import React, { useState, useCallback, useEffect } from 'react'
import { Handle, Position, NodeProps, useReactFlow, useNodes, useEdges } from 'reactflow'
import { ListOrdered, X } from 'lucide-react'
import { getNodeDataFlow } from '@/utils/workflowUtils'

interface GetAsinByIndexNodeData {
  label: string
  index?: number
}

export const GetAsinByIndexNode: React.FC<NodeProps<GetAsinByIndexNodeData>> = ({
  id,
  data,
  isConnectable,
}) => {
  const [index, setIndex] = useState(data.index || 0)
  const { deleteElements, setNodes } = useReactFlow()
  const nodes = useNodes()
  const edges = useEdges()
  
  const dataFlow = getNodeDataFlow(id, 'get_asin_by_index', edges, nodes)

  const onDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  // Sync local state when data prop changes
  useEffect(() => {
    setIndex(data.index || 0)
  }, [data.index])

  const handleIndexChange = useCallback((newIndex: number) => {
    setIndex(newIndex)
    // Update the node data in ReactFlow
    setNodes((nodes) =>
      nodes.map((node) =>
        node.id === id
          ? {
              ...node,
              data: {
                ...node.data,
                index: newIndex,
              },
            }
          : node
      )
    )
  }, [id, setNodes])

  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-green-500 relative">
      <button
        onClick={onDelete}
        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
        title="Delete node"
      >
        <X className="w-3 h-3" />
      </button>
      
      <div className="flex items-center">
        <div className="rounded-full w-12 h-12 flex justify-center items-center bg-green-100">
          <ListOrdered className="w-6 h-6 text-green-600" />
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold text-green-600">Get ASIN by Index</div>
          <div className="text-gray-500">Select item from list</div>
        </div>
      </div>
      
      <div className="mt-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Index
        </label>
        <input
          type="number"
          value={index}
          onChange={(e) => handleIndexChange(Number(e.target.value))}
          className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
          min="0"
        />
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 space-y-1">
          {dataFlow.hasInput ? (
            <div>
              <span className="font-medium text-green-600">Input:</span> {dataFlow.inputDescription}
            </div>
          ) : (
            <div className="text-orange-600">
              <span className="font-medium">⚠️ Input:</span> Connect from "Get Best Selling ASINs"
            </div>
          )}
          <div>
            <span className="font-medium">Output:</span> Single ASIN at index {index}
          </div>
        </div>
      </div>

      <Handle
        type="target"
        position={Position.Left}
        id="input"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-green-500"
      />
      
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-green-500"
      />
    </div>
  )
}