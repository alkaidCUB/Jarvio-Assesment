import React, { useState, useCallback, useEffect } from 'react'
import { Handle, Position, NodeProps, useReactFlow } from 'reactflow'
import { ShoppingCart, X } from 'lucide-react'

interface GetBestSellingAsinsNodeData {
  label: string
  topCount?: number
}

export const GetBestSellingAsinsNode: React.FC<NodeProps<GetBestSellingAsinsNodeData>> = ({
  id,
  data,
  isConnectable,
}) => {
  const [topCount, setTopCount] = useState(data.topCount || 10)
  const { deleteElements, setNodes } = useReactFlow()

  const onDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  // Sync local state when data prop changes
  useEffect(() => {
    setTopCount(data.topCount || 10)
  }, [data.topCount])

  const handleTopCountChange = useCallback((newTopCount: number) => {
    setTopCount(newTopCount)
    // Update the node data in ReactFlow
    setNodes((nodes) =>
      nodes.map((node) =>
        node.id === id
          ? {
              ...node,
              data: {
                ...node.data,
                topCount: newTopCount,
              },
            }
          : node
      )
    )
  }, [id, setNodes])

  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-blue-500 relative">
      <button
        onClick={onDelete}
        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
        title="Delete node"
      >
        <X className="w-3 h-3" />
      </button>
      
      <div className="flex items-center">
        <div className="rounded-full w-12 h-12 flex justify-center items-center bg-blue-100">
          <ShoppingCart className="w-6 h-6 text-blue-600" />
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold text-blue-600">Get Best Selling ASINs</div>
          <div className="text-gray-500">Fetch top selling products</div>
        </div>
      </div>
      
      <div className="mt-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Top Count
        </label>
        <input
          type="number"
          value={topCount}
          onChange={(e) => handleTopCountChange(Number(e.target.value))}
          className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
          min="1"
          max="100"
        />
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600">
          <div className="mb-1">
            <span className="font-medium">Output:</span> List of ASINs
          </div>
          <div className="text-gray-500">
            Returns top {topCount} best selling product ASINs
          </div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        id="output"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-blue-500"
      />
    </div>
  )
}