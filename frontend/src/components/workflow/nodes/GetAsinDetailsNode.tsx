import React from 'react'
import { Handle, Position, NodeProps, useReactFlow, useNodes, useEdges } from 'reactflow'
import { FileText, X } from 'lucide-react'
import { getNodeDataFlow } from '@/utils/workflowUtils'

interface GetAsinDetailsNodeData {
  label: string
}

export const GetAsinDetailsNode: React.FC<NodeProps<GetAsinDetailsNodeData>> = ({
  id,
  isConnectable,
}) => {
  const { deleteElements } = useReactFlow()
  const nodes = useNodes()
  const edges = useEdges()
  
  const dataFlow = getNodeDataFlow(id, 'get_asin_details', edges, nodes)

  const onDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-purple-500 relative">
      <button
        onClick={onDelete}
        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
        title="Delete node"
      >
        <X className="w-3 h-3" />
      </button>
      
      <div className="flex items-center">
        <div className="rounded-full w-12 h-12 flex justify-center items-center bg-purple-100">
          <FileText className="w-6 h-6 text-purple-600" />
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold text-purple-600">Get ASIN Details</div>
          <div className="text-gray-500">Fetch product details</div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 space-y-1">
          {dataFlow.hasInput ? (
            <div>
              <span className="font-medium text-green-600">Input:</span> {dataFlow.inputDescription}
            </div>
          ) : (
            <div className="text-orange-600">
              <span className="font-medium">⚠️ Input:</span> Connect from "Get ASIN by Index"
            </div>
          )}
          <div>
            <span className="font-medium">Output:</span> Complete product details
          </div>
        </div>
      </div>

      <Handle
        type="target"
        position={Position.Left}
        id="input"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-purple-500"
      />
    </div>
  )
}