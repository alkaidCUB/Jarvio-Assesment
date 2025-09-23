import React from 'react'
import { CheckCircle, XCircle, Clock } from 'lucide-react'
import type { WorkflowRun } from '@/types'

interface WorkflowResultsProps {
  runs: WorkflowRun[]
}

export const WorkflowResults: React.FC<WorkflowResultsProps> = ({ runs }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'running':
        return <Clock className="w-5 h-5 text-yellow-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const formatResults = (results: Record<string, any>) => {
    if (!results) return null

    return Object.entries(results).map(([nodeId, result]) => (
      <div key={nodeId} className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">{nodeId}</h4>
        <div className="bg-gray-50 p-3 rounded text-sm">
          <div className="mb-1">
            <span className="font-medium">Type:</span> {result.type}
          </div>
          {result.type === 'asin_list' && (
            <div>
              <span className="font-medium">ASINs ({result.count}):</span>
              <ul className="list-disc list-inside mt-1">
                {result.value.map((asin: string, index: number) => (
                  <li key={index} className="text-xs">{asin}</li>
                ))}
              </ul>
            </div>
          )}
          {result.type === 'single_asin' && (
            <div>
              <span className="font-medium">ASIN:</span> {result.value}
            </div>
          )}
          {result.type === 'product_details' && (
            <div>
              <div><span className="font-medium">ASIN:</span> {result.value.asin}</div>
              <div><span className="font-medium">Title:</span> {result.value.title}</div>
              {result.value.description && (
                <div><span className="font-medium">Description:</span> {result.value.description}</div>
              )}
              {result.value.bullet_points && (
                <div>
                  <span className="font-medium">Bullet Points:</span>
                  <ul className="list-disc list-inside mt-1">
                    {result.value.bullet_points.map((point: string, index: number) => (
                      <li key={index} className="text-xs">{point}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    ))
  }

  if (runs.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">
        No workflow runs yet. Click "Run Workflow" to execute your workflow.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Workflow Runs</h3>
      {runs.map((run) => (
        <div key={run.id} className="border rounded-lg p-4 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              {getStatusIcon(run.status)}
              <span className="font-medium capitalize">{run.status}</span>
            </div>
            <div className="text-sm text-gray-500">
              {new Date(run.started_at).toLocaleString()}
            </div>
          </div>
          
          {run.error_message && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded">
              <span className="text-red-800">{run.error_message}</span>
            </div>
          )}
          
          {run.results && (
            <div>
              <h4 className="font-semibold mb-2">Results:</h4>
              {formatResults(run.results)}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}