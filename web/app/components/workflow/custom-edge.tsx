import type { EdgeProps } from 'reactflow'
import type {
  Edge,
  OnSelectBlock,
} from './types'
import { intersection } from 'es-toolkit/array'
import {
  memo,
  useCallback,
  useMemo,
  useState,
} from 'react'
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  Position,
} from 'reactflow'
import { ErrorHandleTypeEnum } from '@/app/components/workflow/nodes/_base/components/error-handle/types'
import { cn } from '@/utils/classnames'
import BlockSelector from './block-selector'
import { ITERATION_CHILDREN_Z_INDEX, LOOP_CHILDREN_Z_INDEX } from './constants'
import CustomEdgeLinearGradientRender from './custom-edge-linear-gradient-render'
import {
  useAvailableBlocks,
  useNodesInteractions,
} from './hooks'
import { NodeRunningStatus } from './types'
import { getEdgeColor } from './utils'

const CustomEdge = ({
  id,
  data,
  source,
  sourceHandleId,
  target,
  targetHandleId,
  sourceX,
  sourceY,
  targetX,
  targetY,
  selected,
}: EdgeProps) => {
  const [
    edgePath,
    labelX,
    labelY,
  ] = getBezierPath({
    sourceX: sourceX - 8,
    sourceY,
    sourcePosition: Position.Right,
    targetX: targetX + 8,
    targetY,
    targetPosition: Position.Left,
    curvature: 0.16,
  })
  const [open, setOpen] = useState(false)
  const [isLabelHovering, setIsLabelHovering] = useState(false)
  const { handleNodeAdd } = useNodesInteractions()
  const { availablePrevBlocks } = useAvailableBlocks((data as Edge['data'])!.targetType, (data as Edge['data'])?.isInIteration || (data as Edge['data'])?.isInLoop)
  const { availableNextBlocks } = useAvailableBlocks((data as Edge['data'])!.sourceType, (data as Edge['data'])?.isInIteration || (data as Edge['data'])?.isInLoop)
  const {
    _sourceRunningStatus,
    _targetRunningStatus,
  } = data

  const linearGradientId = useMemo(() => {
    if (
      (
        _sourceRunningStatus === NodeRunningStatus.Succeeded
        || _sourceRunningStatus === NodeRunningStatus.Failed
        || _sourceRunningStatus === NodeRunningStatus.Exception
      ) && (
        _targetRunningStatus === NodeRunningStatus.Succeeded
        || _targetRunningStatus === NodeRunningStatus.Failed
        || _targetRunningStatus === NodeRunningStatus.Exception
        || _targetRunningStatus === NodeRunningStatus.Running
      )
    ) {
      return id
    }
  }, [_sourceRunningStatus, _targetRunningStatus, id])

  const handleOpenChange = useCallback((v: boolean) => {
    setOpen(v)
  }, [])

  const handleLabelMouseEnter = useCallback(() => {
    setIsLabelHovering(true)
  }, [])

  const handleLabelMouseLeave = useCallback(() => {
    setIsLabelHovering(false)
  }, [])

  const handleInsert = useCallback<OnSelectBlock>((nodeType, pluginDefaultValue) => {
    handleNodeAdd(
      {
        nodeType,
        pluginDefaultValue,
      },
      {
        prevNodeId: source,
        prevNodeSourceHandle: sourceHandleId || 'source',
        nextNodeId: target,
        nextNodeTargetHandle: targetHandleId || 'target',
      },
    )
  }, [handleNodeAdd, source, sourceHandleId, target, targetHandleId])

  const stroke = useMemo(() => {
    if (selected)
      return getEdgeColor(NodeRunningStatus.Running)

    if (linearGradientId)
      return `url(#${linearGradientId})`

    if (data?._connectedNodeIsHovering)
      return getEdgeColor(NodeRunningStatus.Running, sourceHandleId === ErrorHandleTypeEnum.failBranch)

    return getEdgeColor()
  }, [data._connectedNodeIsHovering, linearGradientId, selected, sourceHandleId])

  const isLabelVisible = open || !!data?._hovering || isLabelHovering
  const labelZIndex = data.isInIteration
    ? ITERATION_CHILDREN_Z_INDEX
    : data.isInLoop
      ? LOOP_CHILDREN_Z_INDEX
      : undefined

  return (
    <>
      {
        linearGradientId && (
          <CustomEdgeLinearGradientRender
            id={linearGradientId}
            startColor={getEdgeColor(_sourceRunningStatus)}
            stopColor={getEdgeColor(_targetRunningStatus)}
            position={{
              x1: sourceX,
              y1: sourceY,
              x2: targetX,
              y2: targetY,
            }}
          />
        )
      }
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke,
          strokeWidth: 2,
          opacity: data._dimmed ? 0.3 : (data._waitingRun ? 0.7 : 1),
          strokeDasharray: data._isTemp ? '8 8' : undefined,
        }}
      />
      <EdgeLabelRenderer>
        <div
          className={cn(
            'nopan nodrag flex h-8 w-8 items-center justify-center rounded-full transition-opacity duration-150',
            isLabelVisible ? 'visible opacity-100' : 'invisible opacity-0',
          )}
          onMouseEnter={handleLabelMouseEnter}
          onMouseLeave={handleLabelMouseLeave}
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: isLabelVisible ? 'all' : 'none',
            opacity: data._waitingRun ? 0.7 : 1,
            zIndex: labelZIndex,
          }}
        >
          <BlockSelector
            open={open}
            onOpenChange={handleOpenChange}
            asChild
            onSelect={handleInsert}
            availableBlocksTypes={intersection(availablePrevBlocks, availableNextBlocks)}
            triggerClassName={() => 'transition-colors duration-150'}
          />
        </div>
      </EdgeLabelRenderer>
    </>
  )
}

export default memo(CustomEdge)
