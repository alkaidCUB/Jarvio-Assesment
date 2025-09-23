import React, { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, Save, Plus } from 'lucide-react'
import { WorkflowCanvas } from '@/components/workflow/WorkflowCanvas'
import { WorkflowResults } from '@/components/workflow/WorkflowResults'
import { 
  useWorkflow, 
  useCreateWorkflow, 
  useUpdateWorkflow, 
  useRunWorkflow, 
  useWorkflowRuns 
} from '@/hooks/useWorkflows'
import type { WorkflowNode, WorkflowEdge } from '@/types'

export const WorkflowEditorPage: React.FC = () => {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const isNewWorkflow = workflowId === 'new'

  const [workflowName, setWorkflowName] = useState('Untitled Workflow')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const [nodes, setNodes] = useState<WorkflowNode[]>([])
  const [edges, setEdges] = useState<WorkflowEdge[]>([])
  const [showResults, setShowResults] = useState(false)

  const { data: workflow, isLoading } = useWorkflow(workflowId!)
  const { data: runs } = useWorkflowRuns(workflowId!)
  
  const createWorkflowMutation = useCreateWorkflow()
  const updateWorkflowMutation = useUpdateWorkflow()
  const runWorkflowMutation = useRunWorkflow()

  React.useEffect(() => {
    if (workflow && !isNewWorkflow) {
      setWorkflowName(workflow.name)
      setWorkflowDescription(workflow.description || '')
      setNodes(workflow.flow_data.nodes || [])
      setEdges(workflow.flow_data.edges || [])
    }
  }, [workflow, isNewWorkflow])

  const handleSave = useCallback(async () => {
    const flowData = { nodes, edges }
    
    try {
      if (isNewWorkflow) {
        const newWorkflow = await createWorkflowMutation.mutateAsync({
          name: workflowName,
          description: workflowDescription,
          flow_data: flowData,
        })
        navigate(`/workflows/${newWorkflow.id}`)
      } else {
        await updateWorkflowMutation.mutateAsync({
          workflowId: workflowId!,
          workflow: {
            name: workflowName,
            description: workflowDescription,
            flow_data: flowData,
          },
        })
      }
    } catch (error) {
      console.error('Error saving workflow:', error)
    }
  }, [
    workflowName,
    workflowDescription,
    nodes,
    edges,
    isNewWorkflow,
    createWorkflowMutation,
    updateWorkflowMutation,
    workflowId,
    navigate,
  ])

  const handleRun = useCallback(async () => {
    if (isNewWorkflow) {
      alert('Please save the workflow first before running it.')
      return
    }

    try {
      await runWorkflowMutation.mutateAsync(workflowId!)
      setShowResults(true)
    } catch (error) {
      console.error('Error running workflow:', error)
    }
  }, [isNewWorkflow, runWorkflowMutation, workflowId])

  const addNode = useCallback((nodeType: string) => {
    const newNode: WorkflowNode = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType as any,
      position: { x: Math.random() * 400 + 100, y: Math.random() * 400 + 100 },
      data: {
        label: `${nodeType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
        ...(nodeType === 'get_bestselling_asins' && { topCount: 10 }),
        ...(nodeType === 'get_asin_by_index' && { index: 0 }),
      },
    }
    setNodes(prev => [...prev, newNode])
  }, [])

  if (!isNewWorkflow && isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading workflow...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 text-gray-500 hover:text-gray-700"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <input
                type="text"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                className="text-xl font-semibold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 px-2 py-1 rounded"
                placeholder="Workflow name"
              />
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowResults(!showResults)}
                className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                {showResults ? 'Hide Results' : 'Show Results'}
              </button>
              <button
                onClick={handleRun}
                disabled={runWorkflowMutation.isPending || isNewWorkflow}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
              >
                <Play className="h-4 w-4 mr-2" />
                Run Workflow
              </button>
              <button
                onClick={handleSave}
                disabled={createWorkflowMutation.isPending || updateWorkflowMutation.isPending}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                Save
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex">
        <div className="flex-1 relative">
          <div className="absolute top-4 left-4 z-10 bg-white rounded-lg shadow-sm border p-2">
            <div className="text-sm font-medium text-gray-700 mb-2">Add Nodes</div>
            <div className="space-y-2">
              <button
                onClick={() => addNode('get_bestselling_asins')}
                className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded"
              >
                <Plus className="h-4 w-4 inline mr-2" />
                Get Best Selling ASINs
              </button>
              <button
                onClick={() => addNode('get_asin_by_index')}
                className="w-full text-left px-3 py-2 text-sm text-green-600 hover:bg-green-50 rounded"
              >
                <Plus className="h-4 w-4 inline mr-2" />
                Get ASIN by Index
              </button>
              <button
                onClick={() => addNode('get_asin_details')}
                className="w-full text-left px-3 py-2 text-sm text-purple-600 hover:bg-purple-50 rounded"
              >
                <Plus className="h-4 w-4 inline mr-2" />
                Get ASIN Details
              </button>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs text-gray-500 space-y-1">
                <div>
                  🔗 <strong>Sequential Flow:</strong> Best Selling ASINs → Get by Index → ASIN Details
                </div>
                <div>
                  💡 <strong>Tips:</strong> Connect nodes to pass data between them. Delete with red X or Delete key.
                </div>
              </div>
            </div>
          </div>
          
          <WorkflowCanvas
            initialNodes={nodes}
            initialEdges={edges}
            onNodesChange={setNodes}
            onEdgesChange={setEdges}
          />
        </div>

        {showResults && (
          <div className="w-96 bg-white border-l border-gray-200 p-4 overflow-y-auto">
            <WorkflowResults runs={runs || []} />
          </div>
        )}
      </div>
    </div>
  )
}