import type { FC } from 'react'
import type { RegistryApiNodeType } from './types'
import type { NodeProps } from '@/app/components/workflow/types'
import * as React from 'react'
import ReadonlyInputWithSelectVar from '../_base/components/readonly-input-with-select-var'

const Node: FC<NodeProps<RegistryApiNodeType>> = ({
  id,
  data,
}) => {
  const displayName = data.registry_display_name || data.title
  const url = data.registry_api_config?.gateway_url || data.url
  const method = data.method

  if (!url)
    return null

  return (
    <div className="mb-1 space-y-1 px-3 py-1">
      <div className="truncate text-xs font-medium text-text-tertiary">{displayName}</div>
      <div className="flex items-center justify-start rounded-md bg-workflow-block-parma-bg p-1">
        <div className="flex h-4 shrink-0 items-center rounded-sm bg-components-badge-white-to-dark px-1 text-xs font-semibold text-text-secondary uppercase">{method}</div>
        <div className="w-0 grow pt-1 pl-1">
          <ReadonlyInputWithSelectVar
            className="text-text-secondary"
            value={url}
            nodeId={id}
          />
        </div>
      </div>
    </div>
  )
}

export default React.memo(Node)
