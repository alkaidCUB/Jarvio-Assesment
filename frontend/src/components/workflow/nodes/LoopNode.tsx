import React, { useCallback } from 'react'
import { Handle, Position, NodeProps, useReactFlow } from 'reactflow'
import { RotateCw, X } from 'lucide-react'

interface LoopNodeData {
  label: string
}

export const LoopNode: React.FC<NodeProps<LoopNodeData>> = ({
  id,
  data,
  isConnectable,
}) => {
  const { deleteElements } = useReactFlow()

  const onDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-orange-500 relative">
      <button
        onClick={onDelete}
        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
        title="Delete node"
      >
        <X className="w-3 h-3" />
      </button>
      
      <div className="flex items-center">
        <div className="rounded-full w-12 h-12 flex justify-center items-center bg-orange-100">
          <RotateCw className="w-6 h-6 text-orange-600" />
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold text-orange-600">Loop</div>
          <div className="text-gray-500">Split array for processing</div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 space-y-1">
          <div>
            <span className="font-medium text-orange-600">Input:</span> List of ASINs
          </div>
          <div>
            <span className="font-medium">Output:</span> Individual items for processing
          </div>
          <div className="text-gray-500">
            Splits array input into individual items for batch processing
          </div>
        </div>
      </div>

      <Handle
        type="target"
        position={Position.Left}
        id="input"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-orange-500"
      />
      
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-orange-500"
      />
    </div>
  )
}
