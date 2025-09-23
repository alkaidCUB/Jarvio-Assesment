import { Edge, Node } from 'reactflow'

export interface NodeDataFlow {
  hasInput: boolean
  inputType?: string
  inputDescription?: string
  outputType: string
  outputDescription: string
}

export const getNodeDataFlow = (nodeId: string, nodeType: string, edges: Edge[], nodes: Node[]): NodeDataFlow => {
  // Find incoming edge
  const incomingEdge = edges.find(edge => edge.target === nodeId)
  const sourceNode = incomingEdge ? nodes.find(node => node.id === incomingEdge.source) : null

  // Determine input type based on source node
  let inputType: string | undefined
  let inputDescription: string | undefined
  
  if (sourceNode) {
    switch (sourceNode.type) {
      case 'get_bestselling_asins':
        inputType = 'asin_list'
        inputDescription = 'List of ASINs from best selling products'
        break
      case 'get_asin_by_index':
        inputType = 'single_asin'
        inputDescription = 'Single ASIN selected from list'
        break
      case 'get_asin_details':
        inputType = 'product_details'
        inputDescription = 'Product details with title, description, etc.'
        break
    }
  }

  // Determine output type and description based on current node type
  let outputType: string
  let outputDescription: string

  switch (nodeType) {
    case 'get_bestselling_asins':
      outputType = 'asin_list'
      outputDescription = 'List of top selling ASINs'
      break
    case 'get_asin_by_index':
      outputType = 'single_asin'
      outputDescription = 'Single ASIN at specified index'
      break
    case 'get_asin_details':
      outputType = 'product_details'
      outputDescription = 'Complete product information'
      break
    default:
      outputType = 'unknown'
      outputDescription = 'Unknown output type'
  }

  return {
    hasInput: !!incomingEdge,
    inputType,
    inputDescription,
    outputType,
    outputDescription
  }
}

export const isValidConnection = (sourceNodeType: string, targetNodeType: string): boolean => {
  const validConnections: Record<string, string[]> = {
    'get_bestselling_asins': ['get_asin_by_index'],
    'get_asin_by_index': ['get_asin_details'],
    'get_asin_details': []  // Terminal node
  }

  const validTargets = validConnections[sourceNodeType]
  return validTargets ? validTargets.includes(targetNodeType) : false
}