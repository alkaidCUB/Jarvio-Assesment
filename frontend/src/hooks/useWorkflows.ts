import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { Workflow, WorkflowRun } from '@/types'

export const useWorkflows = () => {
  return useQuery({
    queryKey: ['workflows'],
    queryFn: async () => {
      const response = await api.get('/workflows/')
      return response.data as Workflow[]
    },
  })
}

export const useWorkflow = (workflowId: string) => {
  return useQuery({
    queryKey: ['workflows', workflowId],
    queryFn: async () => {
      const response = await api.get(`/workflows/${workflowId}`)
      return response.data as Workflow
    },
    enabled: !!workflowId,
  })
}

export const useCreateWorkflow = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (workflow: { name: string; description?: string; flow_data: any }) => {
      const response = await api.post('/workflows/', workflow)
      return response.data as Workflow
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
    },
  })
}

export const useUpdateWorkflow = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ 
      workflowId, 
      workflow 
    }: { 
      workflowId: string
      workflow: { name?: string; description?: string; flow_data?: any }
    }) => {
      const response = await api.put(`/workflows/${workflowId}`, workflow)
      return response.data as Workflow
    },
    onSuccess: (_, { workflowId }) => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      queryClient.invalidateQueries({ queryKey: ['workflows', workflowId] })
    },
  })
}

export const useRunWorkflow = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (workflowId: string) => {
      const response = await api.post(`/workflows/${workflowId}/run`)
      return response.data as WorkflowRun
    },
    onSuccess: (_, workflowId) => {
      queryClient.invalidateQueries({ queryKey: ['workflow-runs', workflowId] })
    },
  })
}

export const useWorkflowRuns = (workflowId: string) => {
  return useQuery({
    queryKey: ['workflow-runs', workflowId],
    queryFn: async () => {
      const response = await api.get(`/workflows/${workflowId}/runs`)
      return response.data as WorkflowRun[]
    },
    enabled: !!workflowId,
  })
}