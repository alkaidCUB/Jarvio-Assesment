import React, { useCallback } from 'react'
import { Handle, Position, NodeProps, useReactFlow } from 'reactflow'
import { Merge, X } from 'lucide-react'

interface MergeNodeData {
  label: string
}

export const MergeNode: React.FC<NodeProps<MergeNodeData>> = ({
  id,
  data,
  isConnectable,
}) => {
  const { deleteElements } = useReactFlow()

  const onDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

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
          <Merge className="w-6 h-6 text-green-600" />
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold text-green-600">Merge</div>
          <div className="text-gray-500">Collect results into table</div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 space-y-1">
          <div>
            <span className="font-medium text-green-600">Input:</span> Individual processed items
          </div>
          <div>
            <span className="font-medium">Output:</span> Product details table
          </div>
          <div className="text-gray-500">
            Collects all individual results into a consolidated table
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
