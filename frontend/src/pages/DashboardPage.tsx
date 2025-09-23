import React from 'react'
import { Link } from 'react-router-dom'
import { Plus, Workflow, Package } from 'lucide-react'
import { useWorkflows } from '@/hooks/useWorkflows'
import { useAuthStore } from '@/stores/authStore'

export const DashboardPage: React.FC = () => {
  const { data: workflows, isLoading } = useWorkflows()
  const { user, logout } = useAuthStore()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Workflow className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-semibold text-gray-900">
                Workflow Builder
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/my-products"
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                <Package className="h-4 w-4 mr-1" />
                My Products
              </Link>
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-semibold text-gray-900">My Workflows</h1>
            <Link
              to="/workflows/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Workflow
            </Link>
          </div>

          {workflows && workflows.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {workflows.map((workflow) => (
                <Link
                  key={workflow.id}
                  to={`/workflows/${workflow.id}`}
                  className="block p-6 bg-white rounded-lg border border-gray-200 hover:bg-gray-50"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {workflow.name}
                  </h3>
                  {workflow.description && (
                    <p className="text-gray-600 mb-4">{workflow.description}</p>
                  )}
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>Nodes: {workflow.flow_data.nodes.length}</span>
                    <span>{new Date(workflow.updated_at).toLocaleDateString()}</span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Workflow className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold text-gray-900">No workflows</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating a new workflow.
              </p>
              <div className="mt-6">
                <Link
                  to="/workflows/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New Workflow
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}