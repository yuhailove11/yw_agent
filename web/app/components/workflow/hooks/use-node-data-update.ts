import type { SyncCallback } from './use-nodes-sync-draft'
import { isEqual } from 'es-toolkit/predicate'
import { produce } from 'immer'
import { useCallback } from 'react'
import { useStoreApi } from 'reactflow'
import { useNodesSyncDraft } from './use-nodes-sync-draft'
import { useNodesReadOnly } from './use-workflow'

type NodeDataUpdatePayload = {
  id: string
  data: Record<string, any>
}

export const useNodeDataUpdate = () => {
  const store = useStoreApi()
  const { handleSyncWorkflowDraft } = useNodesSyncDraft()
  const { getNodesReadOnly } = useNodesReadOnly()

  const handleNodeDataUpdate = useCallback(({ id, data }: NodeDataUpdatePayload) => {
    const {
      getNodes,
      setNodes,
    } = store.getState()
    const nodes = getNodes()
    const currentNode = nodes.find(node => node.id === id)
    if (!currentNode)
      return false
    const nextData = { ...currentNode.data, ...data }
    if (isEqual(currentNode.data, nextData))
      return false

    const newNodes = produce(nodes, (draft) => {
      const targetNode = draft.find(node => node.id === id)
      if (targetNode)
        targetNode.data = nextData
    })
    setNodes(newNodes)
    return true
  }, [store])

  const handleNodeDataUpdateWithSyncDraft = useCallback((
    payload: NodeDataUpdatePayload,
    options?: {
      sync?: boolean
      notRefreshWhenSyncError?: boolean
      callback?: SyncCallback
    },
  ) => {
    if (getNodesReadOnly())
      return

    const changed = handleNodeDataUpdate(payload)
    if (!changed)
      return
    handleSyncWorkflowDraft(options?.sync, options?.notRefreshWhenSyncError, options?.callback)
  }, [handleSyncWorkflowDraft, handleNodeDataUpdate, getNodesReadOnly])

  return {
    handleNodeDataUpdate,
    handleNodeDataUpdateWithSyncDraft,
  }
}
